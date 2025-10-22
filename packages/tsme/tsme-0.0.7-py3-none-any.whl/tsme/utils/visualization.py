import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation, rc

rc("text", usetex=True)


def animate(sol, time=None,
            fig=None, ax=None, title="", savepath=None, fig_size=(6, 6), variable=0, go_by=1, **kwargs):
    """
    Method that animates the time evolution of the defined system. Optionally saves an mp4 video file to
    'savepath'.

    Parameters
    ----------
    sol : numpy.array
        Array of shape either (#Variables, #Timesteps, #Dim1) or (#Variables, #Timesteps, #Dim1, #Dim2)
    time : numpy.array
        (Optional, default=None) Array of time stamps, if None defaults to 0 + 1 per time step.
    title : string
        (Optional, default="") Give a title for the resulting animation
    savepath : string
        (Optional, default=None) Give a savepath for the animation
    fig_size : tuple
        (Optional, default=(6, 6)) Give a figure size for matplotlib
    variable : int
        (Optional, default=0) Gives the index of the variable to show (if there are more than one)
    go_by : int
        (Optional, default=1) Steps through the solution by `go_by` number of steps
    kwargs
        Additional key word arguments are passed to matplotlib.animation.FuncAnimation

    Returns
    -------
    matplotlib.animation.FuncAnimation

    """
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=fig_size)

    if time is None:
        time = range(sol.shape[1])

    dimension = len(sol.shape) - 2

    if dimension == 2:
        sol_img = ax.imshow(sol[variable, 0])
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        colorbar = plt.colorbar(sol_img)
    elif dimension == 1:
        sol_img, = ax.plot(sol[variable, 0])
        ax.set_ylim(np.min(sol[variable, :]), np.max(sol[variable, :]))
        ax.set_xlabel("x")
        ax.set_ylabel("u")
    else:
        raise NotImplementedError("Only 1D and 2D solutions can be animated.")

    # This feels stupid (trying to avoid "if" in animation call)+
    def anime2d(i):
        ax.set_title(title + f" Time: {time[i]:.3f}")
        data_max = np.max(sol[variable, i])
        data_min = np.min(sol[variable, i])

        sol_img.set_data(sol[variable, i])
        sol_img.set_clim(data_min, data_max)


        return sol_img

    def anime1d(i):
        ax.set_title(title + f" Time: {time[i]:.3f}")

        sol_img.set_ydata(sol[variable, i])
        return sol_img

    # This feels even more stupid
    if dimension == 2:
        anime = anime2d
    elif dimension == 1:
        anime = anime1d

    frames = np.arange(0, len(time), go_by)
    anima = animation.FuncAnimation(fig, anime, frames=frames, repeat=False, **kwargs)
    if savepath is not None:
        Writer = animation.writers["ffmpeg"]
        writer = Writer(fps=15, bitrate=1800)
        anima.save(savepath, writer=writer)
    # else:
    # plt.show()

    return anima


def barplot_parameters(sigma, sigma_ref=None, labels=None, width=0.35, table_fontsize=None, **kwargs):
    """
    Method that visualizes a set of parameters as a bar plot and may compare it to the true set of parameters

    Parameters
    ----------
    sigma : numpy.array
        Array of shape (# Varibales, # library terms), essentially `model_estimation.model.sigma`
    sigma_ref : numpy.array, default=None
        Array of same shape as sigma with reference values.
    labels : list of strings, default=None
        List of strings to label the x-axis with. If none indices are used
    width : float, default=0.35
        Width of bars in barplot
    table_fontsize : float, default=None
        Overwrites the automatic fontsize of the table which shows library labels
    kwargs
        Additional Keyword arguments are passed on to matplotlib.pyplot.subplot
    """
    plt.rcParams.update({"text.usetex": False})

    ind = np.arange(sigma.shape[1])
    labels_loc = range(sigma.shape[1])
    if labels is None:
        labels = labels_loc

    ratios = [2.5] + [1]
    # fig, ax = plt.subplots(nrows=sigma.shape[0], ncols=2, sharex=True, gridspec_kw={'width_ratios': ratios}, **kwargs)

    # only works for matplotlib >= 3.6.0:
    # fig, ax = plt.subplots(nrows=sigma.shape[0], ncols=2, sharex=True, width_ratios=ratios, **kwargs)

    fig = plt.figure(**kwargs)  # layout="constrained"
    spec = fig.add_gridspec(sigma.shape[0], 2, width_ratios=ratios)
    ax = []

    for i in range(sigma.shape[0]):
        axis = fig.add_subplot(spec[i, 0])
        rect = axis.bar(ind, sigma[i], width, color="tab:blue")
        leg = [(rect[0],), ("Estimated",)]
        axis.set_axisbelow(True)

        if sigma_ref is not None:
            rect_true = axis.bar(ind + width, sigma_ref[i], width, color="tab:purple")
            leg = [(rect[0], rect_true[0]), ("Estimated", "Reference")]

        axis.set_ylabel(f"Value for Variable {i}")
        axis.set_xticks(ind + (sigma_ref is not None) * (width / 2))
        axis.set_xticklabels(labels_loc)
        axis.legend(leg[0], leg[1])
        axis.grid()
        ax.append(axis)

    ax_table = fig.add_subplot(spec[:, 1])
    ax_table.axis("off")
    text = np.array([labels_loc, labels])
    table = ax_table.table(cellText=text.T, colLabels=("Index", "Label"), loc="center", colWidths=[0.25, 1])
    if table_fontsize is not None:
        table.auto_set_font_size(False)
        table.set_fontsize(table_fontsize)
    plt.tight_layout()

    plt.show()
    plt.rcParams.update({"text.usetex": True})
