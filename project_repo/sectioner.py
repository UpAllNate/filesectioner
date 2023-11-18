from __future__ import annotations

import os
import shutil
import pathlib
import copy
from enum import Enum, auto as enum_auto

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
# section_number     : 3
# section_description: HeaderDefinition
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~-

class HeaderElement(Enum):
    HEADER_START = enum_auto()
    HEADER_END = enum_auto()
    COMMENT_DECLARATION = enum_auto()
    SECTION_NUMBER = enum_auto()
    SECTION_DESCRIPTION = enum_auto()
    SECTION_NUMBER_DESIGNATOR = enum_auto()
    SECTION_DESCRIPTION_DESIGNATOR = enum_auto()

header_key_words = {
    HeaderElement.COMMENT_DECLARATION : "#",
    HeaderElement.SECTION_NUMBER_DESIGNATOR : "section_number     :",
    HeaderElement.SECTION_NUMBER : "_value_{section number}",
    HeaderElement.SECTION_DESCRIPTION_DESIGNATOR : "section_description:",
    HeaderElement.SECTION_DESCRIPTION : "_value_{section description}"
}

header_key_words[HeaderElement.HEADER_START] = header_key_words[HeaderElement.COMMENT_DECLARATION] + " " + "~"*70 + "+"
header_key_words[HeaderElement.HEADER_END] = header_key_words[HeaderElement.COMMENT_DECLARATION] + " " + "~"*70 + "-"

# The sequence must start and end with Header Start / Header End
standard_header_sequence = (
    header_key_words[HeaderElement.HEADER_START],
    "\n",
    header_key_words[HeaderElement.COMMENT_DECLARATION],
    " ",
    header_key_words[HeaderElement.SECTION_NUMBER_DESIGNATOR],
    " ",
    header_key_words[HeaderElement.SECTION_NUMBER],
    "\n",
    header_key_words[HeaderElement.COMMENT_DECLARATION],
    " ",
    header_key_words[HeaderElement.SECTION_DESCRIPTION_DESIGNATOR],
    " ",
    header_key_words[HeaderElement.SECTION_DESCRIPTION],
    "\n",
    header_key_words[HeaderElement.HEADER_END]
)

standard_header = ''.join(element for element in standard_header_sequence)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
# section_number     : 4
# section_description: HeaderDefinitionErrors
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~-

if standard_header_sequence[0] != header_key_words[HeaderElement.HEADER_START]:
    # print("No, no. The first characters of the standard header sequence must be the HEADER_START keyword")
    # print("Press enter to exit")
    _ = input()
    exit()

if standard_header_sequence[-1] != header_key_words[HeaderElement.HEADER_END]:
    # print("No, no. The last characters of the standard header sequence must be the HEADER_END keyword")
    # print("Press enter to exit")
    _ = input()
    exit()

if standard_header_sequence[-2] != "\n":
    # print("No, no. The HEADER_END keyword at the end of the header sequence must be on it's own line. Add a new line \\n")
    # print("Press enter to exit")
    _ = input()
    exit()
 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
# section_number     : 5
# section_description: generate_section_header
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~-

def generate_section_header(number : int, description : str) -> str:

    global header_key_words
    global standard_header

    section_number_key_word = header_key_words[HeaderElement.SECTION_NUMBER]
    section_description_key_word = header_key_words[HeaderElement.SECTION_DESCRIPTION]

    new_header = copy.deepcopy(standard_header)

    while section_number_key_word in new_header:
        new_header = new_header.replace(section_number_key_word, str(number))

    while section_description_key_word in new_header:
        new_header = new_header.replace(section_description_key_word, description)

    return new_header

# # print(generate_section_header(number= 34, description= "The only way to fly"))

# # print(generate_section_header(number= 35, description= "A special crow swoops"))

# # print(generate_section_header(number= 36, description= "Down frost exposure"))
# exit()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
# section_number     : 6
# section_description: file_classes
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~-

