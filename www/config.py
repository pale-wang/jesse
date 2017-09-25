import config_default

def merge(defaults, override):
    r = {}
    for k, v in defaults.items():
        if k in override:
            if isinstance(v, dict):
                r[k] = merge(v, override[k])
            else:
                r[k] = override[k]
        else:
            r[k] = v
    return r

configs = config_default.configs

try:
    import config_override
    configs = merge(configs, config_override.configs)
    print(configs)
except ImportError:
    pass