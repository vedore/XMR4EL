from dataclasses import dataclass

@dataclass
class MRDEF:
    """Class for keeping track of MRDEF objects"""
    cui: str
    aui: str
    atui: str
    satui: str
    sab: str
    definition: str
    suppress: str
    cvf: str
    dummy: str

    @classmethod
    def from_row(cls, row):
        return cls(*row)