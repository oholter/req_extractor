from xml.dom.minidom import parse
import xml.dom.minidom
from nltk import sent_tokenize

from configparser import ConfigParser



def print_reqs(requirements, file=None, filter_shall=True):
    num_req_sents = 0
    num_shall_reqs = 0
    num_reqs = len(requirements)
    print("sec\treq\tsent_num\tsent")


    for req in requirements:
        req_num = req.getAttribute('num')
        sub1 = req.parentNode
        part = sub1.parentNode
        section = part.parentNode
        # print(req.firstChild.nodeValue)
        try:
            sents = sent_tokenize(req.firstChild.nodeValue)
        except AttributeError:
            sents = []
        try:
            section_num = section.getAttribute('num')
        except AttributeError:
            section_num = 0
        part_num = part.getAttribute('num')
        sub1_num = sub1.getAttribute('num')
        for i, sent in enumerate(sents):
            sent = sent.replace('\n', ' ')
            print("{}\t{}\t{}\t{}".format(section_num, req_num, i + 1, sent.strip()))
            num_req_sents +=1
            if ' shall ' in sent:
                num_shall_reqs += 1


    if file:
        with open(file, 'w') as F:
            F.write("sec\treq\tsent_num\tsent\n")
            for req in requirements:
                req_num = req.getAttribute('num')
                sub1 = req.parentNode
                part = sub1.parentNode
                section = part.parentNode
                try:
                    sents = sent_tokenize(req.firstChild.nodeValue)
                except AttributeError:
                    sents = []
                try:
                    section_num = section.getAttribute('num')
                except AttributeError:
                    section_num = 0
                for i, sent in enumerate(sents):
                    if not filter_shall:
                        sent = sent.replace('\n', ' ')
                        F.write("{}\t{}\t{}\t{}\n".format(section_num, req_num, i + 1, sent.strip()))
                    else:
                        sent = sent.replace('\n', ' ')
                        if ' shall ' in sent:
                            F.write("{}\t{}\t{}\t{}\n".format(section_num, req_num, i + 1, sent.strip()))



    print("\ntotal number of reqs: {}".format(num_reqs))
    print("total number of req sents: {}".format(num_req_sents))
    print("number of shall req sents: {}".format(num_shall_reqs))


def print_sub(subs, filter_shall=False):
    """Prints the selection for tsv-file split into individual sentences"""
    num_sents = 0
    num_shall_sents = 0
    num_subs = len(subs)
    print("sec\tsub\tsent_num\tsent")

    for sub in subs:
        num = sub.getAttribute('num')
        part = sub.parentNode
        section = part.parentNode
        sents = sent_tokenize(sub.firstChild.nodeValue)

        #section_num = section.getAttribute('num')
        section_num = num[0]
        for i, sent in enumerate(sents):
            num_sents += 1
            if not filter_shall:
                sent = sent.replace('\n', ' ')
                print("{}\t{}\t{}\t{}".format(section_num, num, i + 1, sent.strip()))
                if ' shall ' in sent:
                    num_shall_sents += 1

            else:
                if ' shall ' in sent:
                    num_shall_sents += 1
                    sent = sent.replace('\n', ' ')
                    print("{}\t{}\t{}\t{}".format(section_num, num, i + 1, sent.strip()))




    print("\ntotal number of subs: {}".format(num_subs))
    print("total number of sents: {}".format(num_sents))
    print("number of shall sents: {}".format(num_shall_sents))


def print_selection(subs, out_file):
    """print the chosen with number without breaking into individual sentences"""

    with open(out_file, "w") as F:
        for sub in subs:
            # Concat titles
            titles = []
            parent = sub.parentNode
            try:
                while parent is not None:
                    titles.append(parent.getAttribute("title"))
                    #print(parent.getAttribute("title"))
                    parent = parent.parentNode
            except(AttributeError):  # I have no idea how to check if an element is Document, so exception is normal behavior
                pass
                #print("stopp")

            titles.reverse()
            titles = ", ".join(titles)
            titles += ". "
            #print(titles)
            num = sub.getAttribute("num")
            req = str(sub.firstChild.nodeValue)
            req = req.replace("\n", " ")
            #print("{}: {} {}".format(num, titles, req))
            F.write("{}: {} {}\n".format(num, titles, req))




if __name__ == "__main__":
    config_path = "./req_extract/config.cfg"
    cfg = ConfigParser()
    cfg.read(config_path)

    #path = "xml/dnvgl-st-f101.xml"
    path = cfg.get("parsexml", "input")
    out = cfg.get("parsexml", "output")
    #tsv_path = "tsv/DNVGL-RU-FD.tsv"


    DOMTree = xml.dom.minidom.parse(path)
    collection = DOMTree.documentElement
    if collection.hasAttribute('document'):
        print('root element has: '.format(collection.getAttribute('document')))

    requirements = collection.getElementsByTagName("req")
    sub2 = collection.getElementsByTagName("sub2")
    sub1 = collection.getElementsByTagName("sub1")
    part = collection.getElementsByTagName("part")
    sec = collection.getElementsByTagName("section")


    #print_reqs(requirements, file=tsv_path, filter_shall=True)
    #print_sub(sub1, filter_shall=True)
    #print_sub(requirements, filter_shall=True)

    print_selection(requirements, out)
    # not always used on ru-ship
    #print_sub(sub2, filter_shall=True)
