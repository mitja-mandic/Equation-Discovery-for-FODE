import numpy as np


def select_refinement_candidates(results: list[dict], error_margin: float, sorting_metric) -> list[dict]:
    """Select finite MSEs <= best MSE * (1 + margin), preserving input order.

    The margin is a nonnegative fraction (0.20 means 20%). A zero best MSE
    admits only exact zero-error fits; empty input returns an empty list.
    """
    if not np.isfinite(error_margin) or error_margin < 0:
        raise ValueError("error_margin must be finite and nonnegative")
    finite_results = [result for result in results if np.isfinite(result["mse"])]
    if not finite_results:
        return []
    cutoff = min(result[sorting_metric] for result in finite_results) * (1 + error_margin)
    return [result for result in finite_results if result[sorting_metric] <= cutoff]

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


def compute_relative_mse(measured, predicted):
    error = predicted - measured
    s_min = 0.1 * np.median(abs(measured))
    scale = np.maximum(abs(measured), s_min)
    return np.mean((error.real/scale) ** 2 + (error.imag/scale) ** 2)


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

def normalize_sigma(sigma, percentage_floor=0.1):
    floor = percentage_floor * np.nanmedian(sigma)
    return np.maximum(np.abs(sigma), floor)

def compute_ebic(
    n_frequencies: int,
    mse: float,
    num_params: int,
    num_candidate_models: int,
    gamma: float = 0.5,
) -> float:
    """Calculate EBIC, omitting model-independent likelihood constants.

    mse: mean(abs(predicted_impedance - measured_impedance)**2).
    num_params: number of fitted circuit parameters, excluding noise variance.
    num_candidate_models: number of distinct allowed circuit models having
        this same number of fitted parameters, before fit-quality filtering.
    """
    if n_frequencies <= 0:
        raise ValueError("n_frequencies must be positive")
    if not np.isfinite(mse) or mse <= 0:
        raise ValueError("mse must be finite and positive")
    if num_params < 0:
        raise ValueError("num_params must be nonnegative")
    if num_candidate_models < 1:
        raise ValueError("num_candidate_models must be at least 1")
    if not np.isfinite(gamma) or not 0 <= gamma <= 1:
        raise ValueError("gamma must be between 0 and 1")

    n = 2 * n_frequencies        # Real and imaginary scalar observations.
    variance_mle = mse / 2       # Your MSE sums both squared components.
    k = num_params + 1           # Include the estimated noise variance.

    return float(
        n * np.log(variance_mle)
        + k * np.log(n)
        + 2 * gamma * np.log(num_candidate_models)
    )
