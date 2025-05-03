# Standard libraries
import sys, os, platform, traceback, tempfile
from datetime import datetime

# Internal libraries
from scribe import read_file, write_new_lines

def parse_old_lines(path: str, old_lines: list) -> list:
    # Remove lines with encoding markers and adjacent empty lines
    new_lines = []
    skip_next = False

    for i, line in enumerate(old_lines):
        if any(key in line for key in ["P103", "#6"]):
            skip_next = True
            continue
        if skip_next:
            if line.strip() == "":
                skip_next = False
                continue
        new_lines.append(line)

    return new_lines

def remove_encoding(path:str):
    old_lines = read_file(path)
    new_lines = parse_old_lines(path, old_lines)
    write_new_lines(path, new_lines)
