import numpy as np
from findiff import FinDiff
from scipy.signal import convolve


def get_differential_operator(array, order):
    return FinDiff(order, array)


def _pad_array_by_diff(array, padding):
    diff = np.roll(array, -1) - array
    pad_left = array[..., 0, np.newaxis] - np.cumsum(diff[..., -padding - 1:-1], axis=0)
    pad_right = array[..., -1, np.newaxis] + np.cumsum(diff[..., :padding], axis=0)
    pad = np.hstack((pad_left, array, pad_right))
    return pad


class DifferentialOperator:
    """
    Class that handles numerical differentiation under certain boundary conditions.
    """

    def __init__(self, space_dict, boundary="periodic", method="pseudo_spectral"):
        # TODO: remove discretization from input and read from x or y instead
        nx = space_dict["nx"]  # get number of spatial points in first dimension
        self.p = 5  # set size of padding for finite difference method

        if "y" in space_dict.keys() and "z" in space_dict.keys():
            self.dimensions = 3
            if "ny" in space_dict.keys():
                ny = space_dict["ny"]
            else:
                ny = nx
            if "nz" in space_dict.keys():
                nz = space_dict["nz"]
            else:
                nz = nx

            self.x = np.array(space_dict["x"])
            self.y = np.array(space_dict["y"])
            self.z = np.array(space_dict["z"])

            if method == "finite_difference":
                # for boundary conditions in finite differences
                x_pad = _pad_array_by_diff(self.x, self.p)
                y_pad = _pad_array_by_diff(self.y, self.p)
                z_pad = _pad_array_by_diff(self.z, self.p)

                # x_pad = np.linspace(self.x[0] - self.p * (self.x[1] - self.x[0]),
                #                     self.x[-1] + self.p * (self.x[1] - self.x[0]),
                #                     num=nx + 2 * self.p)
                #
                # y_pad = np.linspace(self.y[0] - self.p * (self.y[1] - self.y[0]),
                #                     self.y[-1] + self.p * (self.y[1] - self.y[0]),
                #                     num=ny + 2 * self.p)

                # this is to accommodate for one, two and tree dimension in the differentiation method and feels
                # discouraged
                def unpad(u):
                    return u[self.p:-self.p, self.p:-self.p, self.p:-self.p]

                self.d_dx = lambda u, o: self.finite_difference(u, 0, x_pad, order=o, boundary=boundary, unpad=unpad)
                self.d_dy = lambda u, o: self.finite_difference(u, 1, y_pad, order=o, boundary=boundary, unpad=unpad)
                self.d_dz = lambda u, o: self.finite_difference(u, 2, z_pad, order=o, boundary=boundary, unpad=unpad)
                self.dd_dxdy = lambda u, o: self.finite_difference(u, [0, 1], [x_pad, y_pad], order=o,
                                                                   boundary=boundary, unpad=unpad)
                self.dd_dxdz = lambda u, o: self.finite_difference(u, [0, 2], [x_pad, z_pad], order=o,
                                                                   boundary=boundary, unpad=unpad)
                self.dd_dydz = lambda u, o: self.finite_difference(u, [1, 2], [y_pad, z_pad], order=o,
                                                                   boundary=boundary, unpad=unpad)
                self.ddd_dxdydz = lambda u, o: self.finite_difference(u, [0, 1, 2], [x_pad, y_pad, z_pad], order=o,
                                                                      boundary=boundary, unpad=unpad)

            elif method == "pseudo_spectral":

                # for pseudo-spectral method
                kx, ky, kz = np.meshgrid(np.fft.fftfreq(nx, space_dict["Lx"] / (nx * 2 * np.pi)),
                                         np.fft.fftfreq(ny, space_dict["Ly"] / (ny * 2 * np.pi)),
                                         np.fft.fftfreq(nz, space_dict["Lz"] / (ny * 2 * np.pi)))
                # somehow I feel like I could've used fftn for all dimensions
                self.d_dx = lambda u, o: self.pseudo_spectral(u, kx, order=o, fft=np.fft.fftn, ifft=np.fft.ifftn)
                self.d_dy = lambda u, o: self.pseudo_spectral(u, ky, order=o, fft=np.fft.fftn, ifft=np.fft.ifftn)
                self.d_dz = lambda u, o: self.pseudo_spectral(u, kz, order=o, fft=np.fft.fftn, ifft=np.fft.ifftn)
                self.dd_dxdy = lambda u, o: self.d_dx(self.d_dy(u, o[1]), o[0])
                self.dd_dxdz = lambda u, o: self.d_dx(self.d_dz(u, o[1]), o[0])
                self.dd_dydz = lambda u, o: self.d_dy(self.d_dz(u, o[1]), o[0])
                self.dd_dxdydz = lambda u, o: self.d_dx(self.d_dy(self.d_dz(u, o[2]), o[1]), o[0])

            self.div = lambda u, o: self.d_dx(u, o) + self.d_dy(u, o) + self.d_dz(u, o)
            self.convolve = lambda k, u: (
                        convolve(k, u, mode="same", method="fft") * (self.x[1] - self.x[0]) * (self.y[1] - self.y[0])
                        * (self.z[1] - self.z[0]))  # methods = "fft" or "direct"

        elif "y" in space_dict.keys() and "z" not in space_dict.keys():
            self.dimensions = 2
            if "ny" in space_dict.keys():
                ny = space_dict["ny"]
            else:
                ny = nx

            self.x = np.array(space_dict["x"])
            self.y = np.array(space_dict["y"])

            if method == "finite_difference":
                # for boundary conditions in finite differences
                x_pad = _pad_array_by_diff(self.x, self.p)
                y_pad = _pad_array_by_diff(self.y, self.p)

                # x_pad = np.linspace(self.x[0] - self.p * (self.x[1] - self.x[0]),
                #                     self.x[-1] + self.p * (self.x[1] - self.x[0]),
                #                     num=nx + 2 * self.p)
                #
                # y_pad = np.linspace(self.y[0] - self.p * (self.y[1] - self.y[0]),
                #                     self.y[-1] + self.p * (self.y[1] - self.y[0]),
                #                     num=ny + 2 * self.p)

                # this is to accommodate for one and two dimension in the differentiation method and feels discouraged
                def unpad(u):
                    return u[self.p:-self.p, self.p:-self.p]

                self.d_dx = lambda u, o: self.finite_difference(u, 0, x_pad, order=o, boundary=boundary, unpad=unpad)
                self.d_dy = lambda u, o: self.finite_difference(u, 1, y_pad, order=o, boundary=boundary, unpad=unpad)
                self.dd_dxdy = lambda u, o: self.finite_difference(u, [0, 1], [x_pad, y_pad], order=o,
                                                                   boundary=boundary, unpad=unpad)

            elif method == "pseudo_spectral":

                # for pseudo-spectral method
                kx, ky = np.meshgrid(np.fft.fftfreq(nx, space_dict["Lx"] / (nx * 2 * np.pi)),
                                     np.fft.fftfreq(ny, space_dict["Ly"] / (ny * 2 * np.pi)))

                self.d_dx = lambda u, o: self.pseudo_spectral(u, kx, order=o, fft=np.fft.fft2, ifft=np.fft.ifft2)
                self.d_dy = lambda u, o: self.pseudo_spectral(u, ky, order=o, fft=np.fft.fft2, ifft=np.fft.ifft2)
                self.dd_dxdy = lambda u, o: self.d_dx(self.d_dy(u, o[1]), o[0])

            self.div = lambda u, o: self.d_dx(u, o) + self.d_dy(u, o)
            self.convolve = lambda k, u: (
                    convolve(k, u, mode="same", method="fft") * (self.x[1] - self.x[0]) * (self.y[1] - self.y[0]))
                    # methods: "fft" or "direct"
        else:
            self.dimensions = 1
            self.x = np.array(space_dict["x"])

            if method == "finite_difference":
                # for boundary conditions in finite differences
                x_pad = _pad_array_by_diff(self.x, self.p)

                # x_pad = np.linspace(self.x[0] - self.p * (self.x[1] - self.x[0]),
                #                     self.x[-1] + self.p * (self.x[1] - self.x[0]),
                #                     num=nx + 2 * self.p)

                def unpad(u):
                    return u[self.p:-self.p]

                self.d_dx = lambda u, o: self.finite_difference(u, 0, x_pad, order=o, boundary=boundary, unpad=unpad)
                self.d_dy = None
                self.dd_dxdy = None

            elif method == "pseudo_spectral":
                kx = np.fft.fftfreq(nx, space_dict["Lx"] / (nx * 2 * np.pi))
                self.d_dx = lambda u, o: self.pseudo_spectral(u, kx, order=o, fft=np.fft.fft, ifft=np.fft.ifft)
                self.d_dy = None
                self.dd_dxdy = None
            self.div = self.d_dx
            # alternative methods for convolve: "fft" or "direct"
            self.convolve = lambda k, u: (convolve(k, u, mode="same", method="fft") * (self.x[1] - self.x[0]))

    def finite_difference(self, u, var, pad, order=1, boundary="periodic", unpad=None):
        if boundary == "periodic":
            bound = "wrap"
        elif boundary == "neumann":
            bound = "edge"
        else:
            raise NotImplementedError("Boundary condition not implemented.")

        u_padded = np.pad(u, [(self.p, self.p) for i in range(len(u.shape))], bound)
        if isinstance(var, list) or isinstance(var, np.ndarray):
            n_multi_derivative = len(var)
            try:
                tuples = [(var[i], pad[i], order[i]) for i in range(n_multi_derivative)]
            except TypeError:
                raise TypeError("Multivariate derivative requires lists or arrays of same length for all (numeric) "
                                "inputs")

            dn_dxn = FinDiff(*tuples, acc=6)
            # try:
            #     dn_dxn = FinDiff((var[0], pad[0], order[0]), (var[1], pad[1], order[1]))
            # except TypeError:
            #     raise TypeError("Multivariate derivative requires lists or arrays for all (numeric) inputs")
        elif isinstance(var, int):
            dn_dxn = FinDiff(var, pad, order, acc=6)
        else:
            raise TypeError("Can only differentiate for int index or list-like indices.")

        gradient = dn_dxn(u_padded)
        return unpad(gradient)

    def pseudo_spectral(self, u, k, order=1, fft=np.fft.fft2, ifft=np.fft.ifft2):
        return ifft((1j * k) ** order * fft(u))
