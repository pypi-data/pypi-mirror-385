from importlib import util

if util.find_spec("wowool.sdk") is not None:
    from wowool.sdk import Pipeline
else:
    if util.find_spec("wowool.portal") is not None:
        from wowool.portal import Pipeline
    else:
        raise ImportError("Please install the wowool package: pip install wowool-sdk or pip install wowool-portal)")
