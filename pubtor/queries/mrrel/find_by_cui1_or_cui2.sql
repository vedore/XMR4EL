SELECT
    CUI1,
    AUI1,
    STYPE1,
    REL,
    CUI2,
    AUI2,
    STYPE2,
    RELA,
    RUI,
    SRUI,
    SAB,
    SL,
    RG,
    DIR,
    SUPPRESS,
    CVF,
    DUMMY
FROM MRREL
WHERE CUI1 = %s OR CUI2 = %s
ORDER BY SAB, REL, RELA, CUI1, CUI2;