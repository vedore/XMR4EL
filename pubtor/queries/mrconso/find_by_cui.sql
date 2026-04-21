SELECT
    CUI,
    LAT,
    TS,
    LUI,
    STT,
    SUI,
    ISPREF,
    AUI,
    SAUI,
    SCUI,
    SDUI,
    SAB,
    TTY,
    CODE,
    STR,
    SRL,
    SUPPRESS,
    CVF,
    DUMMY
FROM MRCONSO
WHERE CUI = %s
ORDER BY ISPREF DESC, SAB, TTY, STR;