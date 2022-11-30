#!/usr/bin/env python
import os
import re

path = "/Users/whitney/myprojects"
path2 = "/Users/whitney/raw_data"
current_dir = os.getcwd()
os.chdir(path)  # Change current directory 
# Finds the latest file in the directory and returns it
# Probably won't work on Windows machines, tho

# Finds the latest file in the directory and returns it
# If the grabbed directory doesn't match the filename format in the
# destination directory, call user for directory name
file = max(os.listdir(), key=os.path.getctime)

if re.search(r"(\d+_\d+_\d+)", file):   # Regex for valid file
    # Exclude file extension, replacing dash for underscore
    new_file = file.replace('_', '-')[:10]
    print(f"\nSuccess!\n{new_file}\n")
    os.chdir(current_dir)   # Change current directory back
    myfile = max(os.listdir(), key=os.path.getctime).replace('_', '-')[:10]

else:
    print(f"\nNo match dude: {file}\n")
    _path = input("\nEnter correct path:\n")
    os.chdir(_path)

    file = max(os.listdir(), key=os.path.getctime)
    print(f"File: {file}\n")

    if re.search(r"(\d+_\d+_\d+)", file):
        new_file = file.replace('_', '-')[:10]
        print(f"\nSuccess!\n{new_file}\n")
        os.chdir(current_dir)   # Change current directory back
        myfile = max(os.listdir(), key=os.path.getctime).replace('_', '-')[:10]

