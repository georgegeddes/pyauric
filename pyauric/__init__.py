"""Pyauric Documentation

Pyauric is an interface for the AURIC airglow modelling software. The AURICManager class keeps track of environment variables and the working directory to facilitate AURIC use in python scripts, jupyter notebooks, interactive ipython sessions, etc.

If AURIC is set up so that you can use the standard command line interface, pyauric should work as well.

Example
-------
import pyauric
auric = payuric.AURICManager()

...
"""

from .manager import AURICManager

_param_format = r"""Mandatory parameters:
        NALT =        100 : number of altitude points
         ZUB =    1000.00 : upper bound of atmosphere (km)
       YYDDD =      92080 : year & day (YYDDD format)
       UTSEC =   45000.00 : universal time (sec)
        GLAT =      42.00 : latitude (deg)
        GLON =     000.00 : longitude (deg)
   SCALE(N2) =       1.00 : N2 density scale factor
   SCALE(O2) =       1.00 : O2 density scale factor
    SCALE(O) =       1.00 : O  density scale factor
   SCALE(O3) =       1.00 : O3 density scale factor
   SCALE(NO) =       1.00 : NO density scale factor
    SCALE(N) =       1.00 : N  density scale factor
   SCALE(He) =       1.00 : He density scale factor
    SCALE(H) =       1.00 : H  density scale factor
   SCALE(Ar) =       1.00 : Ar density scale factor
Derived parameters:
       GMLAT =      51.84 : geomagnetic latitude (deg)
       GMLON =       1.71 : geomagnetic longitude (deg)
       DPANG =      70.16 : magnetic dip angle (deg)
         SZA =      30.00 : solar zenith angle (deg)
         SLT =       1.00 : solar local time (hours)
      F10DAY =      79.30 : F10.7 (current day)
      F10PRE =      76.80 : F10.7 (previous day)
      F10AVE =      79.40 : F10.7 (81-day average)
       AP(1) =       9.00 : daily Ap
       AP(2) =      -1.00 : 3-hour Ap
       AP(3) =      -1.00 : 3-hour Ap
       AP(4) =      -1.00 : 3-hour Ap
       AP(5) =      -1.00 : 3-hour Ap
       AP(6) =      -1.00 : average 3-hour Ap
       AP(7) =      -1.00 : average 3-hour Ap"""