class MonitoredFile:

    def __init__(self, path : pathlib.Path) -> None:
        self.path = path
        self.filename = self.path.name.split(".")[0]
        self.filetype = self.path.name.split(".")[-1]
        self.prev_mod_time = self.get_mod_time()
        self.pulse_file_changed : bool = False
        

        # Attempt to read all lines on init to validate this is possible for this file.
        try:
            with open(self.path, "r") as f:
                self.lines = f.readlines()
        except:
            self.lines_readable = False
        else:
            self.lines_readable = True

        # Save the RAM, we don't need the lines right now.
        self.lines = ""

    def get_mod_time(self) -> float:
        try:
            return os.stat(self.path).st_mtime
        except:
            return None

    def detect_file_change(self) -> bool:
        new_mod_time = self.get_mod_time()
        if self.prev_mod_time != new_mod_time:
            self.pulse_file_changed = True
            self.prev_mod_time = new_mod_time
        else:
            self.pulse_file_changed = False

        return self.pulse_file_changed

    def __eq__(self, __value: object) -> bool:
        return self.path == __value.path
    
    def __hash__(self) -> int:
        return hash(tuple(self.path, self.filename, self.filetype))

class SectionFile(MonitoredFile):
    """MonitoredFile that is one named and numbered part of a MasterFile"""

    def __init__(self, path : pathlib.Path, section_number: int, section_description: str, master_file : MasterFile) -> None:
        super().__init__(path)
        self.section_number = section_number
        self.section_description = section_description
        self.master_file = master_file

    def __str__(self) -> str:
        return f"Section File {self.section_number}, '{self.section_description}'"

