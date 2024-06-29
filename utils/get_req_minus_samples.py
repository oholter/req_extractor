import logging
from sklearn.model_selection import train_test_split
import random
import json
from argparse import ArgumentParser
from configparser import ConfigParser
from pathlib import Path

SEED = 42

random.seed(SEED)

def find_unused_samples(doc, samples):
    print("Total length doc: {}".format(len(doc)))
    unused_samples = []
    num_equal = 0
    for d in doc:
        found = False
        for s in samples:
            if d['meta']['org'] == s['meta']['org']:
                num_equal += 1
                found = True
                break
        if found:
            continue
        else:
            unused_samples.append(d)

    print("Removed {} samples".format(num_equal))
    print("Final length: {}".format(len(unused_samples)))
    return unused_samples


def read_file(p):
    data = None
    with p.open(mode='r') as F:
        data = json.load(F)

    return data


def write_json(samples, filename, out_dir):
    out_file = out_dir / (filename + "_" + str(len(samples)) + "_samples" + ".json")
    with out_file.open(mode='w') as F:
        json.dump(samples, F, indent=4)
        print("written {} samples to {}".format(len(samples), out_file))


def main():
    logging.basicConfig(format="%(lineno)s::%(funcName)s::%(message)s",
                        level=logging.DEBUG)

    parser = ArgumentParser()
    parser.add_argument("doc", help=".json requirements file")
    parser.add_argument("samples", help=".json file with samples")
    parser.add_argument("output", help="output dir")
    args = parser.parse_args()

    doc_path = Path(args.doc)
    samples_path = Path(args.samples)
    output_path = Path(args.output)

    if doc_path.suffix != ".json":
        print("wrong requriements file format")
        exit()

    if samples_path.suffix != ".json":
        print("wrong requriements file format")
        exit()

    if not doc_path.exists():
        print("{} does not exist exiting".format(doc_path))
        exit()

    if not samples_path.exists():
        print("{} does not exist exiting".format(samples_path))
        exit()

    doc = read_file(doc_path)
    samples = read_file(samples_path)

    unused_samples = find_unused_samples(doc, samples)

    write_json(unused_samples, doc_path.stem, output_path)



if __name__ == '__main__':
    main()
