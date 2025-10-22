import numpy as np
import sys
import re
from scipy.integrate import cumulative_trapezoid as cumtrapz
from scipy.interpolate import CubicHermiteSpline
from tqdm import tqdm
import math
from tsme.time_simulation import AbstractTimeDelaySimulator
from .optimization import train_ridge_wip, optimize_threshold, sequencing_threshold_ridge  #, optimize_threshold_optuna
from .optimization import optimize_threshold_with_delay
from itertools import combinations_with_replacement as combinations_wr
from itertools import permutations
from tabulate import tabulate


def _make_combination_string(order, n_variables):
    """
    This helper method gives a string containing all combinations of multiplying n_variables with one another and
    also the single elements.
    Example output for order=2 and n_variables=3:
    `np.array([np.ones(u[0].shape), u[0], u[1], u[2], u[0]*u[0], u[0]*x[1], u[0]*u[2], u[1]*u[1], u[1]*u[2], u[2]*u[2]])`

    Parameters
    ----------
    order : int
        Order up to which permutations should be included
    n_variables :
        Number of variables to combine

    Returns
    -------
    x_string : string
        String containing a 'one' element, the elements of an array u and products of all combinations of elements of u.

    """
    xstr = [f"u[{i}]" for i in range(n_variables)]
    x_string = "np.array([np.ones(u[0].shape)"
    for o in range(order + 1):
        comb = combinations_wr(xstr, o)
        for c in list(comb):
            if c == ():
                continue
            x_string += ", "
            for i, t in enumerate(c):
                if i == 0:
                    x_string += t
                else:
                    x_string += "*" + t
    x_string += "])"
    return x_string


def unique_permutations(tuple):
    uniqure_perms = set(permutations(tuple))
    return list(uniqure_perms)


def _label_to_latex(label):
    """
    Helper method that takes a term label of the default library and returns a string in latex syntax of said label.

    Parameters
    ----------
    label : string
        A term label as constructed by the default library generation (minus object calls)

    Returns
    -------
    new_string : string
        A new label in LateX syntax

    """

    def convert_product(term):
        assert term.startswith("u")
        assert "d_d" not in term and "dd_d" not in term
        factors = term.split("*")
        unique_factors = set(factors)
        exponents = [factors.count(factor) for factor in reversed(list(unique_factors))]
        output = ""
        for i, factor in enumerate(reversed(list(unique_factors))):
            index = re.findall(r"\[\s*\+?(-?\d+)\s*\]", factor)[0]  # could be done outside this loop
            exponent = exponents[i]
            u = "u"
            if "u_d" in factor:
                u = r"{u_{\tau}}"
            factor_proper = u + "_{" + f"{int(index)+1}" + "}^{" + f"{exponent}" + "}"
            output += r"\," + factor_proper
        return output[2:]

    def convert_single_partial_derivative(term):
        assert term.startswith("d_d")
        variable = term[3]

        product_in = term.find("(")
        product_out = term.find(",")
        product = convert_product(term[product_in + 1:product_out])
        order = term[product_out + 1:-1]
        output = r"\partial_" + variable + "^{" + f"{order}" + "}" + r"\left(" + product + r"\right)"

        return output

    def convert_double_partial_derivative(term):
        assert term.startswith("dd_")

        product_in = term.find("(")
        product_out = term.find(",")
        product = convert_product(term[product_in + 1:product_out])
        order = eval(term[product_out + 1:-1])

        output = r"\partial_x^{" + f"{order[0]}" + "}" + \
                 r"\partial_y^{" + f"{order[1]}" + "}" + \
                 r"\left(" + product + r"\right)"

        return output

    if label.startswith("1"):
        return "$" + label + "$"

    elif label.startswith("u") and not ("d_" in label):
        return "$" + convert_product(label) + "$"

    elif label.startswith("u") and "d_" in label:
        product = convert_product(label[:label.rfind("*")])
        # diff = label[label.rfind(".") + 1:]
        start_diff = re.search(r"d{1,2}_", label).start()
        diff = label[start_diff:]
        if diff.startswith("d_d"):
            diff = convert_single_partial_derivative(diff)
        elif diff.startswith("dd_d"):
            diff = convert_double_partial_derivative(diff)
        return "$" + product + r"\," + diff + "$"

    elif label.startswith("d_d"):
        return "$" + convert_single_partial_derivative(label) + "$"

    elif label.startswith("dd_"):
        return "$" + convert_double_partial_derivative(label) + "$"


