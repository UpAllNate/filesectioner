from __future__ import annotations

import pathlib
import os

from header import SectionHeader
from icecream import ic

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
    def __init__(self, path : pathlib.Path) -> None:

        super().__init__(path)
        self.dir_master_sections = path.parent.resolve().joinpath("sections").joinpath(self.filename)
        self.sections : list[SectionFile] = []
        self.section_header : SectionHeader = None

class HeaderSpecifier:

    def __init__(
            self,
            header_start_line,
            header_end_line,
            section_number,
            section_description
        ) -> None:

        self.header_start_line = header_start_line
        self.header_end_line = header_end_line
        self.code_start_line = None
        self.code_end_line = None
        self.section_number = section_number
        self.section_description = section_description

def parse_master_file_headers(master_file : MasterFile) -> list[HeaderSpecifier]:

    # The header sequence specifies the position
    # in standard_header_sequence that is being
    # parsed for

    last_head_sq_index = len(master_file.section_header.key_sequence) - 1

    head_sq_index = 0
    parsing_header = False
    header_lines : list[str] = []
    return_header_specifiers : list[HeaderSpecifier] = []
    new_header_specifier = None

    section_number = None
    section_description = None

    # ic("Parsing master file", master_file.filename)

    try:
        with open(master_file.path, "r") as f:

            for line_num, line in enumerate(f):
                line : str

                # ic("evaluating line\n", line)

                index_char = 0

                # Parse the entire line, which could contain
                # several header sequence elements
                while index_char < len(line):
                    # ic(head_sq_index)
                    current_header_sequence_string = master_file.section_header.key_sequence[head_sq_index]
                    test_string = line[index_char : index_char + len(current_header_sequence_string)]
                    header_sequence_match = test_string == current_header_sequence_string
                    pulse_last_head_sq_index = last_head_sq_index == head_sq_index
                    header_parse_success = False

                    # ic(current_header_sequence_string, test_string, header_sequence_match, pulse_last_head_sq_index)

                    # Header text match
                    if header_sequence_match:
                        index_char += len(master_file.section_header.key_sequence[head_sq_index])
                        header_parse_success = True

                    # Header sequence number
                    if current_header_sequence_string == master_file.section_header.key_number:

                        parse_key = False

                        # Get the section number as string
                        if pulse_last_head_sq_index:
                            section_number_str = line[index_char:].strip()
                            parse_key = True

                        else:
                            next_test_string = master_file.section_header.key_sequence[head_sq_index + 1]
                            try:
                                next_test_string_index = line[index_char:].index(next_test_string)
                            except:
                                pass
                            else:
                                section_number_str = line[index_char:][:next_test_string_index].strip()
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
                    if current_header_sequence_string == master_file.section_header.key_description:

                        # Get the section number as string
                        if pulse_last_head_sq_index:
                            section_description = line[index_char:].strip()
                            header_parse_success = True

                        else:
                            next_test_string = master_file.section_header.key_sequence[head_sq_index + 1]
                            try:
                                next_test_string_index = line[index_char:].index(next_test_string)
                            except:
                                pass
                            else:
                                section_description = line[index_char:][:next_test_string_index].strip()
                                header_parse_success = True
                                index_char += len(section_description)

                    # Increment header sequence index
                    # or reset if header parsing failure
                    if header_parse_success:
                        head_sq_index += 1
                        if pulse_last_head_sq_index:

                            head_sq_index = 0
                            index_char = len(line)

                            header_lines.append(line)

                            # ic("header complete", line_num, header_lines)
                            new_header_specifier = HeaderSpecifier(
                                header_start_line= line_num - len(header_lines) + 1,
                                header_end_line= line_num,
                                section_description= section_description,
                                section_number= section_number
                            )

                    else:
                        # ic("just a regular line", line)
                        head_sq_index = 0
                        index_char = len(line)

                        if new_header_specifier is not None:
                            # ic("parsing when code starts and ends...")

                            if line.strip() and new_header_specifier.code_start_line is None:
                                new_header_specifier.code_start_line = line_num
                                # ic(new_header_specifier.code_start_line)

                            if line.strip():
                                new_header_specifier.code_end_line = line_num
                                # ic(new_header_specifier.code_end_line)

                if not parsing_header:
                    header_lines = []

                if header_parse_success and not pulse_last_head_sq_index:
                    parsing_header = True
                    header_lines.append(line.strip())
                    # ic("Header parse success",header_lines)

                elif parsing_header:

                    parsing_header = False
                    header_lines = []

            if new_header_specifier is not None:
                return_header_specifiers.append(new_header_specifier)

    except PermissionError:
        pass

    return return_header_specifiers

if __name__ == "__main__":

    section_header = SectionHeader(
        key_sequence= [
            "numnumnum",
            " ",
            "numnumnum",
            " ",
            "numnumnum",
            " ",
            "numnumnum",
            " ",
            "spank ",
            "numnumnum",
            "\n",
            " dobonk: ",
            "descdescdesc",
            "\n",
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