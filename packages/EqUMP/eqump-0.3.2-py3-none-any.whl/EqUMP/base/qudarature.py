import numpy as np
import scipy.stats as stats
from numpy.polynomial.hermite import hermgauss
from typing import Tuple

def gauss_hermite_quadrature(nq: int = 30) -> Tuple[np.ndarray, np.ndarray]: 
    """
    Gaussian–Hermite quadrature nodes and weights scaled for the standard normal distribution.
    
    Parameters
    ----------
    nq: int, optional
        Number of quadrature nodes (default 30, as in R 'equateIRT').
    
    Returns
    ----------
    Tuple
        nodes: np.ndarray
            Quadrature nodes (scaled Hermite polynomial roots) corresponding to the standard normal distribution.
        weights: np.ndarray
            Quadrature weights associated with each node for integration with respect to the standard normal distribution.
    
    Examples
    ----------    
    (Todo)
    """
    # Standard Gauss-Herimte quadrature nodes and weight
    node, weight = hermgauss(nq)
    
    # Scaling to standard normal distribution
    theta_node = node * np.sqrt(2.0)
    theta_weight = weight / np.sqrt(np.pi)
    
    output = theta_node, theta_weight
    
    return output

def fixed_point_quadrature(
    nq: int = 40,
    theta_range: Tuple[float, float] = (-4.0, 4.0)) -> Tuple[np.ndarray, np.ndarray]: 
    """
    Fixed-point quadrature nodes and weights for the standard normal distribution.
    
    Parameters
    ----------
    nq: int, optional
        Number of quadrature nodes (default 40, as in R 'equateIRT')
    theta_range: Tuple of float, optional
        Lower and upper bounds of the latent trait (default -4 to 4, as in R 'equateIRT')
        
    Returns
    ----------
    Tuple
        nodes: np.ndarray
            Quadrature nodes dividing the theta range into nq equally spaced points.
        weights: np.ndarray
            Quadrature weights associated with each node, proportional to the standard normal distribution.
    
    Examples
    ----------    
    (Todo)        
    """
    theta_node = np.linspace(theta_range[0], theta_range[1], nq)
    prob_node = stats.norm.pdf(theta_node)
    theta_weight = prob_node/np.sum(prob_node)

    output = theta_node, theta_weight
    
    return output