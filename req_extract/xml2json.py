import xmltodict
from xml.parsers.expat import ExpatError
import json
from configparser import ConfigParser
from argparse import ArgumentParser
from pathlib import Path


def read_data(p):
    data = None
    with p.open(mode='r') as F:
        xml = F.read()
        F.close()
        try:
            data = xmltodict.parse(xml)
        except ExpatError as e:
            print("Unable to parse {}".format(p))
            print(e)
            exit()
    return data

def write_json(data, p, out_dir):
    output_file = out_dir / (p + ".json")
    with output_file.open(mode="w") as F:
        json.dump(data, F, indent=4)
        print("data written to {}".format(output_file))


def main():
    cfg = ConfigParser()
    cfg.read("./req_extract/config.cfg")
    parser = ArgumentParser()
    parser.add_argument("input", help=".xml file or directory with xml-files ")
    args = parser.parse_args()

    in_p = Path(args.input)
    out_dir = Path(cfg.get("xml2json", "output_dir"))

    if not out_dir.exists():
        print("output dir: {} does not exists, exiting ...".format(out_dir))
        exit()

    if not in_p.exists():
        print("{} does not exists, exiting ...".format(in_p))
        exit()

    # in_p is a dir
    if in_p.is_dir():
        for e in in_p.iterdir():
            if e.is_file() and e.suffix == ".xml":
                data = read_data(e)
                write_json(data, e.stem, out_dir)


    elif in_p.is_file():
        data = read_data(in_p)
        write_json(data, in_p.stem, out_dir)


if __name__ == "__main__":
    main()
