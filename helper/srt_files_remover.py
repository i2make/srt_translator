# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
# .\venv\Scripts\activate.ps1

import os
from scan_path_helper import scan_path

def fileRemove():
    path = ""
    fileList = scan_path(path, '.vtt', '')
    for file in fileList:
        if not file[-11:].lower() == 'english.vtt' and not file[-10:].lower() == 'korean.vtt':
            os.remove(file)

def srtFileRemove():
    path = ""
    fileList = scan_path(path, '.srt', '')
    for file in fileList:
        os.remove(file)

if __name__ == "__main__":
    srtFileRemove()
