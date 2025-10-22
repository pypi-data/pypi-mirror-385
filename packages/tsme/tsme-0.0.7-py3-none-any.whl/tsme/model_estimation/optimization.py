import hyperopt
import numpy as np
import scipy.integrate as integrate
from scipy.integrate import cumulative_trapezoid as cumtrapz

from hyperopt import fmin, hp, tpe
from tqdm import tqdm


# import optuna
# from optuna.samplers import TPESampler

# from gradient_free_optimizers import HillClimbingOptimizer
# import nevergrad as ng


def _assert_no_intersections(sets_list):
    """
    Assert that there are no intersections between all sets in the list.

    """
    # Flatten all the sets into one union to check if there's overlap
    all_elements = set()

    for s in sets_list:
        # Check if there's already any overlap with the current set
        assert all_elements.isdisjoint(s), f"Intersection found between {all_elements} and {s}"
        # Update all_elements with the current set
        all_elements.update(s)


# Maybe at some point add option for sklearns ridge regressor:
# from sklearn.linear_model import Ridge

# idea for alternative thresholding:
# do until included variables don't change or max_depth is reached:
#     Perform ordinary least square with all included variables
#     for all variables do:
#       remove variable and repeat the least squares
#       check BIC/integration error between the two least squares
#       if removing the variable made the error bigger than some threshold exclude the variable

