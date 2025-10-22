from tsme.time_simulation.simulator import AbstractTimeSimulator, AbstractDiscreteTimeSimulator
import numpy as np


class Lorenz(AbstractTimeSimulator):
    def __init__(self, ic=None, params=None):
        if params is None:
            params = [1.0, 1.0, 1.0]
        super().__init__(ic)
        self.sigma = params[0]
        self.rho = params[1]
        self.beta = params[2]

    def rhs(self, t, u_in):
        """
        Right-hand side function of the Lorenz system.

        Parameters
        ----------
        t : float
            current time value during simulation (here only included to interface with scipy's IVP solver
        u_in : numpy.array
            current state as array of shape (3,) for variables :math:`x`, :math:`y`, :math:`z`

        Notes
        -----
        The lorenz system consists of the following coupled ordinary differential equations:

        .. math::

            \\frac{\\text{d}x}{\\text{d}t} &= \\sigma \\left(y - x \\right) \\\\
            \\frac{\\text{d}y}{\\text{d}t} &= x \\left(\\rho - z \\right) - y \\\\
            \\frac{\\text{d}z}{\\text{d}t} &= x\\, y - \\beta \\, z

        The corresponding parameters are `self.sigma` (:math:`\\sigma`, default: 1.0), `self.rho`
        (:math:`\\rho`, default:1.0) and `self.beta` (:math:`\\beta`, default: 1.0). These are set during initialisation
         using a list in the keyword argument `params`.

        """
        x, y, z = u_in

        x_next = self.sigma * (y - x)
        y_next = x * (self.rho - z) - y
        z_next = x * y - self.beta * z

        return np.array([x_next, y_next, z_next])


class Burgers(AbstractTimeSimulator):
    def __init__(self, ic, dom, bc="periodic", diff="finite_difference"):
        super().__init__(ic, domain=dom, bc=bc, diff=diff)

    def rhs(self, t, u_in):
        """
        Burgers Equation in 1D.

        Parameters
        ----------
        t : float
            current time value during simulation (here only included to interface with scipy's IVP solver
        u_in : numpy.array
            current state as array of shape (1, N) for variable :math:`u(x)`, where N is the number of spatial
            discretization steps

        Notes
        -----
        The burgers equation in 1D reads here:

        .. math::

            \\frac{\\text{d}u}{\\text{d}t} = \\frac{\\text{d}^2u}{\\text{d}x} - u\\, \\frac{\\text{d}u}{\\text{d}x}

        """
        u = u_in[0]
        u_next = self.diff.d_dx(u, 2) - u * self.diff.d_dx(u, 1)

        return np.array([u_next])


class CahnHilliard(AbstractTimeSimulator):
    def __init__(self, ic, dom, params=None, bc="periodic", diff="finite_difference"):
        if params is None:
            params = [1.0, 1.0]
        super().__init__(ic, domain=dom, bc=bc, diff=diff)
        self.D = params[0]
        self.alpha = params[1]

    def rhs(self, t, u_in):
        """
        Cahn-Hilliard Equation

        Parameters
        ----------
        t : float
            current time value during simulation (here only included to interface with scipy's IVP solver
        u_in : numpy.array
            current state as array of shape (1, N, N) for variable :math:`u(x, y)`, where N is the number of spatial
            discretization steps

        Notes
        -----
        The Cahn-Hilliard equation reads here:

        .. math::

            \\frac{\\text{d}u}{\\text{d}t} = \\nabla^2 \\left(u^3 - \\alpha \\, u - D \\, \\nabla^2 u \\right)

        The corresponding parameters are `self.D` (:math:`D`, default: 1.0) and
        `self.alpha` (:math:`\\alpha`, default: 1.0). These are set during initialisation using a list in the keyword
        argument `params`.

        """
        u = u_in[0]
        # f = u ** 3 - self.alpha * u - self.D * (self.diff.d_dx(u, 2) + self.diff.d_dy(u, 2))
        # u_next = self.diff.d_dx(f, 2) + self.diff.d_dy(f, 2)
        u_next = - self.alpha*self.diff.d_dx(u, 2) - self.alpha*self.diff.d_dy(u, 2) \
                 + self.diff.d_dx(u ** 3, 2) + self.diff.d_dy(u ** 3, 2) \
                 - self.D * self.diff.d_dx(u, 4) - self.D * self.diff.d_dy(u, 4)\
                 - self.D * 2 * self.diff.dd_dxdy(u, [2, 2])

        return np.array([u_next])


