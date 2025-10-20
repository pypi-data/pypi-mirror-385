
from .code_ import Code
from .nextflow_building_blocks import Nextflow_Building_Blocks



class Function(Nextflow_Building_Blocks):
    def __init__(self, code, name, origin):
        self.origin = origin
        self.code = Code(code, origin = self, initialise=False)
        self.name = name
        self.alias = name

    def set_alias(self, alias):
        self.alias = alias

    def get_alias(self):
        return self.alias
    
    def get_alias_and_id(self):
        return f"{self.alias}_GG_{id(self)}"

    def get_type(self):
        return "Function"

    def get_name(self):
        return self.name
    
    def add_2_rocrate(self, dico, parent_key):
        None
    
    

