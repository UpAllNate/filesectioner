from __future__ import annotations

import os
import shutil
import pathlib

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
# section_number     : 1
# section_description: SectionDirs
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~-

# Directory path containing the text files
dir_this_file_parent = pathlib.Path(__file__).parent.resolve()
dir_sections = dir_this_file_parent.joinpath("sections")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
# section_number     : 2
# section_description: make_empty_dir
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~-

def make_empty_dir(dir):
    # Check whether the specified path exists or not
    if os.path.exists(dir):
        shutil.rmtree(dir)

    os.mkdir(dir)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
# section_number     : 7
# section_description: detect_files
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~-

def detect_all_master_files(dir) -> list[MasterFile]:

    return_files : list[MasterFile] = []

    for path in os.listdir(dir):
        new_master_file = MasterFile(path= dir_this_file_parent.joinpath(path))
        if new_master_file.lines_readable:
            return_files.append(new_master_file)

    return return_files

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
# section_number     : 8
# section_description: parse_sections
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~-

def parse_sections(master_file : MasterFile, renumber_sections = False) -> list[SectionFile]:

    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
# section_number     : 9
# section_description: generate_section_files
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~-

def generate_section_files(master_file : MasterFile) -> None:

    for section in master_file.sections:
            # # print(section)
            # for line in section.lines:
            #     # print(line, end="")
            with open(section.path, "w") as f:
                if section.lines:
                    if section.lines[-1] == "\n":
                        f.write(section.lines[:-1])
                    else:
                        f.write(section.lines)
                else:
                    f.write("")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
# section_number     : 10
# section_description: build_sections
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~-

def build_sections(master_file : MasterFile) -> MasterFile:

    print("build")

    master_file.sections = parse_sections(master_file= master_file, renumber_sections= True)
    make_empty_dir(dir_sections.joinpath(master_file.dir_master_sections))
    generate_section_files(master_file= master_file)

    return master_file


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
# section_number     : 11
# section_description: detect_all_section_files
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~-

def detect_all_section_files(master_file : MasterFile) -> list[SectionFile]:

    return_files : list[SectionFile] = []

    for file in os.listdir(master_file.dir_master_sections):

        try:
            new_section_file = SectionFile(
                path= master_file.dir_master_sections.joinpath(file),
                section_number= int(file.split("__")[0]),
                section_description= file[file.index("__"):].split(".")[0],
                master_file= master_file
            )

        except:
            continue

        if new_section_file.lines_readable:
            return_files.append(new_section_file)

    return return_files


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
# section_number     : 12
# section_description: main
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~-

if __name__ == "__main__":

    import time

    make_empty_dir(dir= dir_sections)

    mfiles : list[MasterFile] = []

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
# section_number     : 13
# section_description: mainLoop
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~-

    try:
        while True:

            # Add new master files
            potential_masters = detect_all_master_files(dir= dir_this_file_parent)

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