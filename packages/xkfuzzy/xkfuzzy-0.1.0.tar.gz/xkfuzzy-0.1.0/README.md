# xkfuzzy

A simple Python library for fuzzy membership calculations.

## Installation

```bash
pip install -e .
```

## Usage

The library provides a single function `calculate_membership` that can compute fuzzy membership values using different membership functions.

### Basic Usage

```python
import xkfuzzy

# Triangular membership function
membership_value = xkfuzzy.calculate_membership(
    value=5, 
    membership_type="triangular", 
    a=0, b=5, c=10
)
print(membership_value)  # Output: 1.0
```

### Supported Membership Functions

#### 1. Triangular Membership
```python
# Parameters: a, b, c (where a < b < c)
membership = xkfuzzy.calculate_membership(
    value=3, 
    membership_type="triangular", 
    a=0, b=5, c=10
)
```

#### 2. Trapezoidal Membership
```python
# Parameters: a, b, c, d (where a < b < c < d)
membership = xkfuzzy.calculate_membership(
    value=3, 
    membership_type="trapezoidal", 
    a=0, b=2, c=8, d=10
)
```

#### 3. Gaussian Membership
```python
# Parameters: center, sigma
membership = xkfuzzy.calculate_membership(
    value=2, 
    membership_type="gaussian", 
    center=0, sigma=1
)
```

#### 4. Bell-shaped Membership
```python
# Parameters: a (width), b (slope), c (center)
membership = xkfuzzy.calculate_membership(
    value=1, 
    membership_type="bell", 
    a=1, b=2, c=0
)
```

### Working with Arrays

The function also supports numpy arrays:

```python
import numpy as np
import xkfuzzy

values = np.array([0, 2, 5, 8, 10])
memberships = xkfuzzy.calculate_membership(
    value=values, 
    membership_type="triangular", 
    a=0, b=5, c=10
)
print(memberships)  # Output: [0.0, 0.4, 1.0, 0.4, 0.0]
```

## Function Signature

```python
calculate_membership(value, membership_type="triangular", **params)
```

**Parameters:**
- `value`: Input value(s) for which to calculate membership (float or array-like)
- `membership_type`: Type of membership function ("triangular", "trapezoidal", "gaussian", "bell")
- `**params`: Parameters specific to the membership function type

**Returns:**
- Membership value(s) between 0 and 1

## Requirements

- Python 3.7+
- NumPy 1.19.0+

## License

MIT License
