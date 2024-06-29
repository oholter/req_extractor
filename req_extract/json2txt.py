import json
import re
import logging
from configparser import ConfigParser
from collections import defaultdict
import spacy

logging.basicConfig(format="%(lineno)s::%(funcName)s::%(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Json2txt:
    def __init__(self, cfg):
        self.input = cfg.get("json2txt", "input")
        self.output = cfg.get("json2txt", "output")
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


        try:
            self.data = self.open_file()
        except FileNotFoundError as e:
            logger.errro(e)
            logger.error("exiting")
            exit()

        self.parsed_data = []

    def open_file(self):
        with open(self.input, "r") as F:
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



    def create_text_file(self):
        doc_code, doc_ed, doc_name = self.get_metadata()

        data = self.parse_data()
        with open(self.output, "w") as F:
            for element in data:
                if '#text' in element and (not self.only_shall_req or 'shall' in element['#text']):
                    if not self.include_top_level_sentences \
                       and '@num' in element  \
                       and len(element['@num']) == 1:
                        continue
                    else:
                        text = element['#text']
                        text = text.replace("\n", " ")
                        text = re.sub("\\s+", " ", text)
                        doc = self.nlp(text)
                        chunks = {tok.text.lower() for tok in doc.noun_chunks}
                        if self.cat_chunks:
                            chunks = ". ".join(chunks)
                            chunks += ". "
                        for i, sent in enumerate(doc.sents):
                            if not self.only_shall_sentence or 'shall' in sent.text:
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
                                                F.write("# @h{}: {}\n".format(h, p))
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
                                            F.write("# {} {}\n".format(key, val))
                                        else:
                                            F.write("# @{} {}\n".format(key, val))
                                if title:
                                    header_paths += title + ". "
                                F.write("# @snr {}\n".format(i))
                                final_sentence = sent.text
                                if self.doc_name_in_metadata:
                                    F.write("# @document {}\n".format(doc_code))
                                if self.title_in_metadata:
                                    F.write("# @doctitle {}\n".format(doc_name))
                                if self.edition_in_metadata:
                                    F.write("# @edition {}\n".format(doc_ed))
                                if self.original_sentence:
                                    F.write("# @org {}\n".format(sent.text))
                                if self.headers_in_metadata :
                                    h_titles = re.sub("\\ \.", "", header_paths).strip()
                                    h_titles = re.sub("\\. ", "->", h_titles)
                                    h_titles = re.sub("->$", "", h_titles)
                                    h_titles = re.sub("\\.$", "", h_titles)
                                    F.write("# @headers {}\n".format(h_titles))
                                if self.header_numbers_in_metadata:
                                    header_n = re.sub("->$", "", n_header_paths)
                                    F.write("# @headernr {}\n".format(header_n))
                                if self.cat_chunks:
                                    final_sentence = chunks + final_sentence
                                if self.concatinate_headers:
                                    final_sentence = header_paths + final_sentence

                                if self.token_numbers:
                                    tok_with_num = [(tok, tok.i) for tok in self.nlp(final_sentence)]
                                    for tok, num in tok_with_num:
                                        F.write("# @tok {}: {}\n".format(num, tok.text))
                                if self.chunk_numbers:
                                    chunk_with_num = [(chunk, chunk.start, chunk.end) for chunk in self.nlp(final_sentence).noun_chunks]
                                    for chunk, start, end in chunk_with_num:
                                        F.write("# @chunk {}: {}-{}\n".format(chunk.text, start, end))


                                F.write(final_sentence)
                                F.write("\n\n")

        print("Finished printing data to file: {}".format(self.output))

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
                            logger.debug("unexpected type of value")
                            logger.debug("type: {}, value: {}".format(type(value), data))
                            #logger.debug("value: {}".format(value))
                            logger.error("This should not pass, raise Exception")
                            raise Exception()

                elif type(value) == dict: # a single object
                    #logger.debug("key: {}".format(key))
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
                    logger.debug("unexpected type of value")
                    logger.debug("type: {}, value: {}".format(type(value), data))
                    #logger.debug("value: {}".format(value))
                    logger.error("This should not pass, raise Exception")
                    raise Exception()

            new_object['@hpath'] = h_path
            new_object['@npath'] = n_path
            root.append(new_object)

        else:
            logger.debug("type: {}, data: {}".format(type(data), data))
            #logger.debug("data[element]: {}".format(data[element]))
            logger.error("This should not pass, raise Exception")
            raise Exception()



def main():
    cfg = ConfigParser()
    cfg.read("./req_extract/config.cfg")

    json2txt = Json2txt(cfg)
    json2txt.parse_data()
    json2txt.create_text_file()


if __name__ == "__main__":
    main()
