from dataclasses import dataclass

@dataclass
class MRCONSO:
    """Class for keeping track of MRCONSO objects"""
    cui: str
    lat: str
    ts: str
    lui: str
    stt: str
    sui: str
    ispref: str
    aui: str
    saui: str
    scui: str
    sdui: str
    sab: str
    tty: str
    code: str
    string: str
    srl: str
    suppress: str
    cvf: str
    dummy: str

    @classmethod
    def from_row(cls, row):
        return cls(*row)