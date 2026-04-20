SELECT
    cui, lat, ts, lui, stt, sui, ispref, aui, saui, scui,
    sdui, sab, tty, code, str, srl, suppress, cvf, dummy
FROM mrconso
WHERE cui = %s;