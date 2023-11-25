from enum import Enum, auto as enum_auto

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
# section_number     : 1
# section_description: HeaderStructClass
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~-

class SectionHeader:

    def __init__(
        self,
        key_sequence : [list[str]],
        key_number : str,
        key_description : str
    ) -> None:

        self.key_sequence = key_sequence
        self.key_number = key_number
        self.key_description = key_description

    def generate_empty_header(self) -> str:
        return ''.join(s for s in self.key_sequence)

    def generate_header(self, number : int, description : str) -> str:

        new_header = self.generate_empty_header()

        while self.key_number in new_header:
            new_header = new_header.replace(self.key_number, str(number))

        while self.key_description in new_header:
            new_header = new_header.replace(self.key_description, description)

        return new_header


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
# section_number     : 2
# section_description: Main
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~-

if __name__ == "__main__":

    class HeaderElement(Enum):
        HEADER_START = "//" + "~"*70 + "+"
        HEADER_END = "//" + "~"*70 + "-"
        COMMENT_DECLARATION = "//"
        SECTION_NUMBER = "_value_{section number}"
        SECTION_DESCRIPTION = "_value_{section description}"
        SECTION_NUMBER_DESIGNATOR = "section_number     :"
        SECTION_DESCRIPTION_DESIGNATOR = "section_description:"

    standard_header_sequence = (
        HeaderElement.HEADER_START.value,
        "\n",
        HeaderElement.COMMENT_DECLARATION.value,
        " ",
        HeaderElement.SECTION_NUMBER_DESIGNATOR.value,
        " ",
        HeaderElement.SECTION_NUMBER.value,
        "\n",
        HeaderElement.COMMENT_DECLARATION.value,
        " ",
        HeaderElement.SECTION_DESCRIPTION_DESIGNATOR.value,
        " ",
        HeaderElement.SECTION_DESCRIPTION.value,
        "\n",
        HeaderElement.HEADER_END.value
    )

    section_header = SectionHeader(
        key_sequence= standard_header_sequence,
        key_number= HeaderElement.SECTION_NUMBER.value,
        key_description= HeaderElement.SECTION_DESCRIPTION.value
    )

    print("Standard header printout:\n")

    print(section_header.generate_empty_header())

    print("\nHeader for examples:\n")

    print(section_header.generate_header(number= 1, description= "testing yo"))

    print(section_header.generate_header(number= 3, description= "anotha one"))
