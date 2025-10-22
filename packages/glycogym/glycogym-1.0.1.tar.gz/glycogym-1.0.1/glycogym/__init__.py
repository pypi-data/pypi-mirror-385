__version__ = "1.0"

def __getattr__(name):
    if name == "build_glycosylation":
        from glycogym.glycogym import build_glycosylation
        return build_glycosylation
    elif name == "build_lgi":
        from glycogym.glycogym import build_lgi
        return build_lgi
    elif name == "build_taxonomy":
        from glycogym.glycogym import build_taxonomy
        return build_taxonomy
    elif name == "build_tissue":
        from glycogym.glycogym import build_tissue
        return build_tissue
    else:
        raise AttributeError(f"module {__name__} has no attribute {name}")
