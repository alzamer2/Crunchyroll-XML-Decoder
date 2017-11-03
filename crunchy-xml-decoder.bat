@echo off
set PYTHONHTTPSVERIFY=0 
RD "%PUBLIC%\Crunchyroll-XML-Decoder_link" 1>NUL 2>NUL
mklink /j "%PUBLIC%\Crunchyroll-XML-Decoder_link" %cd% 1>NUL 2>NUL
rem cd "%PUBLIC%\Crunchyroll-XML-Decoder_link"
:sratre
crunchy-xml-decoder.py %*
RD "%PUBLIC%\Crunchyroll-XML-Decoder_link" 1>NUL 2>NUL
rem pause

