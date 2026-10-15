try:
    import cms
    from packaging.version import Version as _V

    CMS_4_PLUS = _V(cms.__version__) >= _V("4.0")
except ImportError:
    CMS_4_PLUS = False
