import os, sys
argv = [os.path.join(os.path.dirname(__file__), "dbc.exe"), *sys.argv[1:]]
if os.name == 'posix':
    os.execv(argv[0], argv)
else:
    import subprocess; sys.exit(subprocess.call(argv))

def dummy(): """Dummy function for an entrypoint. dbc is executed as a side effect of the import."""
