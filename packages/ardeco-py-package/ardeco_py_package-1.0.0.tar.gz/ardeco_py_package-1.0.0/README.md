# Ardeco Py Package

*Ardeco Py Package* is a lightweight Python client for the *[ARDECO](https://territorial.ec.europa.eu/ardeco)* API (Annual Regional Database of the European Commission).

It allows easy access to regional socio-economic datasets through both GraphQL and REST endpoints, returning clean and ready-to-use pandas DataFrames.

---

## Installation

```bash
pip install ardeco-py-package
```

Or, to test the package before release:

```bash
pip install -i https://test.pypi.org/simple/ ardeco-py-package --extra-index-url https://pypi.org/simple
```

---

## Quick Example

```python
from ardeco_py_package import Ardeco

# Initialize the ARDECO client
ardeco = Ardeco()

# Get available variables
variables = ardeco.get_variable_list()
print(variables.head())

# Access variable dimensions (auto-formatted)
variable = ardeco.get_variable("SNPTN")
print(variable.dimensions)
# {'age': ['TOTAL', 'Y_LT15', 'Y_GE65'], 'sex': ['F', 'M'], 'unit': ['NR']}

# Fetch data for a specific variable
data = ardeco.get_data(
    "SNPTN",
    unit="NR",
    age="TOTAL",
    nuts_versions=2024,
    date=2021
)
print(data.head())
```

---

## Main Features

- Retrieve variable and dataset lists from the ARDECO API
- Filter datasets by multiple dimensions (unit, sex, age, etc.) and columns (territory_id, date, and level_id)
- Download structured CSV data as pandas.DataFrame
- Query TERCET classifications for territorial analysis

--- 

## Methods Overview

| Method                          | Description                                 |
| --------------------------------| ------------------------------------------- |
| `get_variable_list()`           | List all available variables                |
| `get_variable(var_code)`        | Get details of a specific variable          |
| `get_dataset_list(var_code)`    | Retrieve available datasets                 |
| `get_data(var_code, **filters)` | Fetch filtered data as DataFrame            |
| `get_tercet_list()`             | Retrieve TERCET territorial classifications |

---

## License

This project is licensed under the EUPL v1.2 license.
See the included LICENSE file for details.