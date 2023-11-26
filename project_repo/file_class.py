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
                self.lines : list[str] = f.readlines()
        except:
            self.lines_readable = False
        else:
            self.lines_readable = True

        # Save the RAM, we don't need the lines right now.
        self.lines : list[str] = []

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
        self.lines : list[str] = []
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
        header_lines : list[str] = []
        section_lines : list[str] = [] # Used to only extend section lines with non empty lines

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
                                index_char += len(section_number_str)

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
                                index_char += len(section_description)

                    # Increment header sequence index
                    # or reset if header parsing failure
                    if header_parse_success:
                        head_sq_index += 1
                        if pulse_last_head_sq_index:

                            if parsing_valid_section:
                                self.sections.append(new_section_file)

                            head_sq_index = 0
                            header_lines = []

                            new_section_file = SectionFile(
                                path= self.dir_master_sections.joinpath(
                                    section_number_str + "__" + section_description + "." + self.filetype
                                ),
                                section_number= section_number,
                                section_description= section_description,
                                master_file= self
                            )
                            parsing_valid_section = True
                            section_lines = []

                    else:
                        head_sq_index = 0
                        index_char = len(line)

                if not parsing_header:
                    header_lines = []

                if header_parse_success:
                    parsing_header = True
                    header_lines.append(line.strip())

                elif parsing_header:
                    if parsing_valid_section and header_lines:
                        section_lines.extend(header_lines)
                    parsing_header = False
                    header_lines = []

                elif parsing_valid_section:
                    section_lines.append(line.strip())

                if parsing_valid_section and line:
                    new_section_file.lines.extend(section_lines)
                    section_lines = []

        if parsing_valid_section:

            # If the whole file is completed and was
            # parsing a section, add those header
            # lines to that last section
            if header_lines:
                section_lines.extend(header_lines)
                new_section_file.lines.extend(header_lines)

            self.sections.append(new_section_file)

if __name__ == "__main__":

    section_header = SectionHeader(
        key_sequence= [
            "spank ",
            "numnumnum",
            "\n",
            " dobonk: ",
            "descdescdesc",
            "] browntown"
        ],
        key_number= "numnumnum",
        key_description= "descdescdesc"
    )

    temporary_file_path = pathlib.Path("test.txt").resolve()

    with open(temporary_file_path, "w") as f:

        f.write(section_header.generate_header(number= 1, description= "section one"))

        f.write("\n")

        f.write("code code\ncode section 1\n")

        f.write(section_header.generate_header(number= 2, description= "section two"))

        f.write("\n")

        f.write("code section 2\n\n\n\n\nend of section2")

        f.write("\n")
        f.write("spank ")

    mfile = MasterFile(
        path= temporary_file_path,
        dir_master_sections= pathlib.Path("temp_sections").resolve()
    )
    mfile.section_header = section_header

    if not mfile.dir_master_sections.is_dir():
        os.mkdir(mfile.dir_master_sections)

    mfile.parse()

    for section in mfile.sections:
        print(f"Section {section.section_number}, {section.section_description}")
        for line in section.lines:
            print(f"\t{line}")

        with open(section.path, "w") as f:
            for line_number, line in enumerate(section.lines):
                if line_number < len(section.lines) - 1:
                    f.write(line + "\n")
                else:
                    f.write(line)