import numpy as np

def compute_bic(n, mse, num_params):
    bic = n * np.log(mse) + num_params * np.log(n)
    return bic

def compute_aic(n, mse, num_params):
    aic = n * np.log(mse) + num_params * 2
    return aic

def compute_exact_bic(n, mle, num_params):
    bic_exact = -2 * mle + num_params * np.log(n)
    return bic_exact

def compute_log_likelihood(mse, n):
    return -0.5 * n * (np.log(2 * np.pi * mse) + 1)

def cumulative_absolute_error(measured,  predicted):
    errors = np.abs(measured - predicted)
    return np.sum(errors)

def compute_mse(measured, predicted):
    error = predicted - measured
    return np.mean(error.real**2 + error.imag**2)

def compute_weighted_mse(measured, predicted, weights_real, weights_imag):
    error = predicted - measured
    return np.mean((error.real/weights_real)**2 + (error.imag/weights_imag)**2)

def compute_weighted_lp(measured, predicted, weights_real, weights_imag, p=None):
    if not p:
        p = 1
    if p <= 0:
        raise ValueError("p must be greater than 0")

    error = predicted - measured

    return np.mean((np.abs(error.real) / weights_real) ** p + (np.abs(error.imag) / weights_imag) ** p)