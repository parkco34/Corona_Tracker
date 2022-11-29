#!/usr/bin/env python
import os

def get_max_date(path):
    os.chdir(path)
    # Finds the latest file in the directory and returns it
    # If the grabbed directory doesn't match the filename format in the
    # destination directory, call user for directory name
    dir = max(os.listdir(), key=os.path.getctime).replace('_', '-')[:10]
    if dir == "proper":
        pass

PATH = "/Users/whitney/myprojects"
print(get_max_date(PATH))
