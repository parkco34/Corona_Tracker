#!/usr/bin/env python
import os
path = "/Users/whitney/raw_data"
def get_max_date(path):
    os.chdir(path)
    start_date = max(os.listdir(path))[:10]
    print(f"{start_date.replace('_', '-')}")
    if os.path.isfile(f"{start_date}" + 
                      ".txt"):
        return (f"{start_date.replace('_', '-')}")

    else:
        return input(
    """\nEnter the starting date in the format: mm_dd_yyyy\n
    """) + ".txt"

get_max_date(path)
