import numpy as np
from scipy.integrate import solve_ivp
from .differentiation import DifferentialOperator, get_differential_operator
from .ddeint import ddeint


class AbstractTimeSimulator:
    """
    This abstract class provides basic time simulation functionality for ODEs and PDEs (1D or 2D) using Scipys initial
    value solver. It is intended to be extended with needed attributes and a right-hand-side function (rhs), It also
    provides methods for handling spatial differentiation and boundary conditions.
    """

    def __init__(self, ic, domain=None, bc=None, diff=None, **kwargs):
        """
        Basic constructor method. Provides spatial coordinates (if applicable) and records basic information of the
        problem. Also creates some protected attributes for differentiation methods.

        Parameters
        ----------
        ic : array-like
            array of initial conditions, should be in the shape (# Variables, ) for ODEs, (# Variables, # First
            spatial dimension) for 1D PDEs and (# Variables, # First spatial dimension, # Second spatial dimension) for
            2D PDEs
        domain : tuple
            physical domain of the problem, for ODE value is None (default), for PDE shape should be ((x_min, x_max), )
            in the 1D case and ((x_min, x_max), (y_min, y_max)) for 2D (3D case analogous)
        bc : string
            Set the boundary conditions in case of spatially extended system, otherwise 'None' (default). Options
            include "periodic" or "neumann"
        diff : string
            Set the differentiation method in case of spatially extended system, otherwise 'None' (default). Options
            include "finit_difference" or "pseudo_spectral"

        Attributes
        ----------
        To be extended
        """
        if diff == "pseudo_spectral" and bc != "periodic":
            bc = "periodic"
            print("Warning: Boundary condition forced to 'periodic' due to pseudo-spectral method!")

        assert diff is None or diff == "pseudo_spectral" or diff == "finite_difference", \
            "Unsupported differentiation method."

        self.n_variables = ic.shape[0]  # Number of variables of the problem
        self.domain = domain  # Passed domain as specified above
        self.initial_state = ic  # Passed initial conditions as stated above
        self._dimensions = None  # number of spatial dimension of the problem
        self._discret_x = None  # spatial discretization of the problem in first dimension (if applicable)
        self._discret_y = None  # spatial discretization of the problem in second dimension (if applicable)
        self.diff = None  # instance of DiffirentialOperator handling spatial differentiation
        self.solver = None  # to save the scipy solver object (maybe remove)
        self.sol = None  # to save time simulation
        self.sol_dot = None  # to save derivative of time simulation
        self.time = None  # time stamps of the simulation
        self.d_dt = None  # to save (finite difference) differential operator w.r.t. time

        # Check provided domain to see for different use-cases: ODE, 1D PDE, 2D PDE
        if self.domain is None:
            self._mode = "ODE"
        else:
            self._mode = "PDE"
            self._dimensions = len(domain)
            self._discret_x = self.initial_state.shape[1]

            # Check to see if discretization along the dimensions match and also if domain matches initial conditions
            if self._dimensions >= 2:
                try:
                    self.initial_state.shape[2]
                except IndexError:
                    raise ValueError("Dimension of domain and initial conditions do not match.")
                # assert self._discret == self.initial_state.shape[2], "Discretization needs to be the same in either " \
                #                                               "dimension."
                self._discret_y = self.initial_state.shape[2]

            if self._dimensions == 3:
                try:
                    self.initial_state.shape[3]
                except IndexError:
                    raise ValueError("Dimension of domain and initial conditions do not match.")
                # assert self._discret == self.initial_state.shape[2], "Discretization needs to be the same in either " \
                #                                               "dimension."
                self._discret_z = self.initial_state.shape[3]

        # All of the following enables use of spatial coordinates and derivatives in rhs function call
        if self._dimensions is None:
            pass
        elif self._dimensions == 1:
            self.Lx = self.domain[0][1] - self.domain[0][0]  # Absolute length of the spatial interval
            self.x = np.linspace(self.domain[0][0], self.domain[0][1], num=self._discret_x)  # spatial coordinates
            # create object handling spatial derivatives
            if "x" in kwargs:
                self.x = kwargs.get("x")
            self.diff = DifferentialOperator({"Lx": self.Lx, "x": self.x, "nx": self._discret_x},
                                             boundary=bc, method=diff)
        elif self._dimensions == 2:
            self.Lx = self.domain[0][1] - self.domain[0][0]  # Absolute length of the first spatial interval
            self.Ly = self.domain[1][1] - self.domain[1][0]  # Absolute length of the second spatial interval
            self.x = np.linspace(self.domain[0][0], self.domain[0][1], self._discret_x)  # spatial coordinates
            self.y = np.linspace(self.domain[1][0], self.domain[1][1], self._discret_y)
            if "x" in kwargs:
                self.x = kwargs.get("x")
            if "y" in kwargs:
                self.y = kwargs.get("y")
            self.x_mesh, self.y_mesh = np.meshgrid(self.x, self.y)
            # create object handling spatial derivatives
            # TODO: Remove discretization from function call
            self.diff = DifferentialOperator({"Lx": self.Lx, "x": self.x,
                                              "Ly": self.Ly, "y": self.y, "nx": self._discret_x, "ny": self._discret_y},
                                             boundary=bc, method=diff)
        elif self._dimensions == 3:
            self.Lx = self.domain[0][1] - self.domain[0][0]  # Absolute length of the first spatial interval
            self.Ly = self.domain[1][1] - self.domain[1][0]  # Absolute length of the second spatial interval
            self.Lz = self.domain[2][1] - self.domain[2][0]  # Absolute length of the third spatial interval
            self.x = np.linspace(self.domain[0][0], self.domain[0][1], self._discret_x)  # spatial coordinates
            self.y = np.linspace(self.domain[1][0], self.domain[1][1], self._discret_y)
            self.z = np.linspace(self.domain[1][0], self.domain[1][1], self._discret_z)

            if "x" in kwargs:
                self.x = kwargs.get("x")
            if "y" in kwargs:
                self.y = kwargs.get("y")
            if "z" in kwargs:
                self.z = kwargs.get("z")
            self.x_mesh, self.y_mesh = np.meshgrid(self.x, self.y)
            # create object handling spatial derivatives
            # TODO: Remove discretization from function call
            self.diff = DifferentialOperator({"Lx": self.Lx, "x": self.x,
                                              "Ly": self.Ly, "y": self.y,
                                              "Lz": self.Lz, "z": self.z,
                                              "nx": self._discret_x, "ny": self._discret_y, "nz": self._discret_z},
                                             boundary=bc, method=diff)
        else:
            raise NotImplementedError

    def rhs(self, t, u):
        """
        Abstract method for right-hand-side function of initial value problem. Per default available are:
        self.x (and self.y): spatial coordinates
        self.diff.d_dx(u, o): spatial derivative in first spatial component of order o
        self.diff.d_dy(u, o): spatial derivative in second spatial component of order o (if applicable)
        Other quantities should be computed in the constructor method when they are independent of u and t.

        Parameters
        ----------
        t : float
            current time during simulation
        u : array-like
            current (unflattened) variables during time simulation

        Returns
        -------
        u_next : array-like
            values of variables for the next time step
        """
        pass

    def _flat_rhs(self, t, uin):
        """
        Helper method that corrects input and output dimension between rhs function and scipys ivp solver
        Parameters
        ----------
        self
        t : float
            time argument to pass along to the function
        uin : array-like
            variable values to pass along to the function

        Returns
        -------
        flat_u_next : array-like
            a flattend version of the values for the variables in the next time step
            """
        if self._dimensions is None:
            u = uin
        elif self._dimensions == 1:
            u = np.reshape(uin, (self.n_variables, self._discret_x))
        elif self._dimensions == 2:
            u = np.reshape(uin, (self.n_variables, self._discret_x, self._discret_y))
        elif self._dimensions == 3:
            u = np.reshape(uin, (self.n_variables, self._discret_x, self._discret_y, self._discret_z))
        else:
            raise NotImplementedError

        result = self.rhs(t, u)

        return result.flatten()

    def simulate(self, time_interval, method="DOP853", t_eval=None):
        """
        Solve the initial value problem posed by the right-hand-side function and the initial condition (the latter
        being given during initialization).

        Parameters
        ----------
        time_interval : list
            Two-element list giving initial and final time
        method : string, default="DOP853"
            Passed to scipy's IVP solver to determine the integration method
        t_eval : array_like, default=None
            Also passed to scipy, samples the solution to give time stamps

        """
        # solve initial value problem
        self.solver = solve_ivp(self._flat_rhs, time_interval, self.initial_state.flatten(),
                                method=method, t_eval=t_eval)
        # save solution
        self.sol = [self.solver.y[:, i] for i in range(len(self.solver.y[0, :]))]
        # de-flatten output
        if self._dimensions is None:
            self.sol = np.array([np.reshape(item, (self.n_variables,)) for item in self.sol])
        elif self._dimensions == 1:
            self.sol = [np.reshape(item, (self.n_variables, self._discret_x)) for item in self.sol]
            self.sol = np.array(self.sol)
        elif self._dimensions == 2:
            self.sol = [np.reshape(item, (self.n_variables, self._discret_x, self._discret_y)) for item in self.sol]
            self.sol = np.array(self.sol)
        elif self._dimensions == 3:
            self.sol = [np.reshape(item, (self.n_variables, self._discret_x, self._discret_y, self._discret_z))
                        for item in self.sol]
            self.sol = np.array(self.sol)

        self.sol = np.array([self.sol[:, i] for i in range(self.sol.shape[1])])
        self.time = self.solver.t

        return self.sol

    def get_sol_dot(self, t=None, s=None):
        """
        Helper method that computes the time derivative for given time and solution. (This should approximate the value
        of the right-hand side numerically.)

        Parameters
        ----------
        t : array_like, default=None
            Array of time stamps (if None: use time stored in attributes)
        s : array_like, defautl=None
            Array of system states for every time step (if None: use solution from attributes)

        Returns
        -------
        numpy.array
            Numerical time derivative (finite-differences) of solution array

        """
        if t is None:
            time = self.time
        else:
            time = t
        if s is None:
            sol = self.sol
        else:
            sol = s

        assert time is not None, "Need to pass array of time stamps or perform a time simulation"
        assert sol is not None, "A solution array needs to be provided or a time simulation needs to be performed"

        self.d_dt = get_differential_operator(time, 1)
        self.sol_dot = self.d_dt(sol)[:, :-1]
        return self.sol_dot


