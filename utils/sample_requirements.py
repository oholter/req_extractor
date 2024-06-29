import logging
from sklearn.model_selection import train_test_split
import random
import json
from argparse import ArgumentParser
from configparser import ConfigParser
from pathlib import Path

SEED = 42

random.seed(SEED)


def read_file(p):
    data = None
    with p.open(mode='r') as F:
        data = json.load(F)

    return data


# old - not in use
def sample_data2(data, n):
    if n > len(data):
        logging.warning("Cannot sample %d from a dataset with size %d ... using all",
                        n, len(data))
    samples = random.sample(data, min(len(data), n))
    return samples

def sample_data(data, n):
    train_frac = n / len(data)
    print(train_frac)
    return train_test_split(data, train_size=train_frac, shuffle=True)


def write_json(samples, filename, out_dir):
    out_file = out_dir / (filename + "_" + str(len(samples)) + "_samples" + ".json")
    with out_file.open(mode='w') as F:
        json.dump(samples, F, indent=4)
        print("written {} samples to {}".format(len(samples), out_file))


def main():
    logging.basicConfig(format="%(lineno)s::%(funcName)s::%(message)s",
                        level=logging.DEBUG)

    parser = ArgumentParser()
    parser.add_argument("input", help=".json file input")
    parser.add_argument("--number", "-n", help="number of samples",
                        type=int, default=100)
    args = parser.parse_args()

    cfg = ConfigParser()
    cfg.read("./src/config.txt")

    input_path = Path(args.input)
    output_dir = Path(cfg.get("sample_req", "output_dir"))

    if not input_path.exists():
        print("{} does not exist exiting".format(input_path))

    if input_path.is_file() and input_path.suffix == ".json":
        data = read_file(input_path)
        samples = sample_data(data, args.number)
        write_json(samples, input_path.stem, output_dir)

    elif input_path.is_dir():
        for e in input_path.iterdir():
            if e.suffix == ".json":
                data = read_file(e)
                train_samples, test_samples = sample_data(data, args.number)
                write_json(train_samples, e.stem, output_dir)
                write_json(test_samples, e.stem, output_dir)


if __name__ == '__main__':
    main()
