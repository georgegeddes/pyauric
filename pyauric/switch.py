class Switch:
    """Simple class to make the radtrans options easy."""
    _t = ["ON","on",True,1]
    _f = ["OFF","off",False,0]
    _a = _t + _f
    def __init__(self,x):
        if type(x) == type(self):
            self._x = x._x
        else:
            assert x in self._a, "value must be one of {}".format(self._a)
            self._x = x

    def __bool__(self):
        if self._x in self._t:
            return True
        elif self._x in self._f:
            return False

    def __eq__(self,other):
        if other not in self._a:
            raise NotImplementedError
        if self:
            return (other in self._t)
        else:
            return (other in self._f)

    def __repr__(self):
        if self:
            return "ON"
        else:
            return "OFF"
        
if __name__=="__main__":
    on = Switch("ON")
    tr = Switch(True)
    off = Switch("OFF")
    fa = Switch(False)
    def passed(): print("passed")
    def failed(): print("failed")
    print("logic",end=" ")
    if (on==tr) and (off==fa) and (on!=off):
        passed()
    else:
        failed()
    print("repr",end=" ")
    if " ".join(map(repr,(on,off,tr,fa))) == "ON OFF ON OFF":
        passed()
    else:
        failed()
    print("construction",end=" ")
    if Switch(on) == on:
        passed()
    else:
        failed()

