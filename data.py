# -*- coding: utf-8 -*-
"""
Created on Wed Apr 05 09:43:04 2017

@author: C41237
"""

import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
from bson import json_util
from collections import defaultdict
from audit_atributes import is_street_name, update_name, is_postal_code, update_postal_code

#lower: matches strings containing lower case characters
#lower_colon: matches strings containing lower case characters and a single colon within the string
#problemchars: matches characters that cannot be used within keys in MongoDB Here is a sample of OSM XML:

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

# Create dictionary ( json format) from the ElementTree element from the OSM file

def shape_element(element):
    node = defaultdict(dict) #node = {}
    if element.tag == "node" or element.tag == "way" :
        node["type"] = element.tag
        # attributes
        for a_key, a_val in element.items():
            if a_key in CREATED:
                node.setdefault("created", {})
                node["created"][a_key] = a_val
            elif a_key == "lat":
                node.setdefault("pos", [None, None])
                node["pos"][0] = float(a_val)
            elif a_key == "lon":
                node.setdefault("pos", [None, None])
                node["pos"][1] = float(a_val)
            else:
                node[a_key] = a_val
        # 2nd level tags
        for tag in element.iter("tag"):
            #Skip problematic characters
            if problemchars.search(tag.attrib['k']): 
                continue
            
            k = tag.attrib['k']
            v = tag.attrib['v']
            s = tag.attrib['k'].split(':')
              
            if len(s) >= 3:
                continue
            elif 'addr' in s[0]:
                #call update_name function
                if is_street_name(tag):
                    name = v
                    new_name = update_name(name)
                    node['address'].update({s[1]:new_name})
                else:
                    node['address'].update({s[1]:v})
                #call update_postal_codes
                if is_postal_code(tag):
                    name = v
                    new_postal_code = update_postal_code(name)
                    node['address'].update({s[1]:new_postal_code})
                else:
                    node['address'].update({s[1]:v})
            elif len(s) == 2:
                node[s[0] + '-' + s[1]] = v
            else:
                node[k] = v
        # for "way", covert to  <nd ref="12345678"/> to nd refs: [...]
        if element.tag == 'way':
            for node_ref in element.iter('nd'):
                node.setdefault("node_refs", [])
                ref = node_ref.get("ref")
                if ref is not None:
                    node["node_refs"].append(ref)

    else:
        return None
    
    return node


def process_map(file_in, pretty = False):
    # takes osm file and returs a json file to be imported by MongoDB
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for event, element in ET.iterparse(file_in, events=('start',)):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2, default=json_util.default)+"\n")
                else:
                    fo.write(json.dumps(el, default=json_util.default) + "\n")
    return data

def test():
    # If running this code with a larger dataset, call the process_map procedure with pretty=False. 
    #The pretty=True option adds additional spaces to the output, making it significantly larger.
    data = process_map('Malaga.osm', False)
    pprint.pprint(data)

    
if __name__ == "__main__":
    test()