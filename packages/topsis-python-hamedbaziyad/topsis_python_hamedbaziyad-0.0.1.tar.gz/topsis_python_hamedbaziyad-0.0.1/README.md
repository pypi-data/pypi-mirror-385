# TOPSIS Python

> IMPORTANT: This implementation was originally developed by [Intelizer](https://github.com/hamedbaziyad/TOPSIS). I just modified it (using [Jules](https://jules.google.com/)) to be a pip-installable package.

This repository provides a Python implementation of the Technique for Order of Preference by Similarity to Ideal Solution (TOPSIS), a method for multiple-criteria decision analysis.

## Installation

You can install this package using pip:

```bash
pip install topsis-python-hamedbaziyad
```

## Usage

Here is a simple example of how to use the `topsis` package:

```python
import pandas as pd
from topsis import TOPSIS

# Create a sample decision matrix
data = {
    'Alternatives': ['A1', 'A2', 'A3', 'A4'],
    'C1': [10, 12, 15, 8],
    'C2': [8, 9, 11, 10],
    'C3': [7, 10, 8, 9]
}
decision_matrix = pd.DataFrame(data).set_index('Alternatives')

# Define the weights and attribute types
weights = [0.4, 0.3, 0.3]
attribute_types = ['max', 'max', 'min']

# Run the TOPSIS algorithm
topsis_result = TOPSIS(decision_matrix, weights, attribute_types)

# Display the results
print(topsis_result)
```
