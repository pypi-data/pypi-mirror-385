# TSME: Time Series Model Estimation

A project for estimating differential equations from time series data. Documentation available 
[here](https://nonlinear-physics.zivgitlabpages.uni-muenster.de/ag-kamps/tsme/).

## Overview
This package houses a number of tools an methods to estimate (partial) differential equations given time series data. 
The methodology is based off of [PySINDy](https://github.com/dynamicslab/pysindy), albeit with some noteable deviations 
and add-ons. With this package you can:

- perform time simulations for various dynamical systems (wrapping SciPy's [solve_ivp](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html)),
this includes:
    - ordinary differntial equations
    - partial differential equations (for spatial derivatives either finite-differences or FFT can be used) in 1D or 2D 
(3D experimental)
    - time-delayed (partial) differential equations (wrapping a slighty modified version of [ddeint](https://github.com/zulko/ddeint)) 
    - integro-differential equations (experimental)
- generate generic candidate functions
- define custom candidate functions
- use different methods to estimate best linear combination of candidate functions:
  - least-squares fit
  - sequential thresholding least-squares (STLSQ)
  - [Hyperopt](https://hyperopt.github.io/hyperopt/)'s TPE to optimize STLSQ and additional model parameters with 
  respect to the Bayesian Information Criterion (BIC) 
- give user-defined regularization and constraints

## Installation
The package can now be installed with 
```shell
pip install tsme
```

## Quickstart
For examples see either the 'notebooks' folder in this repository (or the corresponding documentation), more involved 
exampels can be found in this [demo repository](https://github.com/CDSC-CoSyML/tsme_examples).  

In a 2D case we assume some time series data are given in a numpy array of shape `(# variables, # time steps
, # first spatial dim, # second spatial dim)` along with an array of time stamps of shape `(# time steps, )`. If the (equidistant) spatial steps are not by one unit we provide an 
array defining lower and upper bounds, in this case of shape `(2, 2)` (1D: `(1, 2)` or `(2, `)). A bare bones example would
be:

```python 
from tsme.model_estimation import Model

estimated_model = Model(time_series_data, time_stamps, phys_domain=[[x_min, x_max], [y_min, y_max]])

estimated_model.init_library(ode_order=3, pde_order=2)

estimated_model.optimize_sigma()
```

The library of candidate terms can be viewed using `estimated_model.print_library()` and in this case would give for one
variable:

```text
|   Index | Term                          |   Value 0 |
|---------|-------------------------------|-----------|
|       0 | 1.0                           |         0 |
|       1 | u[0]                          |         0 |
|       2 | u[0]*u[0]                     |         0 |
|       3 | u[0]*u[0]*u[0]                |         0 |
|       4 | d_dx(u[0],1)                  |         0 |
|       5 | d_dy(u[0],1)                  |         0 |
|       6 | d_dx(u[0]*u[0],1)             |         0 |
|       7 | d_dy(u[0]*u[0],1)             |         0 |
|       8 | d_dx(u[0]*u[0]*u[0],1)        |         0 |
|       9 | d_dy(u[0]*u[0]*u[0],1)        |         0 |
|      10 | d_dx(u[0],2)                  |         0 |
|      11 | d_dy(u[0],2)                  |         0 |
|      12 | dd_dxdy(u[0],(1,1))           |         0 |
|      13 | d_dx(u[0]*u[0],2)             |         0 |
|      14 | d_dy(u[0]*u[0],2)             |         0 |
|      15 | dd_dxdy(u[0]*u[0],(1,1))      |         0 |
|      16 | d_dx(u[0]*u[0]*u[0],2)        |         0 |
|      17 | d_dy(u[0]*u[0]*u[0],2)        |         0 |
|      18 | dd_dxdy(u[0]*u[0]*u[0],(1,1)) |         0 |
```
The library should then after optimization (hopefully) hold non-zero entries. 
# Citation
If you use this code please cite
> Mai, O., Kroll, T. W., Thiele, U., & Kamps, O. (2025). Hyperparameter Optimization in the Estimation of PDE and Delay-PDE models from data. arXiv. https://doi.org/10.48550/ARXIV.2508.12715
