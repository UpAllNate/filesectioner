from __future__ import annotations

import os
import shutil
from pathlib import Path

from header import SectionHeader
from file_class import MasterFile, SectionFile

import argparse

dir_working = Path(os.getcwd()).resolve()

parser = argparse.ArgumentParser(description='Maintain section files.')
parser.add_argument('dirs', metavar='d', type=str, nargs='*', default= ["."],
                    help='directories or files to manage')

args = parser.parse_args()

# Define section header objects
python_header = SectionHeader(
    key_sequence= [
        "# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n",
        "# section number     : ",
        "___number___",
        "\n",
        "# section description: ",
        "___description___",
        "\n",
        "# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    ],
    key_number="___number___",
    key_description="___description___"
)

st_header = SectionHeader(
    key_sequence= [
        "// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n",
        "// section number     : ",
        "___number___",
        "\n",
        "// section description: ",
        "___description___",
        "\n",
        "// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    ],
    key_number="___number___",
    key_description="___description___"
)

all_section_headers = [
    python_header,
    st_header
]

def get_master_files(directories : list[str], headers : list[SectionHeader]) -> list[MasterFile]:

    input_dirs = directories

    # Evaluate directories and convert to Path class objects
    pops = []
    for i, dir in enumerate(input_dirs):

        if dir == ".":
            pops.append(i)
            for d in os.listdir(dir_working):
                if Path(dir).joinpath(d).is_file():
                    input_dirs.append(Path(dir).joinpath(d).resolve()) 

        elif Path(dir).is_dir():
            pops.append(i)
            for d in os.listdir(dir):
                if Path(dir).joinpath(d).is_file():
                    input_dirs.append(Path(dir).joinpath(d).resolve())    
        
        elif Path(dir).is_file():
            input_dirs[i] = Path(dir).resolve()
        
        else:
            pops.append(i)

    for i in sorted(pops, reverse=True):
        input_dirs.pop(i)

    master_files : list[MasterFile] = []
    for file in input_dirs:
        new_master_file = MasterFile(file)
        added = False
        if new_master_file.lines_readable:
            for header in headers:
                if not added:
                    new_master_file.section_header = header
                    new_master_file.parse()
                    if new_master_file.sections:
                        added = True
                        master_files.append(new_master_file)
    
    return master_files

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# section number     : 2
# section description: make_empty_dir
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def make_empty_dir(dir):
    # Check whether the specified path exists or not
    if os.path.exists(dir):
        shutil.rmtree(dir)

    os.mkdir(dir)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# section number     : 9
# section description: generate_section_files
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def generate_section_files(master_file : MasterFile) -> None:

    make_empty_dir(master_file.dir_master_sections)
    
    for section in master_file.sections:

        with open(section.path, "w") as f:
            if section.lines:
                for line_number, line in enumerate(section.lines):
                    if line_number < len(section.lines) - 1:
                        f.write(line + "\n")
                    else:
                        f.write(line)
            else:
                f.write("")
            

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# section number     : 10
# section description: build_sections
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def build_sections(master_file : MasterFile) -> MasterFile:

    print("build")

    master_file.parse()
    make_empty_dir(dir_sections.joinpath(master_file.dir_master_sections))
    generate_section_files(master_file= master_file)

    return master_file


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# section number     : 11
# section description: detect_all_section_files
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def detect_all_section_files(master_file : MasterFile) -> list[SectionFile]:

    return_files : list[SectionFile] = []

    for path in os.listdir(master_file.dir_master_sections):

        try:
            new_section_file = SectionFile(
                path= master_file.dir_master_sections.joinpath(path),
                section_number= int(path.split("__")[0]),
                section_description= path[path.index("__"):].split(".")[0],
                master_file= master_file
            )

        except:
            continue

        if new_section_file.lines_readable:
            return_files.append(new_section_file)

    return return_files


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# section number     : 12
# section description: main
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == "__main__":

    import time

    make_empty_dir(dir= dir_sections)

    mfiles : list[MasterFile] = []

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# section number     : 13
# section description: mainLoop
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    try:
        while True:

            for header_object in all_section_headers:

                # Add new master files
                potential_masters = detect_all_master_files(
                    dir= dir_this_file_parent,
                    section_header= python_header
                )

                for pm in potential_masters:
                    if pm not in mfiles:
                        mfiles.append(pm)

            # Evaluate all master files
            pop_indexes = []

            # Detect changes to a master file.
            # Remove sections if the master file is
            # deleted
            for index, mfile in enumerate(mfiles):

                if mfile.dir_master_sections.is_dir():

                    # Make sure all section files that are present
                    # match all section files within the scope of master file
                    section_file_mismatch = False
                    potential_sections = detect_all_section_files(master_file= mfile)

                    for file in potential_sections:
                        if file not in mfile.sections:
                            section_file_mismatch = True

                    for file in mfile.sections:
                        if file not in potential_sections:
                            section_file_mismatch = True

                else:
                    make_empty_dir(dir= mfile.dir_master_sections)

                if mfile.path.is_file() \
                    and (
                        mfile.detect_file_change()
                        or not mfile.sections
                        or section_file_mismatch
                    ):
                        mfiles[index] = build_sections(master_file= mfile)
                else:
                    make_empty_dir(dir= mfile.dir_master_sections)
                    os.rmdir(path= mfile.dir_master_sections)
                    pop_indexes.append(index)

            for index in sorted(pop_indexes, reverse= True):
                mfiles.pop(index)

            time.sleep(.1)

    except KeyboardInterrupt:
        exit()