class AbstractDiscreteTimeSimulator:
    """
    This abstract class provides basic time simulation functionality for discrete maps. It is intended to be extended
    with needed attributes and a map function.
    """
    def __init__(self, ic):
        """
        Basic constructor method

        Parameters
        ----------
        ic : array_like
            Initial condition of shape (# Variables, )
        """
        self.init = ic
        self.time = None
        self.sol = None

    def map(self, u, i):
        """
        Abstract mapping method, needs to be implemented.

        Parameters
        ----------
        u : numpy.array
            Array containing system states over time, i.e. of shape (# total time steps, # variables)
        i : integer
            current time step

        Returns
        -------
        numpy.array
            u with a set entry for i+1

        """
        pass

    def simulate(self, steps):
        """
        Evolve the map for `steps` number of time steps

        Parameters
        ----------
        steps : integer
            Number of time steps for which to apply the discrete map

        Returns
        -------
        numpy.array
            Array of shape (# total number of steps, # variables)

        """
        self.sol = np.zeros((steps+1, *self.init.shape))
        self.sol[0] = self.init

        for step in range(steps):
            self.sol = self.map(self.sol, step)

        self.sol = self.sol.T
        return self.sol


class AbstractTimeDelaySimulator(AbstractTimeSimulator):
    """
    This abstract class is based on the 'AbstractTimeSimulator' class and provides basic time simulation functionality
    for ODEs and PDEs with time delay using a slightly modified version of the Scipy-based DDE integration package
    'ddeint'. It is intended to be extended with needed attributes and a delay model (in self.model). As of now only
    one fixed delayed variable is provided to the model (may be changed in the future).
    """
    def __init__(self, delay, domain=None, bc=None, diff=None):
        """
        Basic constructor method. It should be noted that for construction a "values_before_zero" function needs to be
        implemented, which for t=0 should return the initial state with the correct dimension of the problem.

        Parameters
        ----------
        delay : float
            Time delay
        domain : array_like
            Physical domain of the problem, for ODE value is None (default), for PDE shape should be ((x_min, x_max), )
            in the 1D case and ((x_min, x_max), (y_min, y_max)) for 2D and analogous for the 3D case
        bc : string
            Set the boundary conditions in case of spatially extended system, otherwise 'None' (default). Options
            include "periodic" or "neumann"
        diff : string
            Set the differentiation method in case of spatially extended system, otherwise 'None' (default). Options
            include "finit_difference" or "pseudo_spectral"
        """
        ic = self.values_before_zero(0)
        super().__init__(ic, domain=domain, bc=bc, diff=diff)
        self.delay = delay

    def values_before_zero(self, t):
        """
        Function that needs to be implemented by the user. It should return values for the system state for t <= 0.
        Take special note that the shape of the output (#variable, # spatial_discretization) for PDEs or (#variables,)
        for ODEs should match the (user-implemented) model function.

        Parameters
        ----------
        t : float
            Time

        Returns
        -------
        numpy.ndarray
            System state at time t (<= 0)
        """
        pass

    def model(self, u, u_d, t):
        """
        Function that needs to be implemented by the user. Should return a new system sate with shape (#variable,
        #spatial_discretization) for PDEs or (#variables,) for ODEs

        Parameters
        ----------
        u : numpy.ndarray
            System state at current time t
        u_d : numpy.ndarray
            System state at time (t - self.delay)
        t : float
            Current time t

        Returns
        -------
        numpy.ndarray
            New system state
        """
        pass

    def _model_wrapper(self, Y, t, d):
        """
        Internal helper function that wraps the model function to pass it along to ddeint for simulation. Note that
        here we more or less define what is available to the model function, i.e. here we restrict the model to only one
        type of delay.

        Parameters
        ----------
        Y : ddeint.sate (not accurate)
            State as recorded by ddeint
        t : float
            Current time t
        d : float
            Delay for the model

        Returns
        -------
        numpy.ndarray
            New system state, but flattened
        """
        u = self.extract_Y(Y, t, 0)
        u_d = self.extract_Y(Y, t, d)

        du = self.model(u, u_d, t)

        return du.flatten()

    def _values_before_zero_wrapper(self, t):
        """
        Internal helper function that wraps the 'values_before_zero' function to accommodate different shapes, i.e.
        allow for PDEs

        Parameters
        ----------
        t : float
            Time t (<= 0)

        Returns
        -------
        numpy.ndarray
            System state at time t (<= 0), but flattened
        """
        return self.values_before_zero(t).flatten()

    def extract_Y(self, Y, t, d):
        """
        Helper function that takes a system state as it is recorded by ddeint, and returns the system state at time
        (t - d) in appropriate dimensions, i.e. unflattened.

        Parameters
        ----------
        Y : ddeint.sate (not accurate)
            System state as it is recorded by ddeint
        t : float
            Time
        d : float
            Delay

        Returns
        -------
        numpy.ndarray
            System state at time t (t - d) in appropriate dimensions, i.e. unflattened.
        """
        if self._dimensions is None:
            u = Y(t - d)
        elif self._dimensions == 1:
            u = np.reshape(Y(t - d), (self.n_variables, self._discret_x))
        elif self._dimensions == 2:
            u = np.reshape(Y(t - d), (self.n_variables, self._discret_x, self._discret_y))
        elif self._dimensions == 3:
            u = np.reshape(Y(t - d), (self.n_variables, self._discret_x, self._discret_y, self._discret_z))
        else:
            raise NotImplementedError
        return u

    def simulate_delay_model(self, t, d=None):
        """
        Use 'ddeint' to simulate the delay model in time.

        Parameters
        ----------
        t : array-like
            Time steps
        d : float, optional
            To overwrite the system delay (default: 'None').

        Returns
        -------
        numpy.ndarray
            Time series of the simulated system of shape (#variables, #time_steps, #spatial_discretization_1), where
            the number of discretization steps is either NA for ODEs or repeated per spatial dimension for PDEs.
        """
        if d is None:
            d = self.delay
        self.sol = ddeint(self._model_wrapper, self._values_before_zero_wrapper, t, fargs=(d,))
        # de-flatten output
        if self._dimensions is None:
            self.sol = np.array([np.reshape(item, (self.n_variables,)) for item in self.sol])
        elif self._dimensions == 1:
            self.sol = [np.reshape(item, (self.n_variables, self._discret_x)) for item in self.sol]
            self.sol = np.array(self.sol)
        elif self._dimensions == 2:
            self.sol = [np.reshape(item, (self.n_variables, self._discret_x, self._discret_y)) for item in self.sol]
            self.sol = np.array(self.sol)
        elif self._dimensions == 3:
            self.sol = [np.reshape(item, (self.n_variables, self._discret_x, self._discret_y, self._discret_z))
                        for item in self.sol]
            self.sol = np.array(self.sol)

        self.sol = np.array([self.sol[:, i] for i in range(self.sol.shape[1])])
        self.time = t

        return self.sol