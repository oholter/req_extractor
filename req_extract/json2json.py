import json
from pathlib import Path
from tqdm import tqdm
import re
import logging
from configparser import ConfigParser
from argparse import ArgumentParser
import spacy


class Json2txt:
    def __init__(self, cfg, input_file):
        #self.input = cfg.get("json2json", "input")
        self.input_file = input_file
        self.output_dir = Path(cfg.get("json2json", "output_dir"))
        self.only_shall_req = cfg.getboolean("json2txt", "only_shall_req")
        self.only_shall_sentence = cfg.getboolean("json2txt", "only_shall_sentence")
        self.concatinate_headers = cfg.getboolean("json2txt", "concatinate_headers")
        self.include_top_level_sentences = cfg.getboolean("json2txt", "include_top_level_sentences")
        self.cat_chunks = cfg.getboolean("json2txt", "concatinate_surrounding_chunks")
        self.token_numbers = cfg.getboolean("json2txt", "token_numbers")
        self.original_sentence = cfg.getboolean("json2txt", "original_sentence")
        self.chunk_numbers = cfg.getboolean("json2txt", "chunk_numbers")
        self.ignore_tables = cfg.getboolean("json2txt", "ignore_tables")
        self.headers_in_metadata = cfg.getboolean("json2txt", "headers_in_metadata")
        self.doc_name_in_metadata = cfg.getboolean("json2txt", "doc_name_in_metadata")
        self.title_in_metadata = cfg.getboolean("json2txt", "title_in_metadata")
        self.edition_in_metadata = cfg.getboolean("json2txt", "edition_in_metadata")
        self.header_numbers_in_metadata = cfg.getboolean("json2txt", "header_numbers_in_metadata")
        self.nlp = spacy.load("en_core_web_sm")

        if not self.output_dir.exists():
            print("\"{}\" does not exist, exiting ...".format(self.output_dir))
            exit()

        try:
            self.data = self.open_file(self.input_file)
        except FileNotFoundError as e:
            logging.error(e)
            logging.error("exiting")
            exit()

        self.parsed_data = []

    def open_file(self, p):
        with p.open(mode="r") as F:
            data = json.load(F)
        return data


    def get_metadata(self):
        doc = self.data['document']
        if '@theme' in doc:
            title = doc['@theme']
        else:
            title = "unknown"
        if '@title' in doc:
            code = doc['@title']
        else:
            code = "unknown"
        if '@edition' in doc:
            ed = doc['@edition']
        else:
            ed = "unknown"

        return code, ed, title



    def create_json_file(self):
        doc_code, doc_ed, doc_name = self.get_metadata()

        data = self.parse_data()
        json_objects = []
        # for each data element
        for element in tqdm(data):
            # ignore if there is no shall in any of the sentences
            if '#text' in element and (not self.only_shall_req or 'shall' in element['#text']):
                # ignore document level text just below Part/Section
                if not self.include_top_level_sentences and '@num' in element  and len(element['@num']) == 1:
                    continue
                else:
                    text = element['#text']
                    text = text.replace("\n", " ")
                    text = re.sub("\\s+", " ", text)
                    doc = self.nlp(text)
                    chunks = {tok.text.lower() for tok in doc.noun_chunks}
                    # Adding surrounding chunks
                    if self.cat_chunks:
                        chunks = ". ".join(chunks)
                        chunks += ". "
                    # for each sentence in req
                    for i, sent in enumerate(doc.sents):
                        # ignoring non-'shall' sentences
                        if not self.only_shall_sentence or 'shall' in sent.text:
                            json_object = {}
                            json_object['meta'] = {}
                            header_paths = ""
                            n_header_paths = ""
                            title = None
                            for key, val in element.items():
                                if key.lower() == "@hpath":
                                    for h, p in enumerate(val):
                                        p = p.strip()
                                        if self.concatinate_headers:
                                            header_paths += p + ". "
                                        else:
                                            #F.write("# @h{}: {}\n".format(h, p))
                                            json_object['meta']['h{}'.format(h)] = p
                                if key.lower() == "@npath":
                                    for h, n in enumerate(val):
                                        n = n.strip()
                                        n_header_paths += n + "->"

                                if key.lower() == "@title" or key.lower() == "@theme" and self.concatinate_headers:
                                    title = val.lower() + ". "
                                if key.lower() not in ["#text", "@npath" , "@hpath", "@title"]:
                                    val = val.replace("\n", " ")
                                    val = re.sub("\\s+", " ", val)
                                    if key[0] == "@":
                                        #F.write("# {} {}\n".format(key, val))
                                        json_object['meta'][key] = val
                                    else:
                                        #F.write("# @{} {}\n".format(key, val))
                                        json_object['meta'][key] = val
                            if title:
                                header_paths += title + ". "
                            #F.write("# @snr {}\n".format(i))
                            json_object['meta']['snr'] = i
                            #final_sentence = sent.text
                            final_sentence = ""
                            if self.doc_name_in_metadata:
                                #F.write("# @document {}\n".format(doc_code))
                                json_object['meta']['document'] = doc_code
                            if self.title_in_metadata:
                                #F.write("# @doctitle {}\n".format(doc_name))
                                json_object['meta']['doctitle'] = doc_name
                            if self.edition_in_metadata:
                                #F.write("# @edition {}\n".format(doc_ed))
                                json_object['meta']['edition'] = doc_ed
                            if self.original_sentence:
                                #F.write("# @org {}\n".format(sent.text))
                                json_object['meta']['org'] = sent.text
                            if self.headers_in_metadata :
                                h_titles = re.sub("\\ \.", "", header_paths).strip()
                                h_titles = re.sub("\\. ", "->", h_titles)
                                h_titles = re.sub("->$", "", h_titles)
                                h_titles = re.sub("\\.$", "", h_titles)
                                #F.write("# @headers {}\n".format(h_titles))
                                json_object['meta']['headers'] = h_titles

                            if self.header_numbers_in_metadata:
                                header_n = re.sub("->$", "", n_header_paths)
                                #F.write("# @headernr {}\n".format(header_n))
                                json_object['meta']['headernr'] = header_n
                            if self.cat_chunks:
                                final_sentence = chunks + final_sentence
                            if self.concatinate_headers:
                                final_sentence = header_paths + final_sentence

                            if self.token_numbers:
                                tok_with_num = [(tok, tok.i) for tok in self.nlp(final_sentence)]
                                json_object['meta']['tok'] = []
                                for tok, num in tok_with_num:
                                    #F.write("# @tok {}: {}\n".format(num, tok.text))
                                    json_object['meta']['tok'].append(tok.text)
                            if self.chunk_numbers:
                                chunk_with_num = [(chunk, chunk.start, chunk.end) for chunk in self.nlp(final_sentence).noun_chunks]
                                json_object['meta']['chunk'] = []
                                for chunk, start, end in chunk_with_num:
                                    #F.write("# @chunk {}: {}-{}\n".format(chunk.text, start, end))
                                    json_object['meta']['chunk'].append("{}: {}-{}".format(chunk.text, start, end))

                            final_sentence = sent.text + " " + final_sentence.strip()
                            json_object['text'] = final_sentence
                            if len(final_sentence.split()) <= 512:
                                json_objects.append(json_object)
                            else:
                                logging.warning("Ignoring sent: \"%s\" ... too long...", final_sentence[:50])

        with open(self.output_dir / self.input_file.name, "w") as F:
            json.dump(json_objects, F, indent=4)

        print("Finished printing data to file: {}".format(self.output_dir / self.input_file.name))

    def parse_data(self):
        """
        Calls the recursive function parse_section
        Returns a "flat list of text elements" on the form
        [
          {
             @num: 10.2,
             @hpath: ['drilling facilities', 'certification and classification'],
             @npath: ['1', '3'],
             @theme: ['drilling facilities'],
             @title: ['Documentation requirements'],
             #text: 'See applicable parts of Ch 3 Sec 2.'
          },
          ...
        ]

        """
        if not self.parsed_data:
            self.parse_section(self.data, h_path=None, n_path=None, root=self.parsed_data)
        return self.parsed_data

    def parse_section(self, data, h_path, n_path, root):
        """ each element contains
        1) a list of metadata
        2) one or multiple sentences
        """

        if not h_path:
            h_path = []

        if not n_path:
            n_path = []


        if type(data) == dict:
            new_object = {}
            for key, value in data.items():
                if self.ignore_tables and key == 'table':
                    continue
                if type(value) == str: # end of recursion
                    new_object[key] = value
                elif type(value) == list: # a list of objects
                    for subelement in value:
                        if type(subelement) == str: # multi sentence element
                            new_object[key] = subelement # terminate rec
                        elif type(subelement) == dict: # new object - must add possible title to h_path
                            if '@theme' in data:
                                if '@num' in data:
                                    self.parse_section(subelement, h_path + [data['@theme'].lower()], n_path + [data['@num']], root)
                                else:
                                    self.parse_section(subelement, h_path + [data['@theme'].lower()], n_path, root)
                            elif '@title' in data:
                                if '@num' in data:
                                    self.parse_section(subelement, h_path + [data['@title'].lower()], n_path + [data['@num']], root)
                                else:
                                    self.parse_section(subelement, h_path + [data['@title'].lower()], n_path, root)
                            else:
                                self.parse_section(subelement, h_path, n_path, root)
                        else:
                            logging.debug("unexpected type of value")
                            logging.debug("type: {}, value: {}".format(type(value), data))
                            #logging.debug("value: {}".format(value))
                            logging.error("This should not pass, raise Exception")
                            raise Exception()

                elif type(value) == dict: # a single object
                    #logging.debug("key: {}".format(key))
                    if '@theme' in data:
                        if '@num' in data:
                            self.parse_section(value, h_path + [data['@theme'].lower()], n_path + [data['@num']], root)
                        else:
                            self.parse_section(value, h_path + [data['@theme'].lower()], n_path, root)
                    elif '@title' in data:
                        if '@num' in data:
                            self.parse_section(value, h_path + [data['@title'].lower()], n_path + [data['@num']], root)
                        else:
                            self.parse_section(value, h_path + [data['@title'].lower()], n_path, root)
                    else:
                        self.parse_section(value, h_path, n_path, root)
                else:
                    logging.debug("unexpected type of value")
                    logging.debug("type: {}, value: {}".format(type(value), data))
                    #logging.debug("value: {}".format(value))
                    logging.error("This should not pass, raise Exception")
                    raise Exception()

            new_object['@hpath'] = h_path
            new_object['@npath'] = n_path
            root.append(new_object)

        else:
            logging.debug("type: {}, data: {}".format(type(data), data))
            #logging.debug("data[element]: {}".format(data[element]))
            logging.error("This should not pass, raise Exception")
            raise Exception()



def main():
    logging.basicConfig(format="%(lineno)s::%(funcName)s::%(message)s", level=logging.DEBUG)
    cfg = ConfigParser()
    cfg.read("./req_extract/config.cfg")
    parser = ArgumentParser()
    parser.add_argument("in_p", help="input .json file or dir with .json files")
    args = parser.parse_args()

    input_path = Path(args.in_p)
    if not input_path.exists():
        print("{} does not exist, exiting ...".format(input_path))
    if input_path.is_file():
        logging.info("transforming %s", input_path)
        json2txt = Json2txt(cfg, input_path)
        json2txt.parse_data()
        json2txt.create_json_file()
    elif input_path.is_dir():
        for e in input_path.iterdir():
            if e.is_file() and e.suffix == ".json":
                logging.info("transforming %s", e)
                json2txt = Json2txt(cfg, e)
                json2txt.parse_data()
                json2txt.create_json_file()

if __name__ == "__main__":
    main()
