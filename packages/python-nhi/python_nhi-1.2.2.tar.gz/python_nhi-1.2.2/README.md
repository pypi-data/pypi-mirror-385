# NHI

[![Repository](https://img.shields.io/badge/jamesansley%2Fnhi-102335?logo=codeberg&labelColor=07121A)](https://codeberg.org/jamesansley/nhi)
[![License](https://img.shields.io/badge/Apache--2.0-002d00?label=license)](https://codeberg.org/jamesansley/nhi/src/branch/main/LICENSE)
[![PyPi](https://img.shields.io/pypi/v/python-nhi)](https://pypi.org/project/python-nhi/)

A function to check strings against the New Zealand Ministry of Health NHI
Validation Routine.
Supports the old and new NHI number formats specified in
[HISO 10046:2023](https://www.tewhatuora.govt.nz/publications/hiso-100462023-consumer-health-identity-standard/).

## Install

```
pip install python-nhi
```

For the other versions of this library, see:
- [nhi on JSR](https://jsr.io/@ansley/nhi)
- [nhi on Crates](https://crates.io/crates/nhi)
- [nhi with Pkl](https://codeberg.org/jamesansley/nhi/src/branch/main/pkl)

## Usage

```python
from nhi import is_nhi

print(is_nhi("WLD9413"))  # True
print(is_nhi("zsc21tn"))  # True
print(is_nhi("zzZ0044"))  # False
print(is_nhi("ZZZ00AA"))  # False
```

Checks are case-insensitive.

***Note:*** This does not check that the NHI number has been _assigned_ to
a person, it merely checks the NHI is consistent with the HISO 10046:2023
standard.

### Excluding Testcases

NHI numbers that begin with `Z` are reserved for testing.
If you wish to exclude these values, you will need to manually check for a `Z`
prefix:

```python
from nhi import is_nhi

value = "zvb97xq"

print(is_nhi(value))  # True
print(not value.upper().startswith("Z") and is_nhi(value))  # False
```

***Note:*** This check does not mean that the NHI number has been _assigned_ to
a person, it just means that the NHI value is not reserved for testing.

## See Also

- https://www.tewhatuora.govt.nz/publications/hiso-100462023-consumer-health-identity-standard/
- https://www.tewhatuora.govt.nz/our-health-system/digital-health/health-identity/national-health-index/information-for-health-it-vendors-and-developers
