import os
import shutil
import pathlib

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create /sections/ and delete all section files
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Directory path containing the text files
dir_sections = "./sections/"

# Check whether the specified path exists or not
if os.path.exists(dir_sections):
   shutil.rmtree(dir_sections)

os.mkdir(dir_sections)

class MonitoredFile:
    
    def __init__(self, filename : str) -> None:
        self.dir : pathlib.Path = 
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
    print(f"file: {filename}, resolved: {file_resolved}, __file__: {dir_this_file}, this: {file_resolved == dir_this_file}")