def sequencing_threshold_ridge(lib, data, lamb, threshold=1e-4, max_it=10, norm=2, constraints=None,
                               scale_threshold=False, subset_threshold=None):
    """
    This reproduces the sequencing threshold ridge regression as it is implemented in PDE-FIND.

    Parameters
    ----------
    lib : np.array
        Time series of library terms as produced by a simulator instance via method create_library_time_series or of
        shape (# Variables, # Time Steps, # Library Terms, Dim1, Dim2(if applicable))
    data : np.array
        Time series to be fitted to (in shape (# Variable, # Time steps, Dim1, Dim2(if applicabe)))
    lamb : float
        Sparsity knob to promote sparsity in regularisation
    threshold : float or list-like
        (Optional, default: 1e-4) Threshold below which values are cut in sequence of regression
    max_it : int
        (Optional, default: 10) Maximum number of iterations in sequence of regressions
    norm : int
        (Optional, default: 2) Give the norm with which to normalize data
    constraints : list of function handles
        (Optional, default: None) A list of function handles for each variable that take the set of library terms and
        adds some sort of regulation
    scale_threshold : boolean
        (Optional, default: False) Whether to scale the threshold based on the L2-norm of the corresponding library
        function
    subset_threshold : list of dicts
        (Optional, default: None) List of dictionaries with a sub-sets of indices and a value for their threshold. Note
        That no overlap between the sub-sets is allowed. Any index not in a sub-set gets the threshold set by
        'threshold'.

    Returns
    -------
    np.array of weights for linear combination of library terms to best achieve data series

    """
    # Initialize weights and read the number of variables and the number of library terms
    w = []
    n_var = lib.shape[0]
    n_terms = lib.shape[1]

    if isinstance(threshold, float):
        tols = n_var * [threshold]
    elif isinstance(threshold, dict):
        try:
            tols = [threshold[key] for key in [f"t{n}" for n in range(n_var)]]
        except KeyError:
            raise KeyError("If thresholds are given as dictionary the keys need to be set as 't0', 't1' and so on.")
    else:
        tols = threshold

    assert len(tols) == n_var, "Thresholds need to be set for all variables. (Should be given as float for all" \
                               "or list-like.)"

    indices = set(np.arange(n_terms))
    sub_indices = []
    sub_thresholds = []
    if subset_threshold is not None:
        for subset in subset_threshold:
            sub_thresholds.append(subset["threshold"])
            sub_indices.append(set(subset["indices"]))
        _assert_no_intersections(sub_indices)
        for sub_index in sub_indices:
            indices = indices - sub_index

    # We try to find a set of weights for every variable's right hand side
    for var in range(n_var):
        # Read and reshape the library terms for the current variable, here we flatten all except the first dimension
        x = np.reshape(lib[var], (lib[var].shape[0], np.prod(lib[var].shape[1:])))
        # Flatten the corresponding data time series
        y = data[var].flatten()
        # When normalization is set, save the scaling factor and normalize the library according to the parameter norm
        l_norm = None
        tol_loc = tols[var]
        if scale_threshold:
            tol_scale = np.array([np.linalg.norm(item, 2) for item in x])
        else:
            tol_scale = np.ones(x.shape[0])

        if norm != 0:
            l_norm = 1.0 / (np.linalg.norm(x, norm))
            x = l_norm * x
            tol_loc = tol_loc / l_norm
        if lamb != 0 and constraints is None:
            # If a sparsity knob is given get the standard ridge estimate
            w_loc = np.linalg.lstsq(x.dot(x.T) + lamb * np.eye(n_terms), x.dot(y), rcond=None)[0]
        elif constraints is not None:
            w_loc = np.linalg.lstsq(x.dot(x.T) + lamb * np.eye(n_terms) +
                                    constraints[var](lib[var]), x.dot(y), rcond=None)[0]
        else:
            # else perform ordinary least squares fit
            w_loc = np.linalg.lstsq(x.T, y, rcond=None)[0]

        # Set the number of relevant terms to the number of all terms
        n_relevant = n_terms
        for i in range(max_it):
            # We find all the indices which hold values below our threshold and the remaining indices
            off_indices = np.where(np.abs(w_loc[list(indices)]) < tol_loc / tol_scale[list(indices)])[0]
            off_indices = set(np.array(list(indices))[off_indices])
            # TODO: make this such that sub_thresholds and indices can be set per variable
            # also I shouldn't have started with this set stuff
            off_sub_indices = set()
            for i in range(len(sub_indices)):
                off_sub = np.where(np.abs(w_loc)[list(sub_indices[i])] <
                                   sub_thresholds[i] / tol_scale[list(sub_indices[i])])[0]
                off_sub = set(np.array(list(sub_indices[i]))[off_sub])
                off_sub_indices.update(off_sub)
            all_off_indices = off_indices.union(off_sub_indices)
            new_on_indices = set(np.arange(n_terms)) - all_off_indices

            if n_relevant == len(new_on_indices):
                # Stop if the number of relevant terms does not change
                break
            else:
                # Update the number of relevant terms
                n_relevant = len(new_on_indices)

            on_indices = list(new_on_indices)

            if len(on_indices) == 0:
                # If all indices have been tossed stop (if this happened during the first iteration return the value)
                if i == 0:
                    # w.append(w_loc)
                    break
                else:
                    break

            # Cut off all values to the corresponding indices
            w_loc[list(all_off_indices)] = 0
            # Get new ridge or least square estimate
            if lamb != 0 and constraints is None:
                w_loc[on_indices] = np.linalg.lstsq(x[on_indices].dot(x[on_indices].T) +
                                                    lamb * np.eye(len(on_indices)), x[on_indices].dot(y), rcond=None)[0]
            elif constraints is not None:
                w_loc[on_indices] = np.linalg.lstsq(x[on_indices].dot(x[on_indices].T) +
                                                    lamb * np.eye(len(on_indices)) +
                                                    constraints[var](lib[var][on_indices]), x[on_indices].dot(y),
                                                    rcond=None)[0]
            else:
                w_loc[on_indices] = np.linalg.lstsq(x[on_indices].T, y, rcond=None)[0]

        # Normalize the weights
        if norm != 0:
            # w_loc[np.where(np.abs(w_loc) < tol_loc)[0]] = 0
            w.append(np.multiply(l_norm, w_loc))
        else:
            # w_loc[np.where(np.abs(w_loc) < tol_loc)[0]] = 0
            w.append(w_loc)

    return np.array(w)


