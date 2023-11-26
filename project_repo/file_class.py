from __future__ import annotations

import pathlib
import os

from header import SectionHeader

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
        if self.prev_mod_time != new_mod_time and new_mod_time is not None:
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
    """MonitoredFile that is one numbered and described part of a MasterFile"""

    def __init__(
        self,
        path : pathlib.Path,
        section_number: int,
        section_description: str,
        master_file : MasterFile
    ) -> None:

        super().__init__(path)
        self.section_number = section_number
        self.section_description = section_description
        self.lines = ""
        self.master_file = master_file

class MasterFile(MonitoredFile):
    """MonitoredFile with sections delimited by headers"""
    def __init__(self, path : pathlib.Path, dir_master_sections : pathlib.Path) -> None:

        super().__init__(path)
        self.dir_master_sections = dir_master_sections
        self.sections : list[SectionFile] = []
        self.section_header : SectionHeader = None

    def parse(self) -> None:

        # The header sequence specifies the position
        # in standard_header_sequence that is being
        # parsed for

        last_head_sq_index = len(self.section_header.key_sequence) - 1

        head_sq_index = 0
        parsing_header = False
        parsing_valid_section = False
        self.sections : list[SectionFile] = []
        header_str = ""

        section_number = None
        section_description = None

        with open(self.path, "r") as f:

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

                    current_header_sequence_string = self.section_header.key_sequence[head_sq_index]

                    test_string = line[
                        index_char :
                        index_char + len(current_header_sequence_string)
                    ]

                    header_sequence_match = test_string == current_header_sequence_string

                    pulse_last_head_sq_index = last_head_sq_index == head_sq_index
                    header_parse_success = False

                    # Header text match
                    if header_sequence_match:
                        index_char += len(self.section_header.key_sequence[head_sq_index])
                        if head_sq_index == 0:
                            header_str = test_string
                            parsing_header = True
                        
                        header_parse_success = True

                    # Header sequence number
                    if current_header_sequence_string == self.section_header.key_number:

                        parse_key = False

                        # Get the section number as string
                        if pulse_last_head_sq_index:
                            section_number_str = line[index_char:].strip()
                            parse_key = True

                        else:
                            next_test_string = self.section_header.key_sequence[head_sq_index + 1]
                            try:
                                next_test_string_index = line.index(next_test_string)
                            except:
                                pass
                            else:
                                section_number_str = line[index_char : next_test_string_index].strip()
                                parse_key = True

                        if parse_key:
                            try:
                                section_number = int(section_number_str)
                            except:
                                pass
                            else:
                                header_parse_success = True
                                
                        if header_parse_success:
                            # Either already true or the case
                            # of first sequence index being section number
                            if not parsing_header:
                                header_str = section_number_str
                            else:
                                header_str += section_number_str
                            parsing_header = True

                        else:
                            section_number = None
                            parsing_header = False
                            if parsing_valid_section:
                                pass # TODO: Implement putting this header back into the previous section lines

                    # Header sequence description
                    if current_header_sequence_string == self.section_header.key_description:

                        # Get the section number as string
                        if pulse_last_head_sq_index:
                            section_description = line[index_char:].strip()
                            header_parse_success = True

                        else:
                            next_test_string = self.section_header.key_sequence[head_sq_index + 1]
                            try:
                                next_test_string_index = line.index(next_test_string)
                            except:
                                pass
                            else:
                                section_description = line[index_char : next_test_string_index].strip()
                                header_parse_success = True

                        if header_parse_success:
                            # Either already true or the case
                            # of first sequence index being section number
                            if not parsing_header:
                                parsing_header = True
                                header_str = section_description
                            else:
                                header_str += section_description

                        else:
                            section_number = None
                            parsing_header = False
                            if parsing_valid_section:
                                new_section_file.lines += header_str

                    if not header_parse_success:
                        parsing_header = False

                        # If a new header is detected while parsing a valid section,
                        # create a new section file and append to the return list
                        if parsing_valid_section:

                            # print(f"Attempting to create section file\n\t\tnumber:      {section_number}\n\t\tdescription: {section_description}")

                            try:
                                new_section_file = SectionFile(
                                    path= self.dir_master_sections.joinpath(
                                        str(section_number) + "__" + section_description + "." + self.filetype
                                    ),
                                    section_number= section_number,
                                    section_description= section_description,
                                    master_file= self
                                )
                            except:
                                # print("Failed to generate section file")
                                pass
                            else:
                                # print("Section file success")
                                new_section_file.lines = section_lines
                                self.sections.append(new_section_file)

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
                    self.sections.append(new_section_file)

        if renumber_sections:
            with open(master_file.path, "w") as f:
                f.writelines(master_file_lines)

        return self.sections


