"""
Fuzzy membership calculation functions
"""

import numpy as np


def calculate_membership(value, membership_type="triangular", **params):
    """
    Calculate fuzzy membership value for a given input.
    
    Parameters:
    -----------
    value : float or array-like
        Input value(s) for which to calculate membership
    membership_type : str, optional
        Type of membership function. Options:
        - "triangular" (default)
        - "trapezoidal" 
        - "gaussian"
        - "bell"
    **params : dict
        Parameters specific to the membership function type
        
    Returns:
    --------
    float or array
        Membership value(s) between 0 and 1
        
    Examples:
    ---------
    >>> # Triangular membership
    >>> calculate_membership(5, "triangular", a=0, b=5, c=10)
    1.0
    
    >>> # Trapezoidal membership  
    >>> calculate_membership(3, "trapezoidal", a=0, b=2, c=8, d=10)
    0.5
    
    >>> # Gaussian membership
    >>> calculate_membership(2, "gaussian", center=0, sigma=1)
    0.1353352832366127
    """
    
    value = np.asarray(value)
    
    if membership_type == "triangular":
        return _triangular_membership(value, **params)
    elif membership_type == "trapezoidal":
        return _trapezoidal_membership(value, **params)
    elif membership_type == "gaussian":
        return _gaussian_membership(value, **params)
    elif membership_type == "bell":
        return _bell_membership(value, **params)
    else:
        raise ValueError(f"Unknown membership type: {membership_type}")


def _triangular_membership(value, a, b, c):
    """
    Triangular membership function.
    
    Parameters:
    -----------
    value : array-like
        Input values
    a, b, c : float
        Parameters defining the triangular shape (a < b < c)
    """
    result = np.zeros_like(value, dtype=float)
    
    # Left slope (a to b)
    mask1 = (value >= a) & (value <= b)
    result[mask1] = (value[mask1] - a) / (b - a)
    
    # Right slope (b to c)
    mask2 = (value >= b) & (value <= c)
    result[mask2] = (c - value[mask2]) / (c - b)
    
    return result


def _trapezoidal_membership(value, a, b, c, d):
    """
    Trapezoidal membership function.
    
    Parameters:
    -----------
    value : array-like
        Input values
    a, b, c, d : float
        Parameters defining the trapezoidal shape (a < b < c < d)
    """
    result = np.zeros_like(value, dtype=float)
    
    # Left slope (a to b)
    mask1 = (value >= a) & (value <= b)
    result[mask1] = (value[mask1] - a) / (b - a)
    
    # Flat top (b to c)
    mask2 = (value >= b) & (value <= c)
    result[mask2] = 1.0
    
    # Right slope (c to d)
    mask3 = (value >= c) & (value <= d)
    result[mask3] = (d - value[mask3]) / (d - c)
    
    return result


def _gaussian_membership(value, center, sigma):
    """
    Gaussian membership function.
    
    Parameters:
    -----------
    value : array-like
        Input values
    center : float
        Center of the Gaussian function
    sigma : float
        Standard deviation (width) of the Gaussian
    """
    return np.exp(-0.5 * ((value - center) / sigma) ** 2)


def _bell_membership(value, a, b, c):
    """
    Bell-shaped membership function.
    
    Parameters:
    -----------
    value : array-like
        Input values
    a : float
        Width parameter
    b : float
        Slope parameter
    c : float
        Center parameter
    """
    return 1 / (1 + np.abs((value - c) / a) ** (2 * b))
