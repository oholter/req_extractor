#!/bin/bash

# this scripts does the two conversions in a pipeline converts first xml->json->txt
# all input/output parameters are taken from src/config.txt

python -m src.xml2json
#python -m src.json2txt
python -m src.json2json
