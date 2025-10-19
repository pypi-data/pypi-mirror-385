import sys
import base64
import re
import os
from typing import Dict

def from_file_list(lst):
    """
    Generates a filemap for Gempyre
    :param lst: list of filenames.
    :return: two dictionaries, first is map second is to map it's keys to give arguments.
    """
    data = dict()
    names = dict()
    for in_name in lst:
        encoded = ""
        with open(in_name, 'rb') as infile:
            content = infile.read()
            encoded = base64.standard_b64encode(content).decode('utf-8')
        sname = '/' + re.sub('[^a-zA-Z_.]', '', os.path.basename(in_name)) # why this was capitalize()?
        data[sname] = encoded
        names[in_name] = sname
    return data, names
    
    
def from_file(*argv):
    """
    Generates a filemap for Gempyre
    :param argv: argument list of filenames.
    :return: two dictionaries, first is map second is to map it's keys to give arguments.
    """
    lst = list()
    for a in argv:
        lst.append(a);
    return from_file_list(lst)

def from_bytes(data_map: Dict[str, bytes]):
    """
    Generates a filemap for Gempyre
    :param dict of file (kind of) names and their content.
    :return: two dictionaries, first is map second is to map it's keys to give arguments.
    """
    data = dict()
    names = dict()
    for in_name, content in data_map.items():
        encoded = base64.standard_b64encode(content).decode('utf-8')
        sname = '/' + re.sub('[^a-zA-Z_.]', '', os.path.basename(in_name)) # why this was capitalize()?
        data[sname] = encoded
        names[in_name] = sname
    return data, names

def from_html(html: str):
    return from_bytes({"main.html": bytes(html, 'utf-8')})