def train_ridge(lib, data, lamb, thres, l0=None, split=0.7, seed=1234, max_it_train=10, max_it=10, norm=2):
    np.random.seed(seed)
    n_timesteps = lib.shape[2]
    x = np.reshape(lib, (lib.shape[0], lib.shape[1], np.prod(lib.shape[2:])))
    y = np.reshape(data, (data.shape[0], np.prod(data.shape[1:])))

    train_indices = np.random.choice(x.shape[-1], int(x.shape[-1] * split), replace=False)
    test_indices = np.delete(np.arange(x.shape[-1]), train_indices)

    x_train = x[:, :, train_indices]
    y_train = y[:, train_indices]

    x_test = x[:, :, test_indices]
    y_test = y[:, test_indices]

    d_tol = float(thres)
    tol = thres
    tol_best = tol

    if l0 is None:
        l0 = 0.001 * np.linalg.norm(np.linalg.cond(x), 2)

    def error(w_test):
        errors = [np.linalg.norm(y_test[i] - x_test[i].T.dot(w_test[i]), 2)
                  for i in range(x_test.shape[0])]
        error_test = np.sum(errors) + l0 * np.count_nonzero(w_test)
        return error_test

    w_best = np.array([np.linalg.lstsq(x_test[i].T, y_test[i], rcond=None)[0]
                       for i in range(x_test.shape[0])])
    error_best = error(w_best)

    pbar = tqdm(range(max_it_train))
    pbar.set_description(f"Training sequencing threshold ridge regression with "
                         f"{split * 100:.0f} % split")
    for i in pbar:
        w = sequencing_threshold_ridge(x_train, y_train, lamb, max_it=max_it, threshold=tol, norm=norm)
        err = error(w)

        if err <= error_best:
            error_best = err
            tol_best = tol
            w_best = w
            tol = tol + d_tol
        else:
            tol = max([0, tol - 2 * d_tol])
            d_tol = 2 * d_tol / (max_it_train - i)
            tol = tol + d_tol
        pbar.set_postfix({"Threshold": tol_best, "Error": error_best})

    return np.array(w_best), error_best


def train_ridge_wip(lib, data, data_dot, time, lamb, thres, l0=None, seed=1234, max_it_train=10, max_it=10, norm=2,
                    error="BIC"):
    np.random.seed(seed)
    n_timesteps = lib.shape[2]
    # reshaping is done inconsistently
    # x = np.reshape(lib, (lib.shape[0], lib.shape[1], np.prod(lib.shape[2:])))
    # y = np.reshape(data_dot, (data_dot.shape[0], np.prod(data_dot.shape[1:])))
    x = lib
    y = data_dot

    d_tol = thres
    tol = thres
    tol_best = tol

    if l0 is None:
        l0 = 0.001 * np.linalg.norm(np.linalg.cond(x.reshape((x.shape[0], x.shape[1], np.prod(x.shape[2:])))), 2)

    def error_der(w_test):
        errors = [np.linalg.norm(data_dot[i] - x[i].T.dot(w_test[i]).T) for i in range(x.shape[0])]
        error_test = np.sum(errors) + l0 * np.count_nonzero(w_test)
        return error_test

    def error_sp(w_test):
        errors = [np.linalg.norm(data[i, 1:] - cumtrapz(x[i].T.dot(w_test[i]), time).T)
                  for i in range(x.shape[0])]

        error_test = np.sum(errors) + l0 * np.count_nonzero(w_test)
        return error_test

    def error_bic(w_test):
        errors = np.array([np.linalg.norm(data[i, 1:] - cumtrapz(x[i].T.dot(w_test[i]), time).T)
                           for i in range(x.shape[0])])
        errors = errors.flatten() ** 2
        logL = -len(time) * np.log(errors.sum() / len(time)) / 2
        p = np.count_nonzero(w_test)
        bic = -2 * logL + p * np.log(len(time))
        return bic

    if error == "BIC":
        error_func = error_bic
    elif error == "integrate":
        error_func = error_sp
    elif error == "SINDy":
        error_func = error_der
    else:
        raise NotImplementedError("Unrecognized Error function")

    w_best = np.array([np.linalg.lstsq(x[i].reshape(x.shape[1], -1).T, y[i].flatten(), rcond=None)[0]
                       for i in range(x.shape[0])])
    error_best = error_func(w_best)

    pbar = tqdm(range(max_it_train))
    pbar.set_description(f"Training sequencing threshold ridge regression with " + error + "  error")
    for i in pbar:
        w = sequencing_threshold_ridge(x, y, lamb, max_it=max_it, threshold=tol, norm=norm)
        err = error_func(w)

        if err <= error_best:
            error_best = err
            tol_best = tol
            w_best = w
            tol = tol + d_tol
        else:
            tol = max([0, tol - 2 * d_tol])
            d_tol = 2 * d_tol / (max_it_train - i)
            tol = tol + d_tol
        pbar.set_postfix({"Threshold": tol_best, "Error": error_best})

    return np.array(w_best), error_best


