from dataclasses import dataclass

@dataclass
class MRREL:
    """Class for keeping track of MRREL objects"""
    cui1: str
    aui1: str
    stype1: str
    rel: str
    cui2: str
    aui2: str
    stype2: str
    rela: str
    rui: str
    srui: str
    sab: str
    sl: str
    rg: str
    direction: str
    suppress: str
    cvf: str
    dummy: str

    @classmethod
    def from_row(cls, row):
        return cls(*row)