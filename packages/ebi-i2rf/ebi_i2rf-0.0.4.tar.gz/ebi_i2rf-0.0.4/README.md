# I2RF Package for Data postprocessing

## How to install it:

```
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple ebi_i2rf
```

## How to use it

Import at in your document using 
```
import i2rf.wsr2 as pp
```

The following values can be obtained for TUT04 WSR2 by creating a pp object ``data = pp.i2rf()``

- ``data.getAll()`` returns five (5) numpy arrays for
    - mDot
    - All species concentrations for all mDot
    - All temperatures at for all mDot
    - All residence times for all mDot 
    - Species names as they are ordered in the respective numpy array

- ``data.getSpecies(specific:list=None)`` returns two numpy arrays for
    - mDot
    - Specific species concentrations (defined by list of strings)
        - If list is None (or has value None): returns all concentrations

- ``data.temperature()`` returns two numpy arrays for
    - mDot
    - Temperature for all mDot

- ``data.getResidenceTime()`` returns two numpy arrays for
    - mDot
    - Residence Time for all mDot



