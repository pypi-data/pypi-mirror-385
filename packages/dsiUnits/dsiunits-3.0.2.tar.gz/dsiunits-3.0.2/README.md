# D-SI Parser

This library converts D-SI unit strings to Latex.
And is able to perform math operations *, / and power with the D-SI units as well as checked weather teh can be converted into each other with scalar multiplication.


## Javascript version

The Javascript version of this library has moved to  <https://gitlab1.ptb.de/digitaldynamicmeasurement/dsiunits-js/>

## Installation

```bash
pip install dsiUnits
```

## Usage
The Constructor `DsiUnit(str)` will parse the string and create a DsiUnit object. [BIMP-SI-RP](https://si-digital-framework.org/SI/unitExpr?lang=en) strings are also supported and will be converted to D-SI units.
The DsiUnit object has the following methods:
- `to_latex()`: returns the Latex representation of the unit.
- `to_utf8()`: returns the UTF8 representation of the unit.
- `is_scalably_equal_to(other)`: checks whether the unit is equal to another unit with scalar multiplication.
- `to_sirp(pid=False)`: returns the SIRP representation of the unit. If pid is true the PID as URL is returned.
  
And following magic functions: 
- `__mul__(other)`: "*" multiplies the unit with another unit or a scalar
- `__truediv__(other)`: "/" divides the unit by another unit or a scalar
- `__pow__(other)`: "**" raises the unit to the power of another unit or a scalar
- `__eq__(other)`: "==" checks whether the unit is equal to another unit
- `__str__`: "str()" returns the string representation of the unit
- `__repr__`: returns the string representation of the unit

- `to_base_unit_tree()`: returns the base unit tree of the unit.
- `reduce_fraction()`: reduces the fraction of the unit by resolving all `\per` and combining same units by exponent addition.
- `sort_tree()`: sorts the base unit tree of the unit.

```python
from dsi_unit import DsiUnit

unit = DsiUnit(r'\metre\second\tothe{-1}')
latexStr = unit.to_latex()
print(latexStr)
```

```python
from dsi_unit import DsiUnit

mps = DsiUnit(r'\metre\second\tothe{-1}')
kmh = DsiUnit(r'\kilo\metre\per\hour')
scale_factor, base_unit = mps.is_scalably_equal_to(kmh)
print(
    f"The unit {mps} is equal to {kmh} with a factor of {scale_factor} and base unit {base_unit}"
)
```

For more usage examples see the [Example Notebook](https://gitlab1.ptb.de/digitaldynamicmeasurement/dsiUnits/-/blob/main/doc/examples.ipynb),
as well as the [pytest file](https://gitlab1.ptb.de/digitaldynamicmeasurement/dsiUnits/-/blob/main/src/dsiUnits.py).

## D-SI unit regex

This project also generates a RegEx that can be used to test whether a string conforms to the syntax of D-SI units. You can find the up-to-date text files here: <https://gitlab1.ptb.de/digitaldynamicmeasurement/dsiUnits/-/jobs/artifacts/main/browse?job=generate_regex>.

More details on the RegEx generator, including documentation of the different variants,
can be found in the `doc/` folder:
[English](docs/regex-generation-en.md),
[German](docs/regex-generation-de.md)