class FitzHughNagumo(AbstractTimeSimulator):
    def __init__(self, ic, dom, params=None, bc="periodic", diff="finite_difference"):
        if params is None:
            params = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        super().__init__(ic, domain=dom, bc=bc, diff=diff)
        self.D_u = params[0]
        self.D_v = params[1]
        self.lamb = params[2]
        self.omega = params[3]
        self.kappa = params[4]
        self.tau = params[5]

    def rhs(self, t, u_in):
        """
        FitzHugh-Nagumo equation

        Parameters
        ----------
        t : float
            current time value during simulation (here only included to interface with scipy's IVP solver
        u_in : numpy.array
            current state as array of shape (2, N, N) for variables :math:`u(x, y)` and :math:`v(x, y)` where N is the
            number of spatial discretization steps

        Notes
        -----
        The FitzHugh-Nagumo equation reads here:

        .. math::

            f &= \\lambda \\, u - u^3 - \\kappa \\\\
            \\frac{\\text{d}u}{\\text{d}t} &= D_u^2 \\, \\nabla^2 u + f - \\omega \\, v \\\\
            \\tau \\, \\frac{\\text{d}v}{\\text{d}t} &= D_v^2 \\, \\nabla^2 v + u - v

        The corresponding parameters are: `self.D_u` (:math:`D_u`, default: 1.0), `self.D_v` (:math:`D_v`, default: 1.0)
        , `self.lamb` (:math:`\\lambda`, default: 1.0), `self.omega` (:math:`\\omega`, default: 1.0),
        `self.kappa` (:math:`\\kappa`, default: 1.0), `self.tau` (:math:`\\tau`, default: 1.0)

        """
        u = u_in[0]
        v = u_in[1]
        f = self.lamb * u - u ** 3 - self.kappa
        u_next = self.D_u ** 2 * (self.diff.d_dx(u, 2) + self.diff.d_dy(u, 2)) + f - self.omega * v
        v_next = self.D_v ** 2 * (self.diff.d_dx(v, 2) + self.diff.d_dy(v, 2)) + u - v

        return np.array([u_next, self.tau ** (-1) * v_next])


class KortewegDeVries(AbstractTimeSimulator):
    def __init__(self, ic, dom, bc="periodic", diff="finite_difference"):
        super().__init__(ic, domain=dom, bc=bc, diff=diff)

    def rhs(self, t, u_in):
        """
        Korteweg de Vries equation in 1D

        Parameters
        ----------
        t : float
            current time value during simulation (here only included to interface with scipy's IVP solver
        u_in : numpy.array
            current state as array of shape (1, N) for variable :math:`u(x)`, where N is the number of spatial
            discretization steps

        Notes
        -----
        The Kortweg de Vries equation reads here:

        .. math::

            \\frac{\\text{d}u}{\\text{d}t} = \\frac{\\text{d}^3u}{\\text{d}x^3} - 6 u\\, \\frac{\\text{d}u}{\\text{d}x}


        """
        u = u_in[0]
        u_next = - self.diff.d_dx(u, 3) - 6 * u * self.diff.d_dx(u, 1)

        return np.array([u_next])


class HenonMap(AbstractDiscreteTimeSimulator):
    def __init__(self, ic, params=None):
        if params is None:
            params = [0.1, 0.1, 0.01]
        super().__init__(ic)
        self.a = params[0]
        self.b = params[1]
        self.gamma = params[2]

    def map(self, u, i):
        """
        Henon map

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

        Notes
        -----
        Here the Henon map reads:

        .. math::

            x_{i+1} &= 1 - a\\, x_i^2 + y_i + \\gamma \\cdot \\text{noise} \\cdot x_i \\\\
            y_{i+1} &= b\\, x_i

        The parameters are given by the respective attributes `self.a` (:math:`a`, default: 0.1),
        `self.b` (:math:`b`, default: 0.1) and `self.gamma` (:math:`\\gamma`, default: 0.01)

        """
        x_i = u[i][0]
        y_i = u[i][1]

        x_i_1 = 1 - self.a * x_i ** 2 + y_i + self.gamma * np.random.normal() * x_i
        y_i_1 = self.b * x_i

        u[i + 1] = [x_i_1, y_i_1]

        return u