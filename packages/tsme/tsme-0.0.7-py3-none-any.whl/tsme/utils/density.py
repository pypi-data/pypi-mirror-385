import numpy as np
from sklearn.neighbors import KernelDensity
import freud

from tqdm import tqdm

def density_from_2d_positions_freud(box, position_series, width=128, r_max=7.5, sigma=5.0):
    """
    Function that wraps the freud-analysis Guassian density estimator for a time series of 2d positional data

    Parameters
    ----------
    box : tuple
        Tuple (Lx, Ly) containing the length of x and y direction of the 2d slice (positions should fall in between
        these values)
    position_series : numpy.array-like
        Time series of positional values of individual particles. Shape should be (# time steps, # particles, 3), where
        one position is composed of x, y and z coordinates. This case assumes z=0 for all coordinates.
    width : integer, default=128
        Number of bins per side in 2d slice
    r_max : float, default=7.5
        Distance over which particles are blurred
    sigma : float, default=5.0
        Sigma parameter for Gaussian

    Returns
    -------
    numpy.array
        Time series of 2d slices of density approximation (shape: (# time steps, width, width))
    """
    box = freud.box.Box(Lx=box[0], Ly=box[1], Lz=0)

    ds = freud.density.GaussianDensity(width=width, r_max=r_max, sigma=sigma)

    snaps = []

    pbar = tqdm(range(len(position_series)))
    pbar.set_description("Gaussian density estimation using Freud")
    for i in pbar:
        positions = position_series[i]
        density_a = ds.compute((box, positions))

        snaps.append(density_a.density)
        # print(f"Time step: {i} of {len(position_series)}")

    snaps = np.array(snaps)

    return snaps


def density_from_2d_positions_sklearn(box, position_series, bandwidth=2.0, bins=None, kernel="epanechnikov"):
    """
    Method that uses sklearns kernel density estimator to approximate the density of  time series of 2d positinal data

    Parameters
    ----------
    box : tuple
        Tuple (Lx, Ly) containing the length of x and y direction of the 2d slice (positions should fall in between
        these values)
    position_series : numpy.array-like
        Time series of positional values of individual particles. Shape should be (# time steps, # particles, 3), where
        one position is composed of x, y and z coordinates. This case assumes z=0 for all coordinates.
    bandwidth : float, default=2.0
        Smoothing parameter that controls the bias-variance trade-off in kernel density estimation
    bins : tuple, default=None
        Tuple (Nx, Ny) with the number of bins in x and y direction. If `None` is set to 128 in each direction.
    kernel : string, default="epanechnikov"
        Sets which sklearn Kernel should be used. Options are: 'gaussian', 'tophat', 'epanechnikov', 'exponential',
        'linear', 'cosine'.


    Returns
    -------
    numpy.array
        Time series of 2d slices of density approximation (shape: (# time steps, bins[0], bins[1]))
    """
    if bins is None:
        x_bins = 128j
        y_bins = 128j
    else:
        x_bins = bins[0]*1j
        y_bins = bins[1]*1j

    box = np.array([[- box[0] / 2, box[0] / 2],
                    [-box[1] / 2, box[1] / 2]])

    def kde2D(x, y, bw, xbins=x_bins, ybins=y_bins, **kwargs):
        """Build 2D kernel density estimate (KDE). Credits to Geoff on stackoverflow
        (https://stackoverflow.com/questions/41577705/how-does-2d-kernel-density-estimation-in-python-sklearn-work)"""

        xx, yy = np.mgrid[box[0][0]:box[0][1]:xbins, box[1][0]:box[1][1]:ybins]

        xy_sample = np.vstack([yy.ravel(), xx.ravel()]).T
        xy_train = np.vstack([y, x]).T

        kde_skl = KernelDensity(bandwidth=bw, **kwargs)
        kde_skl.fit(xy_train)

        z = np.exp(kde_skl.score_samples(xy_sample))
        return xx, yy, np.reshape(z, xx.shape)

    snaps = []
    pbar = tqdm(range(len(position_series)))
    pbar.set_description("2D kernel density estimation using sklearn")
    for i in pbar:
        positions = position_series[i]
        _, _, zz = kde2D(positions[:, 0], positions[:, 1], bandwidth, kernel=kernel)
        snaps.append(zz)
        # print(f"Time step: {i} of {len(position_series)}")

    snaps = np.array(snaps)

    return snaps


def density_from_two_species_2d_positions_freud(box, position_series_A, position_series_B, width=128, r_max=7.5, sigma=5.0):
    """
    Function that wraps the freud-analysis Guassian density estimator for a time series of 2d positional data of two
    species and gives a combined density, where 1 is species A and -1 is species B.

    Parameters
    ----------
    box : tuple
        Tuple (Lx, Ly) containing the length of x and y direction of the 2d slice (positions should fall in between
        these values)
    position_series : numpy.array-like
        Time series of positional values of individual particles. Shape should be (# time steps, # particles, 3), where
        one position is composed of x, y and z coordinates. This case assumes z=0 for all coordinates.
    width : integer, default=128
        Number of bins per side in 2d slice
    r_max : float, default=7.5
        Distance over which particles are blurred
    sigma : float, default=5.0
        Sigma parameter for Gaussian

    Returns
    -------
    numpy.array
        Time series of 2d slices of density approximation (shape: (# time steps, width, width))
    """
    box = freud.box.Box(Lx=box[0], Ly=box[1], Lz=0)

    ds = freud.density.GaussianDensity(width=width, r_max=r_max, sigma=sigma)

    snaps_A = []
    snaps_B = []

    assert len(position_series_A) == len(position_series_B), "Position series need to be the same length"
    pbar = tqdm(range(len(position_series_A)))
    pbar.set_description("Gaussian density estimation using Freud")
    for i in pbar:
        positions_A = position_series_A[i]
        positions_B = position_series_B[i]

        density_a = ds.compute((box, positions_A))
        snaps_A.append(density_a.density)

        density_b = ds.compute((box, positions_B))
        snaps_B.append(density_b.density)

    snaps_A = np.array(snaps_A)
    snaps_B = np.array(snaps_B)

    snaps = snaps_A - snaps_B
    snaps = 2.0*(snaps - np.min(snaps)) / np.ptp(snaps) - 1

    return snaps
