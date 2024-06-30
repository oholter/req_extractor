import json
from pathlib import Path
from argparse import ArgumentParser

def read_file(path):
    """ read normal .json """
    with path.open(mode='r') as F:
        data = json.load(F)
        print("Read {} documents from {}".format(len(data), path))
    return data

def write_file(data, path):
    with path.open(mode='w') as F:
        for d in data:
            json.dump(d, F)
            F.write("\n")
        print("Written {} documents to {}".format(len(data), path))


def main():
    parser = ArgumentParser()
    parser.add_argument("input", help="input .json file or dir")
    args = parser.parse_args()

    path = Path(args.input)

    if path.is_file():
        data = read_file(path)
        out_path = path.parent / (path.stem + ".jsonl")
        write_file(data, out_path)

    if path.is_dir():
        for file in path.iterdir():
            if file.suffix == ".json":
                data = read_file(file)
                out_path = file.parent / (file.stem + ".jsonl")
                write_file(data, out_path)







if __name__ == '__main__':
    main()


