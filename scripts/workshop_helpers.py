"""Small adapters for the workshop's pinned ppi_py version."""
import numpy as np
from ppi_py.ppi import _wls, _ols_get_stats
from ppi_py.ppi_power_analysis import _get_ppi_corr


def ppi_correlation(X, Y, Yhat, coord=1):
    """Return the package's parameter-specific PPI correlation.

    Args:
        X (numpy.ndarray): Regression design including the intercept.
        Y (numpy.ndarray): Human outcomes.
        Yhat (numpy.ndarray): Predictions for those same people.
        coord (int): Coefficient of interest; 1 is treatment in these notebooks.
    Returns:
        float: PPI correlation computed by ppi_py.
    Notes:
        Uses exactly the package's coefficient-correlation calculation, without
        calling its cost-based allocation optimizer. These internal functions
        are pinned by the notebook's package commit and checked against the
        public ppi_ols_power result. No costs are required.
    """
    X = np.asarray(X, dtype=float)
    beta = _wls(X, Y)
    grads, grads_hat, _, inv_hessian = _ols_get_stats(
        beta, X, Y, Yhat, X, Yhat, use_unlabeled=False)
    return _get_ppi_corr(grads, grads_hat, inv_hessian, coord=coord)



def effective_sample_size(rho, n, N):
    """Return the idealized PPI effective size for fixed labeled/unlabeled sizes.

    Args:
        rho (float): Parameter-specific PPI correlation.
        n (int): Number of labeled people.
        N (int): Number of unlabeled people.
    Returns:
        float: Approximate equivalent number of all-human observations.
    Notes:
        Broska et al. (2025), effective-sample-size formula. Assumes optimal
        linear weighting; this is not measured finite-sample efficiency.
        Negative rho needs a reversed prediction or a negative tuning weight.
    """
    if not np.isfinite(rho) or abs(rho) > 1 or n <= 0 or N < 0:
        raise ValueError('Need a finite correlation in [-1,1], n > 0 and N >= 0.')
    return n / (1 - rho**2 * N / (n + N))
