import subprocess

def install_libraries(library_names):
    for library_name in library_names:
        try:
            __import__(library_name)
            print("{} library is already installed.".format(library_name))
        except ImportError:
            print("{} library is not installed. Installing...".format(library_name))
            subprocess.call(["pip", "install", "--user", library_name])
            print("{} library has been installed.".format(library_name))

