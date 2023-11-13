import os
from typing import List, Tuple





class SectionFile():

    def __init__(self, filename : str = None, filenumber : int = None, sectionname : str = None, programname : str = None) -> None:
        self.filename : str = filename
        self.filenumber = filenumber
        self.sectionname : str = sectionname
        self.programname : str = programname
        self.lines : List[str] = []
        self.vol_lines : List[str] = []

    def __str__(self) -> str:
        return f"{self.filename}, part: {self.filenumber}, section: {self.sectionname}, program: {self.programname}, length: {len(self.lines)}"