def optimize_entire_model(lib, data, data_dot, time, max_evals=20, seed=42141, space=None, **kwargs):
    def training_loss_bic(weights):
        errors = []
        for var in range(lib.shape[0]):
            x_dot_recon = lib[var].T.dot(weights[var])
            x_recon = cumtrapz(x_dot_recon, time).T
            errors.append(np.linalg.norm(data[var, 1:] - x_recon))
        errors = np.array(errors)
        errors = errors.flatten() ** 2
        logL = -len(time) * np.log(errors.sum() / len(time)) / 2
        p = np.count_nonzero(weights)
        bic = -2 * logL + p * np.log(len(time))

        #  * (1/np.mean(np.linalg.norm(weights, axis=1)))
        return (1 + 1000 * (weights == 0.0).all(axis=1).sum()) * bic / len(time)


    def BIC(args):
        weights = [args[key] for key in weights_keys]
        weights = np.array([weights[i:i+lib.shape[1]] for i in range(lib.shape[0])])
        return training_loss_bic(weights)

    space_type = "uniform"
    space_bounds = [0.0, 1.0]
    if isinstance(space, str):
        space_type = space
        if space_type == "log":
            space_bounds = [-20, 0]
    elif isinstance(space, dict):
        space_type = space["type"]
        space_bounds = space["bounds"]

    if space_type == "uniform":
        s = lambda key: hp.uniform(key, space_bounds[0], space_bounds[1])
    elif space_type == "log":
        s = lambda key: hp.loguniform(key, space_bounds[0], space_bounds[1])

    weights_keys = [f"weight_{i}_{j}" for i in range(lib.shape[0]) for j in range(lib.shape[1])]
    s_dict = {key: s(key) for key in weights_keys}


    rstate = np.random.default_rng(seed)
    opt = fmin(BIC, space=s_dict, algo=tpe.suggest, max_evals=max_evals, rstate=rstate)
    model_weights = [opt[key] for key in weights_keys]
    model_weights = np.array([model_weights[i:i+lib.shape[1]] for i in range(lib.shape[0])])
    return opt, model_weights


def optimize_knob_and_threshold(lib, data, data_dot, time, max_evals=20, seed=420, **kwargs):
    def training_loss_bic(weights):
        errors = np.array([np.linalg.norm(data[i, 1:] - cumtrapz(lib[i].T.dot(weights[i]), time).T)
                           for i in range(lib.shape[0])])
        errors = errors.flatten() ** 2
        logL = -len(time) * np.log(errors.sum() / len(time)) / 2
        p = np.count_nonzero(weights)
        bic = -2 * logL  # + p * np.log(len(time))
        return (1 + 10 * (weights == 0.0).all(axis=1).sum()) * bic

    def BIC(args):
        lamb, thres = args
        weights = sequencing_threshold_ridge(lib, data_dot, lamb, threshold=thres, **kwargs)
        return training_loss_bic(weights)

    # s = hp.loguniform("l", -20, 0)
    # TODO: manage these with keyword arguments
    s = (hp.loguniform("l", -20, 0), hp.uniform("t", 0, 1.0))
    rstate = np.random.default_rng(seed)
    opt = fmin(BIC, space=s, algo=tpe.suggest, max_evals=max_evals, rstate=rstate)
    print(f"Optimal lambda found: {opt['l']}\n")
    print(f"Optimal threshold found: {opt['t']}")
    return sequencing_threshold_ridge(lib, data_dot, opt["l"], tol=opt["t"])


