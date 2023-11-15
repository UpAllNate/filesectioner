from __future__ import annotations

import os
import shutil
import pathlib
import copy
from enum import Enum, auto as enum_auto

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Delete /sections/ and delete all section files
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Directory path containing the text files
dir_this_file_parent = pathlib.Path(__file__).parent.resolve()
dir_sections = dir_this_file_parent.joinpath("sections")

# Check whether the specified path exists or not
if os.path.exists(dir_sections):
   shutil.rmtree(dir_sections)

os.mkdir(dir_sections)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define the standard section header format
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class HeaderElement(Enum):
    HEADER_START = enum_auto()
    HEADER_END = enum_auto()
    COMMENT_DECLARATION = enum_auto()
    SECTION_NUMBER = enum_auto()
    SECTION_DESCRIPTION = enum_auto()
    SECTION_NUMBER_DESIGNATOR = enum_auto()
    SECTION_DESCRIPTION_DESIGNATOR = enum_auto()

header_key_words = {
    HeaderElement.COMMENT_DECLARATION : "//",
    HeaderElement.SECTION_NUMBER_DESIGNATOR : "_section_number_      ",
    HeaderElement.SECTION_NUMBER : "_value_{section number}",
    HeaderElement.SECTION_DESCRIPTION_DESIGNATOR : "_section_description_ ",
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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Evaluate sequence for errors
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if standard_header_sequence[0] != header_key_words[HeaderElement.HEADER_START]:
    print("No, no. The first characters of the standard header sequence must be the HEADER_START keyword")
    print("Press enter to exit")
    _ = input()
    exit()

if standard_header_sequence[-1] != header_key_words[HeaderElement.HEADER_END]:
    print("No, no. The last characters of the standard header sequence must be the HEADER_END keyword")
    print("Press enter to exit")
    _ = input()
    exit()

if standard_header_sequence[-2] != "\n":
    print("No, no. The HEADER_END keyword at the end of the header sequence must be on it's own line. Add a new line \\n")
    print("Press enter to exit")
    _ = input()
    exit()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Headers will be generated using search and replace
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

# print(generate_section_header(number= 34, description= "The only way to fly"))
# exit()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# A monitored file has methods for detecting a file change
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MonitoredFile:

    def __init__(self, path : pathlib.Path) -> None:
        self.path = path
        self.filename = self.path.name.split(".")[0]
        self.filetype = self.path.name.split(".")[-1]
        self.prev_mod_time = self.get_mod_time()
        self.pulse_file_changed : bool = False

        # Attempt to read all lines on init to validate this is possible for this file.
        with open(self.path, "r") as f:
            self.lines = f.readlines()

        # Save the RAM, we don't need the lines right now.
        self.lines = ""

    def get_mod_time(self) -> float:
        try:
            return os.stat(self.path).st_mtime
        except:
            print(f"Couldn't get modified time. Was the file {self.path} deleted??")
            raise

    def detect_file_change(self) -> bool:
        new_mod_time = self.get_mod_time()
        if self.prev_mod_time != new_mod_time:
            self.pulse_file_changed = True
            self.prev_mod_time = new_mod_time
        else:
            self.pulse_file_changed = False

        return self.pulse_file_changed

class SectionFile(MonitoredFile):
    """MonitoredFile that is one named and numbered part of a MasterFile"""

    def __init__(self, path : pathlib.Path, section_number: int, section_description: str, master_file : MasterFile) -> None:
        super().__init__(path)
        self.section_number = section_number
        self.section_description = section_description
        self.master_file = master_file

class MasterFile(MonitoredFile):
    """MonitoredFile with sections delimited by headers"""

    def __init__(self, path : pathlib.Path) -> None:
        super().__init__(path)
        self.dir_master_sections = dir_sections.joinpath(self.filename)
        self.sections : list[SectionFile] = []

def detect_all_master_files() -> list[MasterFile]:

    return_files : list[MasterFile] = []

    for path in os.listdir():
        try:
            new_master_file = MasterFile(path= dir_this_file_parent.joinpath(path))
        except:
            pass
        else:
            return_files.append(new_master_file)

    return return_files

def parse_sections(master_file : MasterFile) -> list[SectionFile]:

    parsing_header = True
    return_files : list[SectionFile] = []

    with open(master_file, "r") as f:

        parsing_header = False
        parsing_valid_section = False

        for line in f:

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

                # A header's first line must entirely consist of the HEADER_START string
                if line == header_key_words[HeaderElement.HEADER_START]:

                    # If a new header is detected while parsing a valid section,
                    # create a new section file and append to the return list
                    if parsing_valid_section:
                        new_section_file = SectionFile(
                            path= master_file.dir_master_sections.joinpath(
                                section_description + "." + master_file.filetype
                             ),
                            section_number= section_number,
                            section_description= section_description,
                            master_file= master_file
                        )

                        return_files.append(new_section_file)

                    parsing_header = True
                    parsing_index = 1
                    section_lines = ""
                    section_number = 0
                    section_description = ""

                    index_char = len(line)

                if parsing_header:

                    last_parsing_index = parsing_index + 1 >= len(standard_header_sequence)

                    seq_str = standard_header_sequence[parsing_index]

                    # Parse section number
                    if seq_str == header_key_words[HeaderElement.SECTION_NUMBER]:

                        # If this is the last attribute in the header,
                        # assume the remainder of the line is the section
                        # number and take it!
                        if last_parsing_index:
                            try:
                                section_number_str = line[index_char:].strip()
                                section_number = int(section_number_str)
                            except:
                                pass
                            finally:

                                # End parsing on this line whether a number was found or not.
                                index_char = len(line)

                        # Otherwise, split by the next substring and take the int
                        else:
                            try:
                                section_number_str = line[index_char:].split(standard_header_sequence[parsing_index + 1])[0].strip()
                                section_number = int(section_number_str)
                            except:

                                # End line parsing if the number couldn't be parsed
                                index_char = len(line)
                            else:

                                # If parsing was successful, increment the character index
                                index_char += len(section_number_str)


                    # Parse section description
                    elif seq_str == header_key_words[HeaderElement.SECTION_DESCRIPTION]:

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
                                section_description = line[index_char:].split(standard_header_sequence[parsing_index + 1])[0].strip()
                            except:

                                # End line parsing if the description couldn't be parsed
                                index_char = len(line)
                            else:

                                # If parsing was successful, increment the character index
                                index_char += len(section_description)

                    # Move along if this is boilerplate header text
                    elif seq_str == line[index_char:len(seq_str)]:
                        index_char += len(seq_str)
                        parsing_index += 1

                if parsing_valid_section:
                    pass


        # If the line loop ends while parsing a valid section,
        # create a new section file and append to the return list
        if parsing_valid_section:
            new_section_file = SectionFile(
                path= master_file.dir_master_sections.joinpath(
                    section_description + "." + master_file.filetype
                    ),
                section_number= section_number,
                section_description= section_description,
                master_file= master_file
            )

            return_files.append(new_section_file)







def generate_section_files(master_file : MasterFile) -> None:



def update_master_files(master_files : list[MasterFile]) -> list[MasterFile]:

    current_master_files = detect_all_master_files()





def detect_all_section_files(master_files : list[MasterFile]) -> list[SectionFile]:
    """Section files are appended to master file attribute

    Writes to """

    for m in master_files:

        with open(m.path, "r") as f:
            for line_number, line in enumerate(f):

                # Start parsing header
                if line == standard_header_sequence[0]:
                    pass
