import os
import shutil
import pathlib
import copy

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create /sections/ and delete all section files
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Directory path containing the text files
dir_sections = "./sections/"

# Check whether the specified path exists or not
if os.path.exists(dir_sections):
   shutil.rmtree(dir_sections)

os.mkdir(dir_sections)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define the standard section header format
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

standard_header = "{comment declaration} Section: {section number},\n'{section description}'"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Headers will be generated using search and replace
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Dummy:
    def __init__(self, var) -> None:
        self.var = var

COMMENT_DECLARATION = "//"
section_number = Dummy(var = 0)
section_description = Dummy(var = "trunk")

header_lookups = {
    "{section number}" : section_number,
    "{section description}" : section_description
}

def generate_section_header(number : int, description : str) -> str:
    global section_number
    global section_description
    global header_lookups

    section_number.var = number
    section_description.var = description

    new_header = copy.deepcopy(standard_header)

    for replace_key in header_lookups.keys():
        while replace_key in new_header:
            new_header = new_header.replace(replace_key, str(header_lookups[replace_key].var))
    
    return new_header

print(generate_section_header(number= 4, description= "test section"))
exit()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Parsing headers will 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MonitoredFile:
    
    def __init__(self, filename : str) -> None:
        self.dir : pathlib.Path = None
        self.filename : str = filename
        self.prev_mod_time = self.get_mod_time()
        self.pulse_file_changed : bool = False

    def get_mod_time(self) -> float:
        try:
            return os.stat(self.filename).st_mtime
        except:
            print(f"Couldn't get modified time. Was the file {self.filename} deleted??")
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

    def __init__(self, filename: str, section_number: int, section_name: str, master_name: str) -> None:
        super().__init__(filename)
        self.section_number = section_number
        self.section_name = section_name
        self.master_name = master_name
    
class MasterFile(MonitoredFile):

    def __init__(self, filename: str) -> None:
        super().__init__(filename)
        self.sections : list[SectionFile] = []

dir_this_file_parent = pathlib.Path(__file__).parent.resolve()
dir_this_file = pathlib.Path(__file__).resolve()

for filename in os.listdir(dir_this_file_parent):
    file_resolved = pathlib.Path.joinpath(dir_this_file_parent, filename).resolve()

    # every file that isn't THIS python program is a potential managed file
    if not file_resolved == dir_this_file:


        pass