def optimize_threshold(lib, data, data_dot, time, max_evals=20, seed=420, space=None, condition=None,
                       loss=None, par_guess=0, subset_threshold=None, trials=None, **kwargs):
    if condition is not None and loss is not None:
        raise UserWarning("Both a loss condition and a custom loss function are set; condition is being ignored")

    if condition is None:
        condition = lambda x, x_dot: 0

    if subset_threshold is None:
        subset_threshold = []

    if trials is None:
        trials = hyperopt.Trials()

    def training_loss_bic(weights, lib, data, data_dot, time):
        errors = []
        conditions = []
        for var in range(lib.shape[0]):
            x_dot_recon = lib[var].T.dot(weights[var])
            x_recon = cumtrapz(x_dot_recon, time).T
            errors.append(np.linalg.norm(data[var, 1:] - x_recon))
            conditions.append(condition(x_recon, x_dot_recon))
        errors = np.array(errors)
        conditions = np.array(conditions)
        errors = errors.flatten() ** 2
        logL = -len(time) * np.log(errors.sum() / len(time)) / 2
        p = np.count_nonzero(weights)
        bic = -2 * logL + p * np.log(len(time)) + 200 * (par_guess != 0) * (p - par_guess) ** 2

        #  * (1/np.mean(np.linalg.norm(weights, axis=1)))
        return (1 + 1000 * (weights == 0.0).all(axis=1).sum()) * bic * np.exp(conditions.sum() / len(time))

    # TODO: clean this up (also it's this ugly for backward compatibility)
    space_type = "uniform"
    space_bounds = [0.0, 1.0]
    if isinstance(space, str):
        space_type = space
        if space_type == "log":
            space_bounds = [-20, 0]
    elif isinstance(space, dict):
        space_type = space["type"]
        space_bounds = space["bounds"]

    if space_type == "uniform":
        s = lambda key: hp.uniform(key, space_bounds[0], space_bounds[1])
    elif space_type == "log":
        s = lambda key: hp.loguniform(key, space_bounds[0], space_bounds[1])

    rstate = np.random.default_rng(seed)
    thr_keys = [f"t{i}" for i in range(data.shape[0])]
    sub_thr_keys = [f"st{i}" for i in range(len(subset_threshold))]
    s_dict = {key: s(key) for key in thr_keys + sub_thr_keys}

    if loss is None:
        def training_loss(weights):
            return training_loss_bic(weights, lib, data, data_dot, time)
    else:
        def training_loss(weights):
            return loss(weights, lib, data, data_dot, time)

    def BIC(args):
        thres = [args[key] for key in thr_keys]
        sub_thres = [args[key] for key in sub_thr_keys]
        if len(sub_thres) != 0:
            sub_dict = [{"threshold": sub_thres[i], "indices": subset_threshold[i]} for i in range(len(sub_thres))]
        else:
            sub_dict = None
        weights = sequencing_threshold_ridge(lib, data_dot, 0.0, threshold=thres,
                                             subset_threshold=sub_dict, **kwargs)
        return training_loss(weights)

    opt = fmin(BIC, space=s_dict, algo=tpe.suggest, max_evals=max_evals, rstate=rstate, trials=trials)
    thresholds = [opt[key] for key in thr_keys]
    print(f"Optimal threshold(s) found: { {key: opt[key] for key in thr_keys} }")
    if len(sub_thr_keys) > 0:
        sub_thresholds = [opt[key] for key in sub_thr_keys]
        print(f"Optimal sub-threshold(s) found: { {key: opt[key] for key in sub_thr_keys} }")
        sub_dict = [{"threshold": sub_thresholds[i], "indices": subset_threshold[i]} for i in
                    range(len(sub_thresholds))]
    else:
        sub_dict = None

    return trials, opt, sequencing_threshold_ridge(lib, data_dot, 0.0, threshold=thresholds, subset_threshold=sub_dict)


