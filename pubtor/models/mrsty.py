from dataclasses import dataclass

@dataclass
class MRSTY:
    """Class for keeping track of MRSTY objects"""
    cui: str
    tui: str
    stn: str
    sty: str
    atui: str
    cvf: str
    dummy: str

    @classmethod
    def from_row(cls, row):
        return cls(*row)