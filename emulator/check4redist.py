import os
import sys
import _winreg as winreg
import webbrowser

def is_cpp_redistributable_installed(visual_studio_version):
    try:
        # Attempt to open the 64-bit registry view first
        key_path = r"SOFTWARE\Microsoft\VisualStudio\{0}\VC\Runtimes\x64".format(visual_studio_version)
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        winreg.CloseKey(key)
        return True
    except WindowsError:
        try:
            # If not found, try the 32-bit registry view
            key_path = r"SOFTWARE\WOW6432Node\Microsoft\VisualStudio\{0}\VC\Runtimes\x64".format(visual_studio_version)
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            winreg.CloseKey(key)
            return True
        except WindowsError:
            return False


def open_download_link(download_link):
    webbrowser.open(download_link)

# Define the version of Visual Studio you want to check
visual_studio_version = "14.0"  # For Visual Studio 2017 (Update this if needed)
def check_redist():
    if is_cpp_redistributable_installed(visual_studio_version):
       # print("Microsoft C++ Redistributable for Visual Studio {} is installed.".format(visual_studio_version))
        return 1
    else:
        print("Microsoft C++ Redistributable for Visual Studio {} is not installed.".format(visual_studio_version))
        download_link = "https://aka.ms/vs/14/release/VC_redist.x64.exe"  # Update with the appropriate link
        print("You can download it from:", download_link)
        open_download_link(download_link)
        raw_input("Press Enter to exit.")  # Pause to see the result
        return 0