def optimize_threshold_with_delay(estimated_model, max_evals=20, seed=420, space=None, condition=None,
                                  loss=None, par_guess=0, trials=None, **kwargs):
    # TODO: merge with 'optimize_threshold'
    lib = estimated_model.lot
    data = estimated_model.sol[:, :-1]
    data_dot = estimated_model.sol_dot
    time = estimated_model.time[:-1]

    if condition is not None and loss is not None:
        raise UserWarning("Both a loss condition and a custom loss function are set; condition is being ignored")

    if condition is None:
        condition = lambda x, x_dot: 0

    if trials is None:
        trials = hyperopt.Trials()

    def training_loss_bic(weights, lib, data, data_dot, time):
        errors = []
        conditions = []
        for var in range(lib.shape[0]):
            x_dot_recon = lib[var].T.dot(weights[var])
            x_recon = cumtrapz(x_dot_recon, time).T
            errors.append(np.linalg.norm(data[var, 1:] - x_recon))
            conditions.append(condition(x_recon, x_dot_recon))
        errors = np.array(errors)
        conditions = np.array(conditions)
        errors = errors.flatten() ** 2
        logL = -len(time) * np.log(errors.sum() / len(time)) / 2
        p = np.count_nonzero(weights)
        bic = -2 * logL + p * np.log(len(time)) + 200 * (par_guess != 0) * (p - par_guess) ** 2
        # aic = -2 * logL + 2* p + 200 * (par_guess != 0) * (p - par_guess) ** 2
        return (1 + 1000 * (weights == 0.0).all(axis=1).sum()) * bic * np.exp(conditions.sum() / len(time))

    # TODO: clean this up (also it's this ugly for backward compatibility)
    space_type = "uniform"
    space_bounds = [0.0, 1.0]
    if isinstance(space, str):
        space_type = space
        if space_type == "log":
            space_bounds = [-20, 0]
    elif isinstance(space, dict):
        space_type = space["type"]
        space_bounds = space["bounds"]

    if space_type == "uniform":
        s = lambda key: hp.uniform(key, space_bounds[0], space_bounds[1])
    elif space_type == "log":
        s = lambda key: hp.loguniform(key, space_bounds[0], space_bounds[1])

    rstate = np.random.default_rng(seed)
    thr_keys = [f"t{i}" for i in range(data.shape[0])]
    s_dict = {key: s(key) for key in thr_keys}

    delay_type = "uniform"
    delay_bounds = [0.0, 2.0]
    if "delay" in space:
        delay_type = space["delay"]["type"]
        delay_bounds = space["delay"]["bounds"]

    if delay_type == "uniform":
        d = hp.uniform("delay", delay_bounds[0], delay_bounds[1])
    elif delay_type == "log":
        d = hp.loguniform("delay", delay_bounds[0], delay_bounds[1])
    elif delay_type == "randint":
        d = hp.randint("delay", delay_bounds[0], delay_bounds[1])

    s_dict["delay"] = d

    if loss is None:
        def training_loss(weights):
            return training_loss_bic(weights, lib, data, data_dot, time)
    else:
        def training_loss(weights):
            return loss(weights, lib, data, data_dot, time)

    def BIC(args):
        thres = [args[key] for key in thr_keys]
        delay = args["delay"]
        estimated_model.delay = delay
        estimated_model._recompile_delay_terms()
        weights = sequencing_threshold_ridge(lib, data_dot, 0.0, threshold=thres, **kwargs)
        return training_loss(weights)

    opt = fmin(BIC, space=s_dict, algo=tpe.suggest, max_evals=max_evals, rstate=rstate, trials=trials)
    thresholds = [opt[key] for key in thr_keys]
    print(f"Optimal threshold(s) found: { {key: opt[key] for key in thr_keys} }")
    print(f"Optimal delay found: {opt['delay']}")
    estimated_model.delay = opt["delay"]
    estimated_model._recompile_delay_terms()
    return trials, opt, sequencing_threshold_ridge(lib, data_dot, 0.0, threshold=thresholds)

# def optimize_threshold_optuna(lib, data, data_dot, time, max_evals=20, seed=420,
#                               space="uniform", boundaries=None,
#                               condition=None, loss=None, **kwargs):
#     if condition is not None and loss is not None:
#         raise UserWarning("Both a loss condition and a custom loss function are set; condition is being ignored")
#     if condition is None:
#         condition = lambda x, x_dot: 0
#     if boundaries is None:
#         boundaries = [1e-26, 1]
#
#     def training_loss_bic(weights, lib, data, data_dot, time):
#         errors = []
#         conditions = []
#         for var in range(lib.shape[0]):
#             x_dot_recon = lib[var].T.dot(weights[var])
#             x_recon = cumtrapz(x_dot_recon, time).T
#             errors.append(np.linalg.norm(data[var, 1:] - x_recon))
#             conditions.append(condition(x_recon, x_dot_recon))
#         errors = np.array(errors)
#         conditions = np.array(conditions)
#         errors = errors.flatten() ** 2
#         logL = -len(time) * np.log(errors.sum() / len(time)) / 2
#         p = np.count_nonzero(weights)
#         bic = -2 * logL + p * np.log(len(time))
#         return (1 + 1000 * (weights == 0.0).all(axis=1).sum()) * bic * np.exp(conditions.sum() / len(time))
#         # return bic * np.exp(conditions.sum() / len(time))
#
#     thr_keys = [f"t{i}" for i in range(data.shape[0])]
#
#     if space == "uniform":
#         log = False
#     else:
#         log = True
#
#     if loss is None:
#         def training_loss(weights):
#             return training_loss_bic(weights, lib, data, data_dot, time)
#     else:
#         def training_loss(weights):
#             return loss(weights, lib, data, data_dot, time)
#
#     def BIC(trial):
#         thres = [trial.suggest_float(key, boundaries[0], boundaries[1], log=log) for key in thr_keys]
#         # thres = [np.exp(trial.suggest_float(key, -30.0, 0.0, log=False)) for key in thr_keys]
#         weights = sequencing_threshold_ridge(lib, data_dot, 0.0, threshold=thres, **kwargs)
#         return training_loss(weights)
#
#     study = optuna.create_study(sampler=TPESampler(seed=seed))
#     study.optimize(BIC, n_trials=max_evals)
#     thresholds = study.best_params
#     print(f"Optimal threshold(s) found: {thresholds}")
#     return study, sequencing_threshold_ridge(lib, data_dot, 0.0, threshold=thresholds, **kwargs)

