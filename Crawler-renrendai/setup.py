import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = 'Win32GUI'

setup(
    name = 'crawler_renrendai.exe',
    version = '1.0',
    description = 'web crawler for renrendai.com', 
    executables = [Executable('Crawler_renrendai.py', base = 'Win32GUI')])