class MasterFile(MonitoredFile):
    """MonitoredFile with sections delimited by headers"""
    def __init__(self, path : pathlib.Path) -> None:

        super().__init__(path)
        self.dir_master_sections = dir_sections.joinpath(self.filename + "." + self.filetype)
        self.sections : list[SectionFile] = []

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

    parsing_header = True
    return_files : list[SectionFile] = []

    with open(master_file.path, "r") as f:

        # If renumbering sections, the entire master file
        # will be saved, line by line, with section numbers
        # replaced with generated values
        if renumber_sections:
            global_section_number = 1
            master_file_lines : list[str] = []

        parsing_header = False
        parsing_valid_section = False

        # The header sequence specifies the position
        # in standard_header_sequence that is being
        # parsed for

        head_sq_index = 0

        for line in f:

            # print(f"Parsing line:\n{line}")

            line : str

            # The line is parsed by investigating whether
            # the sequence string matches the current
            # character index
            # The character index is then incremented by
            # the length of the sequence string found

            index_char = 0

            # Parse the entire line, which could contain
            # severall header sequence elements

            while index_char < len(line):

                # print(fr"Parsing substring: {line[index_char:]} of length {len(line[index_char:])}")

                # Detect start of header
                header_start_str = header_key_words[HeaderElement.HEADER_START]
                if header_start_str == line[index_char:index_char + len(header_start_str)]:

                    # print("Header Start")

                    # If a new header is detected while parsing a valid section,
                    # create a new section file and append to the return list
                    if parsing_valid_section:

                        # print(f"Attempting to create section file\n\t\tnumber:      {section_number}\n\t\tdescription: {section_description}")

                        try:
                            new_section_file = SectionFile(
                                path= master_file.dir_master_sections.joinpath(
                                    str(section_number) + "__" + section_description + "." + master_file.filetype
                                ),
                                section_number= section_number,
                                section_description= section_description,
                                master_file= master_file
                            )
                        except:
                            # print("Failed to generate section file")
                            pass
                        else:
                            # print("Section file success")
                            new_section_file.lines = section_lines
                            return_files.append(new_section_file)

                    parsing_header = True
                    head_sq_index = 1
                    section_number = 0
                    section_description = ""

                    index_char += len(header_start_str)

                elif parsing_header:

                    seq_str = standard_header_sequence[head_sq_index]
                    # print(fr"Parsing substring: {line[index_char:]} of length {len(line[index_char:])} for seq_str: {seq_str} of length {len(seq_str)}")

                    # We can only be parsing one at a time
                    parsing_valid_section = False

                    last_parsing_index = head_sq_index + 1 >= len(standard_header_sequence)

                    # Parse section number
                    if seq_str == header_key_words[HeaderElement.SECTION_NUMBER]:

                        # print("Section Number")
                        head_sq_index += 1

                        # If this is the last attribute in the header,
                        # assume the remainder of the line is the section
                        # number and take it!
                        if last_parsing_index:
                            try:
                                section_number_str = line[index_char:].strip()
                                section_number = int(section_number_str)

                                # If replacing the section number,
                                # Set section_number for the section file class
                                # and replace the text in this line
                                if renumber_sections and section_number:

                                    line = line.replace(section_number_str, str(global_section_number))

                                    section_number_str = str(global_section_number)
                                    section_number = global_section_number
                                    global_section_number += 1

                            except:
                                pass
                            finally:

                                # End parsing on this line whether a number was found or not.
                                index_char = len(line)

                        # Otherwise, split by the next substring and take the int
                        else:
                            try:
                                section_number_str = line[index_char:].split(standard_header_sequence[head_sq_index + 1])[0].strip()
                                section_number = int(section_number_str)

                                # If replacing the section number,
                                # Set section_number for the section file class
                                # and replace the text in this line
                                if renumber_sections and section_number:

                                    line = line.replace(section_number_str, str(global_section_number))

                                    section_number_str = str(global_section_number)
                                    section_number = global_section_number
                                    global_section_number += 1

                            except:

                                # End line parsing if the number couldn't be parsed
                                index_char = len(line)
                            else:

                                # If parsing was successful, increment the character index
                                index_char += len(section_number_str)

                    # Parse section description
                    elif seq_str == header_key_words[HeaderElement.SECTION_DESCRIPTION]:

                        # print("Section Description")
                        head_sq_index += 1

                        # If this is the last attribute in the header,
                        # assume the remainder of the line is the section
                        # description and take it!
                        if last_parsing_index:
                            try:
                                section_description = line[index_char:].strip()
                            except:
                                pass
                            finally:

                                # End parsing on this line whether a description was found or not.
                                index_char = len(line)

                        # Otherwise, split by the next substring and take the int
                        else:
                            try:
                                section_description = line[index_char:].split(standard_header_sequence[head_sq_index + 1])[0].strip()
                            except:

                                # End line parsing if the description couldn't be parsed
                                index_char = len(line)
                            else:

                                # If parsing was successful, increment the character index
                                index_char += len(section_description)

                    # Complete header parsing and evaluate if header valid
                    elif line.strip()  == header_key_words[HeaderElement.HEADER_END]:

                        # print("Header End")

                        if parsing_header and section_number > 0 and section_description != "":
                            parsing_valid_section = True

                        index_char += len(line)

                        parsing_header = False
                        section_lines = ""
                        add_lines = ""

                    # Move along if this is boilerplate header text
                    elif seq_str == line[index_char:index_char + len(seq_str)]:

                        # print(fr"Sequence String Match: {seq_str}")

                        index_char += len(seq_str)
                        head_sq_index += 1

                    # If this section of header isn't in the header sequence,
                    # then it's an improperly formatted header.
                    else:
                        # print(fr"Bad Header, seq_str: {seq_str}, substring: {line[index_char:]}")

                        parsing_header = False

                elif parsing_valid_section:

                    # print("Parsing valid section")
                    index_char = len(line)

                    # Skip leading empty lines
                    if section_lines or line.strip():
                        # print("Adding to add_lines")
                        add_lines += line

                        # Skip empty lines at the end
                        if line.strip():
                            # print("Pushing add_lines to section_lines")
                            section_lines += add_lines
                            add_lines = ""

                # If not parsing a header or valid section, just continue
                else:
                    # print("This line is meaningless")

                    index_char = len(line)
            
            if renumber_sections:
                master_file_lines.append(line)

        # If the line loop ends while parsing a valid section,
        # create a new section file and append to the return list
        if parsing_valid_section:

            # print(f"Attempting to create section file\n\t\tnumber:      {section_number}\n\t\tdescription: {section_description}")

            try:
                new_section_file = SectionFile(
                    path= master_file.dir_master_sections.joinpath(
                        str(section_number) + "__" + section_description + "." + master_file.filetype
                    ),
                    section_number= section_number,
                    section_description= section_description,
                    master_file= master_file
                )
            except:
                # print("Failed to generate section file")
                pass
            else:
                # print("Section file success")
                new_section_file.lines = section_lines
                return_files.append(new_section_file)
    
    if renumber_sections:
        with open(master_file.path, "w") as f:
            f.writelines(master_file_lines)

    return return_files

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