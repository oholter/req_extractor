import random
import json
from argparse import ArgumentParser
from pathlib import Path


SEED = 42

random.seed(SEED)

def get_json_data_from_path(path):
    with path.open(mode="r") as F:
        data = json.load(F)
    return data


def write_json_data_to_disk(data, path):
    out_file = Path(path.parent / (path.stem + "_shuffled" + ".json"))
    with out_file.open(mode='w') as F:
        json.dump(data, F, indent=4)
        print("Written shuffled data to: {}".format(out_file))


def main():
    parser = ArgumentParser()
    parser.add_argument("input", help="input .json file")
    args = parser.parse_args()
    in_path = Path(args.input)

    if not in_path.exists() or not in_path.is_file():
        print("Could not find file {}, exiting ...".format(in_path))
        exit()

    data = get_json_data_from_path(in_path)
    random.shuffle(data)
    write_json_data_to_disk(data, in_path)



if __name__ == '__main__':
    main()
