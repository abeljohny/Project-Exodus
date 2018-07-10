import sys
import os
import requests
import vlc
from multiprocessing import Queue
import cx_Freeze

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

os.environ['TCL_LIBRARY'] = r'C:\Users\Abel\AppData\Local\Programs\Python\Python36-32\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\Abel\AppData\Local\Programs\Python\Python36-32\tcl\tk8.6'

executables = [
    cx_Freeze.Executable("./Project Exodus.py", base=base, icon="./Assets/Textures/icon256.ico")
]

cx_Freeze.setup(
    name="Project Exodus",
    version = '1.0.3',
    author = "Avengers Software",
    options={
        "build_exe": {
             "includes": ["numpy.core._methods", "numpy.lib.format", "idna.idnadata"],
             "include_files": ["Assets", "tcl86t.dll", "tk86t.dll", "gamedata.json", "LICENSE", "README.md"]
        }
    },
    executables=executables
)