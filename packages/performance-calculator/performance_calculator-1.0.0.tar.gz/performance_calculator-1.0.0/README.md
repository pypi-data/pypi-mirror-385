# PyOEE-Calc: A Python Library for Performance Factor Calculation

![GitHub last commit](https://img.shields.io/github/last-commit/sergio-oliveira-br/oee-calc-lib)
![License](https://img.shields.io/github/license/sergio-oliveira-br/oee-calc-lib?color=blue)
![Python Version](https://img.shields.io/badge/python-%3E%3D3.7-blue)

The name of this distributable package (as defined in `pyproject.toml`) is **`performance_calculator`**.

---

## 🎯 Academic Objective (LO3)

This project was developed with the main goal of demonstrating **Domain-Driven Design (DDD) Software Architecture**, **Modularization** (LO3), and **Object-Oriented Programming (OOP)**.

The `oee-calc-lib` repository houses the library that isolates the **Domain Logic** (OEE Performance calculation) from the **Application Logic** (e.g., the Django web interface and AWS integrations). This modular separation ensures the core calculation can be reused across any part of the system or in different future platforms.

---

## ⚙️ Installation (Development Use)

For the purpose of development and integration with the main project (e.g., your Django application), we recommend installing it in **editable mode (`-e`)**. This utilizes the modern Python packaging standard defined in `pyproject.toml`.

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/sergio-oliveira-br/oee-calc-lib](https://github.com/sergio-oliveira-br/oee-calc-lib)
    cd oee-calc-lib
    ```

2.  **Install into Your Main Virtual Environment (Editable Mode):**

    *Replace `/full/path/to/` with the actual location where you saved the library.*

    ```bash
    # Ensure you are in your main Django project's virtual environment
    (venv-django) $ pip install -e /full/path/to/oee-calc-lib
    ```
    *The `-e` (editable) flag ensures that any code change in the library's source directory (`src/oee_lib`) is immediately reflected in the main project.*

---

## 📖 How to Use

The library is class-oriented and requires you to instantiate the `OEECalculator` class.

### Usage Example (in your Django `views.py`):

```python
# 1. Import the External Library
# NOTE: The import path uses the source folder name 'oee_lib'.
from oee_lib.calculator import OEECalculator

# 1.1. Instantiate the class
oee_calculator = OEECalculator()

# 1.2. Input Data
# nominal_rate_ref: Ideal Rate
nominal_rate_ref = 600.0        # Units/Hour 

# actual_rate_from_user: Actual Rate
actual_rate_from_user = 580.0   # Units/Hour

# 2. Invoke the core calculation method
performance = oee_calculator.calculate_performance_rate(
    actual_rate=actual_rate_from_user, 
    nominal_rate=nominal_rate_ref
)

# 3. The result will be displayed in percentage.
print(f"Performance: {performance}")
# Expected result: 96.67%