class Model:
    def __init__(self, sol, time, phys_domain=None, bc="periodic", diff="finite_difference", delay=0.0):
        """
        This class is used to wrap the time simulation capabilities of the time_simulation submodule.
        It supplies a method to create a library of possible right-hand-side terms and creates an instance of a Time-
        simulator object used to perfom time simulations provided a vector `sigma` giving factors for linearly combining
        library terms for each variable. The overall geometry of the problem is extracted from the initial conditions
        provided during initialization.

        Parameters
        ----------
        sol : numpy.array
            Time series data
        time : numpy.array
            Array of points in time for each data point in time series data
        phys_domain : tuple
            (Optional, default=None) Physical domain size in shape e. g. ((Lx_min, Lx_max), (Ly_min, Ly_max))
            If None will set the domain size equal to the number of spatial discretization steps (if applicable)
        bc : string
            (optional, default="periodic") Sets boundary conditions (mainly for finite difference method). Options are
            "periodic" and "neumann"
        diff : string
            (optional, default="finite_difference") Sets differentiation method for spatial derivative. Options are
            "finite_difference" and "pseudo_spectral"
        """

        ic = sol[:, 0]
        self.initial_state = ic

        self.simulator = None
        self.optimizer = None
        self.trials = None
        self.sol = sol
        self.time = time
        self.delay = delay
        self.delay_indices = None

        self.n_variables = ic.shape[0]
        self.N = ic.shape[-1]
        self.dimension = len(ic[0].shape)
        # In case of ODE system
        if len(ic.shape) == 1:
            self.dimension = 0
            self.N = 0
        if phys_domain is None and self.dimension != 0:
            self.domain = [(0, self.N) for i in range(self.dimension)]
        else:
            # assert self.dimension is not 0, "Cannot specify physical domain for ODE system."
            self.domain = phys_domain
        self.boundary_condition = bc
        self.differentiation_method = diff

        self.ode_order = None  # Maximum number of factors in products of permutations
        self.indices_ode_to_pde = None  # Maximum order of spatial derivative
        self.pde_order = None  # Maximum order of factors in products for spatial derivatives
        self.ode_count = 0
        self.pde_count = 0
        self.custom_count = 0
        self.ode_string = None
        self.pde_string = None
        self.custom_string = None
        self._ode_comp_string = None
        self._pde_comp_string = None
        self._custom_comp_string = None
        self.sigma = None
        self.sigma_over_time = None
        self.lib_strings = None
        self.print_strings = None

        self.sol_dot = None
        self.cumulative_estimate = None
        self.lot = None

    def init_library(self, ode_order=2, pde_order=2, indices=None, custom_terms=np.array([]), kind="split"):
        """
        Method that initializes all library strings up to specified order. These string will be pre-compiled and later
        evaluated in the right hand side method. They include products of all provided variabled up to order ode_order
        and their spatial derivatives up to order pde_order. Indices is used to filter only selected library terms for
        spatial differentiation.

        Parameters
        ----------
        ode_order : int
            (Optional, default=2) Order up to which products of variables (including with themselves) are included in the library
        pde_order : int
            (Optional, default=2) Order up to which spatial derivatives are to be computed
        indices : np.array
            (optional, default=None) Array of indices of library elements to be included for spatial derivation (as a
            subset of terms created undeer ode_order)
        custom_terms : np.array
            (optional, default=np.array([])) User defined string to append to library and evaluate in RHS
        kind : str
            (optional, default="split") Whether to split derivatives into each spatial direction and their combinations
            (exhaustive) or "pair" them each (non-exhaustive).

        Notes
        -----
        Library creation should focus on the array-valued attribute "lib_string" and later evaluation should use that
        array for easier manipulation of library terms. Then one wouldn't need all this bogus differentiation between
        ode, pde or custom strings. Also using strings may generally be prohibitive.

        """
        if self.dimension == 0:
            pde_order = 0

        self.ode_order = ode_order  # Maximum number of factors in products of permutations
        self.pde_order = pde_order  # Maximum order of spatial derivative
        self.ode_count = self._give_count(self.ode_order)
        if indices is None:
            self.indices_ode_to_pde = np.arange(1, self.ode_count)
        else:
            self.indices_ode_to_pde = indices

        self.pde_count = ((kind == "pair") + (kind == "split") * self.dimension) \
                         * self.pde_order * len(self.indices_ode_to_pde)

        self.ode_string = _make_combination_string(self.ode_order, self.n_variables)
        self._ode_comp_string = compile(self.ode_string, '<string>', 'eval')

        ode_strings = self.ode_string.split(", ")
        ode_strings[-1] = ode_strings[-1][:-2]

        def make_split_pde_terms():
            x_string = "np.array(["
            for order in np.arange(1, pde_order + 1):
                for index in self.indices_ode_to_pde:
                    if self.dimension == 0:
                        x_string += "  "
                        break
                    # x_string += pre + f"self.diff.d_dx(ode_lib[{index}],{order})"
                    x_string += f"self.diff.d_dx({ode_strings[index]},{order}), "

                    def _make_double_derivatives(var_one, var_two):
                        combs = [c for c in combinations_wr(range(1, order + 1), 2) if sum(c) == order]
                        string = ""
                        for comb in combs:
                            string += f"self.diff.dd_d{var_one}d{var_two}({ode_strings[index]},({comb[0]},{comb[1]})), "
                            self.pde_count += 1
                            if comb[0] != comb[1]:
                                string += f"self.diff.dd_d{var_one}d{var_two}({ode_strings[index]},({comb[1]},{comb[0]})), "
                                self.pde_count += 1
                        return string

                    if self.dimension == 2:
                        # x_string += f", self.diff.d_dy(ode_lib[{index}],{order})"
                        x_string += f"self.diff.d_dy({ode_strings[index]},{order}), "
                        x_string += _make_double_derivatives("x", "y")
                        # combs = [c for c in combinations_wr(range(1, order + 1), 2) if sum(c) == order]
                        # for comb in combs:
                        #     x_string += f"self.diff.dd_dxdy({ode_strings[index]},({comb[0]},{comb[1]})), "
                        #     self.pde_count += 1
                        #     if comb[0] != comb[1]:
                        #         x_string += f"self.diff.dd_dxdy({ode_strings[index]},({comb[1]},{comb[0]})), "
                        #         self.pde_count += 1
                    if self.dimension == 3:
                        x_string += f"self.diff.d_dy({ode_strings[index]},{order}), "
                        x_string += f"self.diff.d_dz({ode_strings[index]},{order}), "
                        x_string += _make_double_derivatives("x", "y")
                        x_string += _make_double_derivatives("x", "z")
                        x_string += _make_double_derivatives("y", "z")
                        combs = [c for c in combinations_wr(range(1, order + 1), 3) if sum(c) == order]
                        unique_perms = [unique_permutations(comb) for comb in combs]
                        for perms in unique_perms:
                            for perm in perms:
                                x_string += f"self.diff.ddd_dxdydz({ode_strings[index]},({perm[0]},{perm[1]},{perm[2]})), "
                                self.pde_count += 1

            x_string = x_string[:-2] + (pde_order == 0) * "([" + "])"
            return x_string

        def make_coupled_pde_terms():
            x_string = "np.array(["
            for order in np.arange(1, pde_order + 1):
                for index in self.indices_ode_to_pde:
                    if self.dimension == 0:
                        x_string += "  "
                        break
                    x_string += f"self.diff.div({ode_strings[index]},{order}), "
            x_string = x_string[:-2] + (pde_order == 0) * "([" + "])"
            return x_string

        if kind == "split":
            x = make_split_pde_terms()
        else:
            x = make_coupled_pde_terms()
        self.pde_string = x
        self._pde_comp_string = compile(self.pde_string, '<string>', 'eval')
        self.sigma = np.zeros((self.n_variables, (self.ode_count + self.pde_count)))

        lib_strings = np.concatenate((self.ode_string[10:-2].split(", "), self.pde_string[10:-2].split(", ")))
        self.lib_strings = np.delete(lib_strings, np.argwhere(lib_strings == ''))
        # TODO: make this prettier (maybe refactor with "add_library_terms")
        # TODO: also this breaks for unevenly spaced data
        if self.pde_count == 0:
            if self.dimension == 0:
                x_string = f"np.array([]).reshape(0, )"
            elif self.dimension == 1:
                x_string = f"np.array([]).reshape(0, {self.N})"
            elif self.dimension == 2:
                x_string = f"np.array([]).reshape(0, {self.N}, {self.N})"
            elif self.dimension == 3:
                x_string = f"np.array([]).reshape(0, {self.N}, {self.N}, {self.N})"

            self.pde_string = x_string
            self._pde_comp_string = compile(self.pde_string, '<string>', 'eval')

        self.add_library_terms(custom_terms)

    def add_library_terms(self, list_of_strings):
        """
        Method that adds custom python expressions as strings and adds them to the library of RHS terms.

        Parameters
        ----------
        list_of_strings : numpy.array
            Array of strings to be added, can be empty.

        """
        assert self.lib_strings is not None
        self.custom_count = len(list_of_strings)
        self.lib_strings = np.concatenate((self.lib_strings, list_of_strings))

        if len(list_of_strings) == 0:
            if self.dimension == 0:
                x_string = f"np.array([]).reshape(0, )"
            elif self.dimension == 1:
                x_string = f"np.array([]).reshape(0, {self.N})"
            elif self.dimension == 2:
                x_string = f"np.array([]).reshape(0, {self.N}, {self.N})"
            elif self.dimension == 3:
                x_string = f"np.array([]).reshape(0, {self.N}, {self.N}, {self.N})"
        else:
            x_string = "np.array(["
            for string in list_of_strings:
                x_string += string + ", "

            x_string = x_string[:-2] + "])"

        self.custom_string = x_string
        self._custom_comp_string = compile(self.custom_string, '<string>', 'eval')
        self.sigma = np.zeros((self.n_variables, (self.ode_count + self.pde_count + self.custom_count)))

    def drop_library_terms(self, indices):
        """
        Drop terms of library at the indices specified in the argument. See 'print_library' for an output of library
        terms and their indices.

        Parameters
        ----------
        indices : list or array-like
            List of indices to be dropped from library

        Notes
        -----
        This is all way too cumbersome and should be redone (as described in the note of init_library)

        """

        assert self.lib_strings is not None
        n_drops = len(indices)
        indices = np.array(indices)
        n_ode_drops = np.sum(indices < self.ode_count)
        n_pde_drops = np.sum(np.logical_and(indices >= self.ode_count, indices < (self.ode_count + self.pde_count)))
        n_custom_drops = np.sum(np.logical_and(indices >= (self.ode_count + self.pde_count),
                                               indices < (self.ode_count + self.pde_count + self.custom_count)))
        self.ode_count -= n_ode_drops
        self.pde_count -= n_pde_drops
        self.custom_count -= n_custom_drops

        all_library_strings = self.ode_string.split(", ") + self.pde_string.split(", ") + self.custom_string.split(", ")
        mask = np.ones(len(all_library_strings), dtype=bool)
        mask[indices] = False
        # new_library_strings = np.delete(np.array(all_library_strings), indices)
        new_library_strings = np.array(all_library_strings)[mask].tolist()

        new_ode_strings = new_library_strings[0:self.ode_count]
        new_pde_strings = new_library_strings[self.ode_count:(self.ode_count + self.pde_count)]
        new_custom_strings = new_library_strings[(self.ode_count + self.pde_count):]

        flags = [False, False, False]
        if len(new_ode_strings) == 0:
            new_ode_strings = [" "]
            flags[0] = True
        if len(new_pde_strings) == 0:
            new_pde_strings = [" "]
            flags[1] = True

        if len(new_custom_strings) == 0:
            new_custom_strings = [" "]
            flags[2] = True

        # TODO: use startswith()
        if new_ode_strings[0][0:10] != "np.array([":
            new_ode_strings[0] = "np.array([" + new_ode_strings[0]
        if new_pde_strings[0][0:10] != "np.array([":
            new_pde_strings[0] = "np.array([" + new_pde_strings[0]
        if new_custom_strings[0][0:10] != "np.array([":
            new_custom_strings[0] = "np.array([" + new_custom_strings[0]

        if new_ode_strings[-1][-2:] != "])":
            new_ode_strings[-1] += "])"
            if flags[0]:
                new_ode_strings[-1] += f".reshape(0, {self.N}, {self.N})"
        if new_pde_strings[-1][-2:] != "])":
            new_pde_strings[-1] += "])"
            if flags[1]:
                new_pde_strings[-1] += f".reshape(0, {self.N}, {self.N})"

        if new_custom_strings[-1][-2:] != "])" and not (new_custom_strings[0].startswith("np.array([]).reshape(")):
            new_custom_strings[-1] += "])"
            if flags[2]:
                new_custom_strings[-1] += f".reshape(0, {self.N}, {self.N})"

        self.ode_string = ", ".join(new_ode_strings)
        self.pde_string = ", ".join(new_pde_strings)
        self.custom_string = ", ".join(new_custom_strings)
        self._ode_comp_string = compile(self.ode_string, '<string>', 'eval')
        self._pde_comp_string = compile(self.pde_string, '<string>', 'eval')
        self._custom_comp_string = compile(self.custom_string, '<string>', 'eval')
        self.sigma = np.zeros((self.n_variables, (self.ode_count + self.pde_count + self.custom_count)))
        self.lib_strings = np.delete(self.lib_strings, indices)
        if self.simulator is not None:
            print("User-Warning: Library is being modified after simulator is initiated. Simulator is being discarded.")
            self.simulator = None


    def _give_count(self, order):
        """
        (Internal) helper function that gives the number of ode-type terms that will automatically be created.

        Parameters
        ----------
        order : int
            Highest order up to which products will be created

        Returns
        -------
        int
            Number of ode-type terms that will be created automatically.

        """
        count = int(sum([math.factorial(self.n_variables + o - 1) / math.factorial(o) /
                         math.factorial(self.n_variables - 1) for o in range(order + 1)]))
        return count

    def init_simulator(self, sig=None, sol=None, time=None, attributes=None, **kwargs):
        """
        Method that initializes a TimeSimulator class and object. This object is a child of 'AbstractTimesimulator' of
        the time_simulation submodule. It is extended with a method that provides a time series of the library terms
        given a time series.

        Parameters
        ----------
        sig : numpy.array
            (Optional, default=None) Vector of factors for linearly combining library terms in right hand side. If none
            the attribute self.sigma is used instead (which is initialized as all zeros).
        sol : numpy.array
            (optional, default=None) Time series data to give to the time series simulator, if None self.sol is used.
        time : numpy.array
            (optional, default=None) Time stepping data corresponding to solution, if None self.time is used.
        attributes : dict
            (optional, default=None) Dictionary with additional attributes for time simulator. Used for parameters in
            custom library functions.
        """
        self.lot = None
        if sig is None:
            sigma = self.sigma
        else:
            sigma = sig
        if sol is None:
            sol = self.sol
        if time is None:
            time = self.time

        outer_self = self  # this would actually save quite a few lines, but I realized too late sooo yeah
        ode_string = self._ode_comp_string
        pde_string = self._pde_comp_string
        custom_string = self._custom_comp_string
        initial_state = self.initial_state
        domain = self.domain
        boundary_condition = self.boundary_condition
        differentiation_method = self.differentiation_method


        # TODO: global issue, this breaks for unevenly spaced data; also refactor to make prettier
        if self.dimension == 1:
            n_shape = (self.N,)
        elif self.dimension == 2:
            n_shape = (self.N, self.N)
        elif self.dimension == 3:
            n_shape = (self.N, self.N, self.N)

        class TimeSimulator(AbstractTimeDelaySimulator):
            def __init__(self, att=None):
                super().__init__(initial_state, domain=domain, bc=boundary_condition,
                                 diff=differentiation_method, **kwargs)
                self.sigma = sigma
                # self.library_over_time = None
                self.sol = sol
                self.time = time
                self.sol_dot = self.get_sol_dot()
                self.delay = outer_self.delay
                sol_delayed = np.array([self.get_solution_at_time(t - outer_self.delay) for t in self.time[:-1]])
                self.sol_delayed = np.swapaxes(sol_delayed, 0, 1)

                if att is not None:
                    for k, v in att.items():
                        setattr(self, k, v)

            # def rhs(self, t, u):
            #     ode_lib = eval(ode_string)
            #     pde_lib = eval(pde_string)
            #     custom_lib = eval(custom_string)
            #     vec = np.concatenate((ode_lib, pde_lib, custom_lib))
            #     u_next = [np.dot(s, [item.flatten() for item in vec]).reshape(n_shape) for s in self.sigma]
            #
            #     return np.array(u_next)
            def values_before_zero(self, t):
                return outer_self.initial_state

            def create_library_time_series(self, ts=None):
                if ts is None:
                    assert self.sol is not None, "Must provide time series or perform time simulation."
                    time_series = self.sol[:, :-1]
                else:
                    time_series = ts

                print("Generating library functions (this may take some time)...")

                # Feels inefficient (and it is)
                # TODO: subsample
                library_over_time = []
                for var in range(time_series.shape[0]):
                    var_lib_over_time = []
                    for t in range(time_series.shape[1]):
                        u = time_series[:, t]
                        u_d = self.sol_delayed[:, t]
                        ode_lib = eval(ode_string)
                        pde_lib = eval(pde_string)
                        custom_lib = eval(custom_string)
                        non_empty_arrays = [arr for arr in (ode_lib, pde_lib, custom_lib) if arr.size > 0]
                        if not non_empty_arrays:
                            raise ValueError("Library is empty.")
                        vec = np.concatenate(non_empty_arrays)
                        var_lib_over_time.append(vec)
                    library_over_time.append(np.swapaxes(np.array(var_lib_over_time), 0, 1))

                return np.array(library_over_time)

            def recompile_specific_library_time_series(self, indices):
                time_series = self.sol[:, :-1]
                time_series_delayed = np.array([self.get_solution_at_time(t - outer_self.delay) for t in self.time[:-1]])
                time_series_delayed = np.swapaxes(time_series_delayed, 0, 1)
                if len(indices) == 0:
                    raise ValueError("Must provide at least one index.")

                # print("Re-generating test functions (this may take some time)...")
                sub_string = "np.array([" + ", ".join(outer_self.lib_strings[indices]) + "])"
                sub_library_over_time = []
                for var in range(time_series.shape[0]):
                    var_sub_lib_over_time = []
                    for t in range(time_series.shape[1]):
                        u = time_series[:, t]
                        u_d = time_series_delayed[:, t]
                        sub_lib = eval(sub_string)
                        var_sub_lib_over_time.append(sub_lib)
                    sub_library_over_time.append(np.swapaxes(np.array(var_sub_lib_over_time), 0, 1))

                return np.array(sub_library_over_time)

            def get_solution_at_time(self, t):
                if self.sol_dot is None:
                    self.sol_dot = self.get_sol_dot()

                if t <= self.time[0]:
                    return self.initial_state

                equal_time_indices, = np.where(self.time == t)
                if equal_time_indices.size > 0:
                    first_equal_time_index = equal_time_indices[0]
                    return self.sol[:, first_equal_time_index]

                # find the indices of the two closest values to t in ts.
                inds = np.argsort(np.abs(self.time - t))[0:2]
                # sort the inds so that the corresponding ts are increasing.
                inds_inds = np.argsort(self.time[inds])
                inds = inds[inds_inds]
                # return the cubic hermit spline value at time t
                return CubicHermiteSpline(self.time[inds], self.sol[:, inds], self.sol_dot[:, inds], axis=1)(t)

        # TODO: Incorporate AbstractTimeDelaySimulator to allow for simulation

        # This is actually batshit crazy
        sim = TimeSimulator(att=attributes)
        if self.delay != 0.0:
            def model_pde(self, u, u_d, t):
                ode_lib = eval(ode_string)
                pde_lib = eval(pde_string)
                custom_lib = eval(custom_string)
                vec = np.concatenate((ode_lib, pde_lib, custom_lib))
                u_next = [np.dot(s, [item.flatten() for item in vec]).reshape(n_shape) for s in self.sigma]
                return np.array(u_next)

            def model_ode(self, u, u_d, t):
                ode_lib = eval(ode_string)
                pde_lib = eval(pde_string)
                custom_lib = eval(custom_string)
                vec = np.concatenate((ode_lib, pde_lib, custom_lib))
                u_next = [np.dot(s, [item for item in vec]) for s in self.sigma]
                return np.array(u_next)

            if self.dimension == 0:
                sim.model = model_ode.__get__(sim)
            else:
                sim.model = model_pde.__get__(sim)
        else:
            def rhs_pde(self, t, u):
                ode_lib = eval(ode_string)
                pde_lib = eval(pde_string)
                custom_lib = eval(custom_string)
                vec = np.concatenate((ode_lib, pde_lib, custom_lib))
                u_next = [np.dot(s, [item.flatten() for item in vec]).reshape(n_shape) for s in self.sigma]
                return np.array(u_next)

            def rhs_ode(self, t, u):
                ode_lib = eval(ode_string)
                pde_lib = eval(pde_string)
                custom_lib = eval(custom_string)
                vec = np.concatenate((ode_lib, pde_lib, custom_lib))
                u_next = [np.dot(s, [item for item in vec]) for s in self.sigma]
                return np.array(u_next)

            if self.dimension == 0:
                sim.rhs = rhs_ode.__get__(sim)
            else:
                sim.rhs = rhs_pde.__get__(sim)

        self.simulator = sim

        # Usually doesn't do anything
        self.simulator.sol = sol
        self.simulator.time = time

    def print_library(self, sigma=None, latex=False, reduced=False):
        """
        Print a readable table of library terms, their index and if available their linear factor.

        Parameters
        ----------
        latex : boolean
            (optinal, default=False) Whether or not to convert the names of the terms to latex syntax (only for default
            library).
        sigma : numpy.array
            (optional, default=None) If not None, replace values of linear combination factors with values stored in
            this array.
        reduced : boolean
            (optional, default=False) Whether or not to only print non-zero entries

        """
        indices = range(len(self.lib_strings))

        if self.sigma is None and sigma is None:
            print(tabulate(zip(indices, self.lib_strings), headers=["Index", "Term"]))
        else:
            if sigma is not None:
                sigma_loc = sigma
            else:
                sigma_loc = self.sigma
            headers = ["Index", "Term"]
            for i in range(sigma_loc.shape[0]):
                headers.append(f"Value {i}")  # should do this with list comprehension

            strings = [item.replace("self.", "").replace("diff.", "") for item in self.lib_strings]
            if strings[0] == "np.ones(u[0].shape)":
                strings[0] = "1.0"
            self.print_strings = strings
            format = "github"
            if latex:
                strings = list(map(_label_to_latex, strings))
                format = "latex_raw"

            if reduced:
                non_zero_indices = np.where(np.any(sigma_loc != 0, axis=0))[0]
                non_zero_strings = np.array(strings)[non_zero_indices]
                non_zero_sigma = np.array([item[non_zero_indices] for item in np.array(sigma_loc)])

                print(tabulate(zip(non_zero_indices, non_zero_strings, *non_zero_sigma),
                               headers=headers, tablefmt=format))
            else:
                print(tabulate(zip(indices, strings, *sigma_loc), headers=headers, tablefmt=format))

    def print_library_to_file(self, filename, sigma=None, latex=False, append_delay=False):
        """
        Print a readable table of library terms into a text file. The output is the same as 'print_library'

        Parameters
        ----------
        filename : str
            Name of the text file to print into.
        sigma : numpy.array
            (optional, default=None) If not None, replace values of linear combination factors with values stored in
            this array.
        """
        original_stdout = sys.stdout  # Save a reference to the original standard output
        with open(filename, 'w') as f:
            sys.stdout = f  # Change the standard output to the file we created.
            self.print_library(sigma=sigma, latex=latex)
            if append_delay:
                print(f"\nu_d is u at time t-d with d={self.delay}")
            sys.stdout = original_stdout  # Reset the standard output to its original value

    def optimize_sigma(self, lamb=0.1, thres=0.01, error="BIC",
                       simulate=False, backend="hyperopt", loss=None, with_delay=False, **kwargs):
        """
        Optimize sigma using variation of training for sequencing threshold ridge regression. See Module `opimization`
        for details.

        Parameters
        ----------
        lamb : float
            (Optional, default=0.1) Sparsity knob to promote sparsity in regularisation

        thres : float
            (Optional, default=0.01) Threshold below which values are cut in sequence of regression


        error : string
            (Optional, default="BIC") Keyword argument to pass to optimization routine. Choices are "BIC" for
            bayesian information criterion using integration, "SINDy" for the sum of squared differences in derivative
            and library reconstruction and "integrate" for sum of squared differences in original time series and
            integrated library reconstruction. (Both "SINDy" and "integrate" additionally punish non-sparsity,
            adjustable with the additional keyword argument `l0`.)
        simulate : bool
            (Optional, default=False) Whether to perform a time simulation after initial training has completed


        """
        self._check_library_status()

        # sol_dot_flat = sol_dot.reshape((sol_dot.shape[0], -1))
        # lot_flat = lot.reshape((lot.shape[0], lot.shape[1], -1))

        if backend == "train":
            sigma_opt, error = train_ridge_wip(self.lot, self.sol[:, :-1], self.sol_dot, self.time[:-1], lamb, thres,
                                               error=error,
                                               **kwargs)
        elif backend == "hyperopt":
            if not with_delay:
                trials, optimizer, sigma_opt = optimize_threshold(self.lot, self.sol[:, :-1], self.sol_dot, self.time[:-1],
                                                      loss=loss, trials=self.trials, **kwargs)
            elif with_delay:
                trials, optimizer, sigma_opt = optimize_threshold_with_delay(self, loss=loss, trials=self.trials, **kwargs)
        # elif backend == "optuna":  # this is stupid
        #     optimizer, sigma_opt = optimize_threshold_optuna(self.lot, self.sol[:, :-1], self.sol_dot, self.time[:-1],
        #                                                      loss=loss, **kwargs)

        if "optimizer" in locals():
            self.optimizer = optimizer
        if "trials" in locals():
            self.trials = trials

        self.sigma = sigma_opt
        self.simulator.sigma = self.sigma
        print("New Sigma set to: \n")
        self.print_library(reduced=True)

        if simulate:
            self.simulator.sigma = self.sigma
            if self.delay == 0.0:
                sol = self.simulator.simulate([self.time[0], self.time[-1]], t_eval=self.time)
            else:
                sol = self.simulator.simulate_delay_model(self.time)

            errors = np.array([np.linalg.norm(self.sol[i] - sol[i]) for i in range(self.n_variables)])
            errors = errors.flatten() ** 2
            logL = -len(self.time) * np.log(errors.sum() / len(self.time)) / 2
            p = np.count_nonzero(self.sigma)
            bic = -2 * logL + p * np.log(len(self.time))
            print(f"BIC error: {bic:.4f}")

    def least_square_sigma(self, lamb=None, norm=2):
        """
        Method that performs a least-square fit using numpy to fit the library to the derivative of the time series,
        without any regard for sparsity or further optimization (mainly for debugging purposes).

        Parameters
        ----------
        lamb : float or None
            (Optional, default=None) If provided adds the ridge-regression term for promoting sparsity, then `lamb` is
            the sparsity knob otherwise perform ordinary least-square fit
        norm : int
            (Optional, default=2) Linear algebra norm to be used to normalize for fitting (0: no norm, 1: L1-norm,
            2: L2-norm)

        """
        self._check_library_status()

        sol_dot_flat = self.sol_dot.reshape((self.sol_dot.shape[0], -1))
        lot_flat = self.lot.reshape((self.lot.shape[0], self.lot.shape[1], -1))

        l_norm = None
        if norm != 0:
            l_norm = 1.0 / (np.linalg.norm(sol_dot_flat, norm))
            sol_dot_flat = l_norm * sol_dot_flat

        if lamb is None:
            sigma = [np.linalg.lstsq(lot_flat[i].T, sol_dot_flat[i], rcond=None)[0] for i in range(self.n_variables)]
        else:
            sigma = [np.linalg.lstsq(lot_flat[i].dot(lot_flat[i].T) +
                                     lamb * np.eye(self.lot.shape[1]), lot_flat[i].dot(sol_dot_flat[i]), rcond=None)[0]
                     for i in range(self.n_variables)]

        if l_norm is not None:
            sigma = np.multiply(l_norm, sigma)

        self.sigma = np.array(sigma)
        self.simulator.sigma = self.sigma
        print("New Sigma set to: \n")
        self.print_library()

    def least_square_sigma_over_time(self, lamb=None, norm=2):
        """
        Method that performs a least-square fit using numpy to fit the library to the derivative of the time series at
        each time step, without any regard for sparsity or further optimization (mainly for debugging purposes).

        Parameters
        ----------
        lamb : float or None
            (Optional, default=None) If provided adds the ridge-regression term for promoting sparsity, then `lamb` is
            the sparsity knob otherwise perform ordinary least-square fit
        norm : int
            (Optional, default=2) Linear algebra norm to be used to normalize for fitting (0: no norm, 1: L1-norm,
            2: L2-norm)
        """
        self._check_library_status()

        sigma_over_time = []

        pbar = tqdm(range(len(self.time[:-1])))
        pbar.set_description("Least-square fit per time step" +
                             (lamb is not None) * f" with sparsity-knob {lamb or 0:.2f}")
        for i in pbar:
            sol_dot_i = self.sol_dot[:, i].reshape((self.sol_dot.shape[0], -1))
            lot_i = self.lot[:, :, i].reshape((self.lot.shape[0], self.lot.shape[1], -1))

            l_norm = None
            if norm != 0:
                l_norm = 1.0 / (np.linalg.norm(sol_dot_i, norm))
                sol_dot_i = l_norm * sol_dot_i

            if lamb is None:
                sigma_i = [np.linalg.lstsq(lot_i[j].T, sol_dot_i[j], rcond=None)[0] for j in range(self.n_variables)]
            else:
                sigma_i = [np.linalg.lstsq(lot_i[j].dot(lot_i[j].T) +
                                           lamb * np.eye(self.lot.shape[1]), lot_i[j].dot(sol_dot_i[j]), rcond=None)[0]
                           for j in range(self.n_variables)]

            if l_norm is not None:
                sigma_i = l_norm * np.array(sigma_i)
            sigma_over_time.append(sigma_i)
        self.sigma_over_time = np.swapaxes(np.array(sigma_over_time), 0, 1)

    def sequential_threshold_ridge(self, lamb=0.0, thres=1e-4, max_it=10, norm=2, **kwargs):
        """
        Method that wraps the sequential threshold ridge regression method from optimization module (only for the sake
        of convenience).

        Parameters
        ----------
        lamb : float, default=0.0
            Sparsity knob to promote sparsity in regularisation
        thres : float, default=1e-4
            Threshold below which values are cut in sequence of regressions
        max_it : int, default=10
            Maximum number of iterations in sequence of regressions
        norm : int, default=2
            Norm with which to normalize the data (passed to numpy.linalg.norm)

        """

        self._check_library_status()

        self.sigma = sequencing_threshold_ridge(self.lot, self.sol_dot, lamb, threshold=thres, max_it=max_it, norm=norm,
                                                **kwargs)
        self.simulator.sigma = self.sigma

        print("New Sigma set to: \n")
        self.print_library()

    def get_cumulative_estimate(self, sigma=None):
        """
        Method that uses scipy's cumtrapz method to compute an estimate of the original time series using the
        reconstructed derivative.
        """
        self._check_library_status()
        if sigma is None:
            s = self.sigma
        else:
            s = sigma
        cumulative_estimate = [cumtrapz(self.lot[i].T.dot(s[i]), self.time[:-1]).T
                               for i in range(self.n_variables)]
        self.cumulative_estimate = np.array(cumulative_estimate)
        return self.cumulative_estimate

    def _check_library_status(self):
        """
        Private helper method that checks if the library and time derivative have been computed and if not computes them
        """
        if self.simulator is None:
            self.init_simulator()
        if self.sol_dot is None:
            self.sol_dot = self.simulator.get_sol_dot()
        self.delay_indices = np.where(np.array(["u_d" in item for item in self.lib_strings]))[0]
        if self.lot is None:
            self.lot = self.simulator.create_library_time_series()

    def _recompile_specific_library_terms(self, indices):
        self._check_library_status()
        new_terms = self.simulator.recompile_specific_library_time_series(indices)
        for var in range(self.lot.shape[0]):
            self.lot[var, indices] = new_terms[var]

    def _recompile_delay_terms(self):
        self._recompile_specific_library_terms(self.delay_indices)
