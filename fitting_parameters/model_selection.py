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

def cumulative_absolute_error(y_true, y_pred):
    errors = np.abs(y_true - y_pred)
    # return np.cumsum(errors)[-1]# this is really stupid
    return np.sum(errors)

def compute_mse(measured, predicted):
    error = predicted - measured
    return np.mean(error.real**2 + error.imag**2)