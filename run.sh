#!/bin/bash

# this scripts does the two conversions in a pipeline converts first xml->json->txt
# all input/output parameters are taken from src/config.txt

python -m req_extract.xml2json
python -m req_extract.json2json
