import json
import math
from pathlib import Path
from argparse import ArgumentParser

def get_json_data_from_path(path):
    with path.open(mode="r") as F:
        data = json.load(F)
    return data


def write_json_data_to_disk(data, path, num):
    out_file = Path(path.parent / (path.stem + "_{}".format(num) + ".json"))
    with out_file.open(mode='w') as F:
        json.dump(data, F, indent=4)
        print("Written {} items to: {}".format(len(data), out_file))


def main():
    parser = ArgumentParser()
    parser.add_argument("input", help="input .json file")
    parser.add_argument("-n", help="number of req per file",
                        default=21, type=int)
    args = parser.parse_args()
    in_path = Path(args.input)

    if not in_path.exists() or not in_path.is_file():
        print("Could not find file {}, exiting ...".format(in_path))
        exit()

    if args.n <= 0:
        print("Expected n > 0, exiting ...")
        exit()

    data = get_json_data_from_path(in_path)
    #sents_per_doc = math.ceil(len(data) / args.n)

    #current = 0
    #for n in range(args.n):
        #slice = data[current:current + sents_per_doc]
        #write_json_data_to_disk(slice, in_path, n)
        #current = current + sents_per_doc

    current = 0
    num = 0
    while current < len(data):
        next = min(current+args.n, len(data))
        slice = data[current:next]
        write_json_data_to_disk(slice, in_path, num)
        num += 1
        current = next




if __name__ == '__main__':
    main()
