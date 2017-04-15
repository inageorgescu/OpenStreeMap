# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 11:03:04 2017

@author: C41237
"""


import xml.etree.cElementTree as ET
from collections import defaultdict
import re
from pprint import pprint
import json

"""
- audit the OSMFILE and with the 'mapping' varaiable reflect the changes needed to solve
    the street_type_valid for the full street name returns if valid or not according to list VALID_STREET.
    the audit_street_type updates the street_type not in list VALID_STREET
    the is_street_name checks if if element tree attribute k == addr:street ( is a street)
    the audit gives from osmfile all streets with the (street type) field not valid
    update_names updates the street names not valid in the osm file and returns a dictionary with the updates
    
"""
#Audit street types
# Use Regex to obtain first word of string.
STREET_TYPE_RE = re.compile(r'^([\S]+)', re.IGNORECASE)

# Valid street types
VALID_STREET_FILENAME = './street_types_es.json'

# Read json file with valid street and posible variants 
with open(VALID_STREET_FILENAME) as f:    
    VALID_STREET = json.load(f, encoding='utf-8')  

def is_street_type_valid(name):

    m = STREET_TYPE_RE.search(name)
    if m:
        street_type = m.group()
        street_type = street_type.strip().title()
        if street_type in VALID_STREET.keys():
            return True
        else:
            return False
    

def audit_street_type(street_types, name):

    if not is_street_type_valid(name):
        m = STREET_TYPE_RE.search(name)
        if m:
            street_type = m.group()
            street_types[street_type].add(name)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    OSM_FILE = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(OSM_FILE, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    name = tag.attrib['v']
                    audit_street_type(street_types, name)
    OSM_FILE.close()
    return street_types


def update_name(name):

    if is_street_type_valid(name):
        return name
    else:
        m = STREET_TYPE_RE.search(name)
        if m:
            updated = False
            street_type = m.group()
            c_street_type = re.sub('\W+','', street_type)
            c_street_type = c_street_type.lower()
            c_street_type = unicode(c_street_type)
            for good_street_type, list_abbr in VALID_STREET.items():
                if c_street_type in [unicode(s) for s in list_abbr]:
                    name = re.sub(street_type, good_street_type, name)
                    name = name.encode('utf-8')
                    updated = True
                    break
            if not updated:
                pass
    return name

def update_names(osmfile):

    OSM_FILE = open(osmfile, "r")
    updates = {}
    for event, elem in ET.iterparse(OSM_FILE, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    name = tag.attrib['v']
                    new_name = update_name(name)
                    if name != new_name:
                        updates[name] = new_name
    OSM_FILE.close()
    return updates

    
 #Audit postal codes
POSTAL_CODE_RANGE = ["29001", "29002", "29003", "29004", "29005", "29006", "29007", 
                     "29008", "29009", "29010", "29011", "29012", "29013", "29014", "29015", "29016",
                     "29017", "29018", "29070", "29071", "29080", "29140", "29190", "29590", "29591"]
POSTAL_CODE_DEFAULT = "29001"

#count invalid values for postal codes
def audit_postal_code(invalid_postal_codes, postal_code):
   if not (postal_code in POSTAL_CODE_RANGE):
        
       invalid_postal_codes[postal_code] += 1

def is_postal_code(elem):
    return (elem.attrib['k'] == "addr:postcode")
    
def audit_pc (OSM_FILE):
    OSM_FILE = open(OSM_FILE, "r")
    invalid_postal_codes = defaultdict(int)

    for event, elem in ET.iterparse(OSM_FILE, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_postal_code(tag):
                    audit_postal_code(invalid_postal_codes, tag.attrib['v'])
                

    return invalid_postal_codes

#check if postal code within valid range, if not replace with default value
def update_postal_code(postal_code):
  
    if not (postal_code in POSTAL_CODE_RANGE):
        return POSTAL_CODE_DEFAULT
    else:
        return postal_code
        
def update_postal_codes(osmfile):

    OSM_FILE = open(osmfile, "r")
    updates = {}
    for event, elem in ET.iterparse(OSM_FILE, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_postal_code(tag):
                    postal_code = tag.attrib['v']
                    new_postal_code = update_postal_code(postal_code)
                    if postal_code != new_postal_code:
                        updates[postal_code] = new_postal_code
    OSM_FILE.close()
    return updates

def test():
    
    OSM_FILE = "./Malaga.osm"
    street_types = audit(OSM_FILE)
    postal_codes = audit_pc(OSM_FILE)
    pprint(dict(street_types))
    pprint(dict(postal_codes))
    updates = update_names(OSM_FILE)
    updates_pc = update_postal_codes(OSM_FILE)
    pprint(updates)
    pprint(updates_pc)

if __name__ == '__main__':
    test()