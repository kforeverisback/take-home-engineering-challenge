# -*- coding: utf-8 -*-
def _assertNotRaises(self, exception, obj, attr):
    try:
        result = getattr(obj, attr)
        if hasattr(result, "__call__"):
            result()
    except Exception as e:
        if isinstance(e, exception):
            raise AssertionError("{}.{} raises {}.".format(obj, attr, exception))
