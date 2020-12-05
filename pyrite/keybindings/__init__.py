import platform

if platform.system() == 'Linux':
    from .linux import *
else:
    raise RuntimeError(f"Unsupported platform: '{platform.system()}'")