#
# def optimize_ridge_gfo(lib, data, split=0.7, seed=1234, trials=20, tol_range=[1e-4, 2], lamb_range=[0, 2]):
#     np.random.seed(seed)
#     # l0 = 0.001 * np.linalg.norm(np.linalg.cond(lib), 2)
#     x = np.reshape(lib, (lib.shape[0], lib.shape[1], np.prod(lib.shape[2:])))
#     y = np.reshape(data, (data.shape[0], np.prod(data.shape[1:])))
#
#     train_indices = np.random.choice(x.shape[-1], int(x.shape[-1] * split), replace=False)
#     test_indices = np.delete(np.arange(x.shape[-1]), train_indices)
#
#     x_train = x[:, :, train_indices]
#     y_train = y[:, train_indices]
#
#     x_test = x[:, :, test_indices]
#     y_test = y[:, test_indices]
#
#     l0 = 0.001 * np.linalg.norm(np.linalg.cond(x), 2)
#
#     def error(w_test):
#         errors = [np.linalg.norm(y_test[i] - x_test[i].T.dot(w_test[i]), 2)
#                   for i in range(x_test.shape[0])]
#         error_test = np.sum(errors) + l0 * np.count_nonzero(w_test)
#         return error_test
#
#     def objective(para):
#         tol = para["tol"]
#         # tol = 1.0
#         lamb = para["lamb"]
#         # lamb = 0.01
#         w = sequencing_threshold_ridge(x_train, y_train, lamb, tol=tol)
#         # errors = [np.linalg.norm(data[i].flatten() - lib[i].T.dot(w[i]).flatten(), 2)
#         #          for i in range(lib.shape[0])]
#         # error_test = np.sum(errors) + l0 * np.count_nonzero(w)# + 1 / np.sum([np.linalg.norm(wi, 2) for wi in w])
#         error_test = error(w)
#         return - error_test
#
#     search_space = {"tol": tol_range, "lamb": lamb_range}
#     opt = HillClimbingOptimizer(search_space)
#     opt.search(objective, n_iter=trials)
#
#     lam_best, tol_best = opt.best_value
#
#     return sequencing_threshold_ridge(lib, data, lam_best, tol=tol_best)


# def optimize_wip(model, w_init, trials=20, n_time=5):
#     time = model.simulator.time[:n_time]
#     Nt = len(time)
#
#     def error(w_test):
#         # errors = [np.linalg.norm(y_test[i] - x_test[i].T.dot(w_test[i]), 2)
#         #           for i in range(x_test.shape[0])]
#
#         model.simulator.sigma = w_test
#         y_estimate = model.simulator.simulate([time[0], time[-1]], t_eval=time)
#         try:
#             diff = ((model.sol - y_estimate).flatten()) ** 2
#         except ValueError:
#             diff = np.array([1e10])
#
#         logL = -Nt * np.log(diff.sum() / Nt) / 2
#
#         s = w_test.flatten()
#         s[np.abs(s != 0)] /= np.abs(s[s != 0])
#         p = np.abs(s).sum()
#
#         bic = -2 * logL + p * np.log(Nt)
#
#         return bic
#
#     instru = ng.p.Instrumentation(ng.p.Array(init=w_init))
#     optimizer = ng.optimizers.NGOpt(parametrization=instru, budget=trials)
#     recommendation = optimizer.minimize(error)
#
#     return recommendation.value[0][0]
