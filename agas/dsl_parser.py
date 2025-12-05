# For exec
import subprocess
import sys

# For config info
import jinja2
import os
import re

# For grammar and parsing
from lark import Lark, Transformer, v_args
import json

from lark import Discard
from lark.tree import pydot__tree_to_png   

# For Flask App
import subprocess
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os, json, re
from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef, Literal, XSD

from rdflib.namespace import OWL

from collections import defaultdict

from flask import flash, session, abort

import shutil

from rdflib.plugins.sparql import prepareQuery

#For asking text->query=results
#from openai import OpenAI
#import rdflib

# For RDF Graph generation
from graphviz import Digraph
import uuid

#For about and stats
from datetime import date
import markdown

#For the versions -> already imported before!! 
#import os
#import shutil
from datetime import datetime

#For LOGIN
from flask import render_template_string
from werkzeug.security import generate_password_hash, check_password_hash

#For PYPROJECT
import argparse

from rdflib import Graph, Namespace, RDF, RDFS, OWL
import os

#For parse and validation of vars
from urllib.parse import urlparse

#For utf encoding
import magic


__version__="0.0.1"

##########################################################################################
#                                GRAMMAR                                                 #
##########################################################################################

grammar = r"""
start: statement*

statement: pair
         | list_pair
         | dict_pair

pair: KEY "=" value
list_pair: KEY "=" "[" item ("," item)* "]"
dict_pair: KEY "=" "{" dict_item ("," dict_item)* "}"

value: STRING
     | PATH

item: STRING
    | MULTILINE_STRING
    
dict_item: STRING ":" item

KEY: /[A-Z_]+/

STRING: /'[^'\n]*'/
PATH: /'[^']*\/[^']*'/
MULTILINE_STRING: /'([^']|\n)*?'/

COMMENT: "#" /[^\n]*/
%ignore COMMENT
%ignore /[ \t\f\r\n]+/
"""

# Create parser
parser = Lark(grammar, start="start", parser="lalr")

# Global variables
info = {}

##########################################################################################
#                                TRANSFORMER                                             #
##########################################################################################

class ConfigTransformer(Transformer):
    def __init__(self):
        self.config = {}

    def start(self, statements):
        return self.config

    def pair(self, items):
        key, value = items
        key = key.value  # KEY is a Token
        self.config[key] = value
        info[key] = value
        return (key, value)

    def list_pair(self, items):
        key_token = items[0]
        key = key_token.value  # KEY is a Token
        values = items[1:]
        self.config[key] = values
        info[key] = values
        return (key, values)

    def dict_pair(self, items):
        key_token = items[0]
        key = key_token.value # KEY is a Token
        values = items[1:]
        self.config[key] = values
        info[key] = values
        return (key, values)

    def dict_item(self, items):
        key = items[0]
        values = items[1:]
        self.config[key] = values
        info[key] = values
        return (key, values)

    def value(self, val):
        return val[0]

    def item(self, val):
        return val[0]

    def STRING(self, s):
        return s.value[1:-1]  # Strip surrounding single quotes

    def PATH(self, p):
        return p.value[1:-1]

    def MULTILINE_STRING(self, s):
        return s.value[1:-1]


def load_config(file_path):
    #Detect encoding
    blob = open(file_path, 'rb').read()
    m = magic.Magic(mime_encoding=True)
    encoding = m.from_buffer(blob)  # "utf-8", "us-ascii", etc.
    
    correct_file = file_path
    
    # Not UTF-8, convert it
    if encoding != "utf-8":
        #Where to save the proper encoding
        temp_file = os.path.expanduser("~/agas/dsl_utf8.txt")
        # Make sure directory exists
        os.makedirs(os.path.dirname(temp_file), exist_ok=True)
        
        with open(file_path, "rb") as fin, open(temp_file, "w", encoding="utf-8") as fout:
            for line_bytes in fin:
                # decode from original encoding
                line = line_bytes.decode(encoding, errors="replace")
                # write in utf-8
                fout.write(line)
        
        correct_file = temp_file
        
    #Read correct file -> UTF-8 guaranteed
    with open(correct_file, "r", encoding="utf-8") as f:
        config_data = f.read()
    tree = parser.parse(config_data)
    return ConfigTransformer().transform(tree)


def show_skeleton(file_path):
    if file_path == "NONE":
        ontology_file = "CHANGE_ME"
        agas_name = "My Ontology"
        make_pretty = "['hasImage', 'hasStory']"
        username = "username"
        user_email = "example@hotmail.com"
    else:
        g = Graph()
        g.parse(file_path, format="turtle")  # adjust if needed

        # AGAS_NAME -> file name without extension
        agas_name = os.path.splitext(os.path.basename(file_path))[0]

        # MAKE_PRETTY -> find props starting with "has"
        make_pretty = []
        for s in g.subjects(RDF.type, OWL.DatatypeProperty):
            name = os.path.basename(str(s))
            if name.startswith("has"):
                make_pretty.append(name)
        for s in g.subjects(RDF.type, OWL.ObjectProperty):
            name = os.path.basename(str(s))
            if name.startswith("has"):
                make_pretty.append(name)
        make_pretty = make_pretty or "NONE"

        # Try to fetch creator/username/email from metadata
        username = "username"
        user_email = "example@hotmail.com"
        DC = Namespace("http://purl.org/dc/elements/1.1/")
        FOAF = Namespace("http://xmlns.com/foaf/0.1/")
        for creator in g.objects(None, DC.creator):
            username = str(creator)
        for name in g.objects(None, FOAF.name):
            username = str(name)
        for email in g.objects(None, FOAF.mbox):
            user_email = str(email)

        ontology_file = file_path

    # Print DSL
    print(f"""
# Specify the path to your ontology file and Protégé executable
ONTOLOGY_FILE = '{ontology_file}'
PROTEGE_PATH = 'Protege-5.6.4-linux/Protege-5.6.4/protege'

#Specify the type of ontology you have:
# A: table-like, more homegenic
# B: AGROVOC-like, heavy and more complex
# C1: Arquival, but with extra media (like images, etc)
# C2: Arquival, but no extra media
ONTOLOGY_TYPE = 'C1'

ONTOLOGY_IMAGES = 'NONE' #Specify if ontology has images that are from your own pc ('NONE' if not), if it does, please give the path to the folder you have them in
ONTOLOGY_EDIT = 'LOGIN' #Specify who can edit the ontology -> 'ALL' or 'LOGIN' are the options
USER_TYPE = 'NONEXP' #Specify the type of user for a custom experience -> 'EXP'/'NONEXP'
TEMPLATES = 'NONE' #Direct to templates you want to use
LANGUAGE = 'EN' #Define the language you want -> 'PT'/'EN'
RDF_VIEW = 'ALL' #LIST which classes you want the Graph to be about -> PLACE DOWN 'ALL' IF YOU WANT THEM ALL SHOWN
VIEW_CLASSES = 'STARS' #Specify things you'd like to see in the pages -> PLACE DOWN 'ALL' IF YOU WANT THEM ALL SHOWN -> PLACE DOWN 'STARS' IF YOU WANT TO USE STAR SYSTEM -> PLACE DOWN 'TREE' IF YOU WANT JQUERY SYSTEM
SPECIFIC_PAGES = 'STARS' #LIST specific individuals you'd like to favorite -> PLACE DOWN 'STARS' IF YOU WANT TO USE STAR SYSTEM
MAKE_PRETTY = {make_pretty} #LIST which properties you'd like to 'prettify' (remove the 'has') and enhance on the html -> 'NONE' IF YOU DONT WANT TO
SEE_PROPERTIES = 'NONE' #LIST which properties you'd like to see a list of individuals for  -> 'NONE' IF YOU DONT WANT TO
GIVE_PRIORITY = 'NONE' #LIST the order of things in the html page -> 'NONE' IF YOU HAVE NO PREFERENCE
NOT_SHOW = 'NONE' #LIST what you don't want to be shown -> can list off classes + individuals + properties -> 'NONE' IF YOU WANT TO SHOW EVERYTHING

#List of sparql queries that are going to be executed as a base for this to work
BASE_QUERIES = {{
    'Get Classes': '
    SELECT ?class WHERE {{
        ?class a owl:Class .
    }}
    ',
    'Get Deity List from Specific Class(es)': '
    SELECT ?individual WHERE {{
        ?individual a :<ClassName> .
    }}
    ORDER BY ASC(STR(?individual))
    ',
    'Get Obj Properties': '
    SELECT ?property WHERE {{ 
        ?property a owl:ObjectProperty .
    }}
    ',
    'Get Data Properties with range too': '
    SELECT ?prop ?domain ?range WHERE {{
        ?prop a owl:DatatypeProperty ;
                rdfs:domain ?domain ;
                rdfs:range ?range .
    }}
    '
}}

# METADADA focused variables:
AGAS_NAME = '{agas_name}'
L_DISPOSITION = 'side' #How to show a list 'up'(verticaly) or 'side'(horizontaly)
MODULES = 'NONE' #Want to see information expanded -> typically is for how a 'Story' is a 'Title'  and an 'Abstract' -> 'NONE' IF YOU DONT WANT TO USE IT
ABOUT = 'NONE' #Information about you or the ontology that you want to load -> CAN BE 'NONE' or '/path/specific/file.md'
ONTOLOGY_SOURCE = 'https://natura.di.uminho.pt/~jj/Diana/cwr.owl' #URL/LINK of where you got the ontology, if made by self please use url from the AGAS platform

#USER DATA for the contact page
USERNAME = '{username}'
USER_EMAIL = '{user_email}'
USER_GITHUB = 'github/example'
USER_SOCIALS = {{
  'LinkedIn': 'example@linkIn',
  'Instagram': 'example@insta',
  'Portfolio': 'personal@website.com'
}}

AGAS_PAGES = 'PAGES' #If you want it in blog format or normal pages -> 'BLOG'/'PAGES'
AGAS_BACKGROUNG = 'NONE' #If you want to put a personal background on the app, mostly common on blogs, but can be used in the normal pages too
""")
        
'''
def assess(file):
    with open(file) as f:
        config_data = f.read()
    tree = parser.parse(config_data)
    
    config_dict = ConfigTransformer().transform(tree)
    
    try:
        # Get info from the DSL into global variables
        ONTOLOGY_FILE = info['ONTOLOGY_FILE'] # USING
        PROTEGE_PATH = info['PROTEGE_PATH'] # USING
        ONTOLOGY_TYPE = info['ONTOLOGY_TYPE'] # USING
        ONTOLOGY_IMAGES = info['ONTOLOGY_IMAGES'] # USING
        ONTOLOGY_EDIT = info['ONTOLOGY_EDIT'] # USING
        USER_TYPE = info['USER_TYPE'] # USING
        TEMPLATES = info['TEMPLATES'] # USING
        LANGUAGE = info['LANGUAGE'] # USING
        RDF_VIEW = info['RDF_VIEW'] # USING
        VIEW_CLASSES = info['VIEW_CLASSES'] # USING 
        SPECIFIC_PAGES = info['SPECIFIC_PAGES'] # USING
        BASE_QUERIES = info['BASE_QUERIES'] # USING
        MAKE_PRETTY = info['MAKE_PRETTY'] # USING
        SEE_PROPERTIES = info['SEE_PROPERTIES'] # USING
        GIVE_PRIORITY = info['GIVE_PRIORITY'] # USING
        AGAS_NAME = info['AGAS_NAME'] # USING
        L_DISPOSITION = info['L_DISPOSITION'] # USING
        NOT_SHOW = info['NOT_SHOW'] # USING
        MODULES = info['MODULES'] # USING
        ABOUT = info['ABOUT'] # USING
        ONTOLOGY_SOURCE = info['ONTOLOGY_SOURCE'] # USING
        USERNAME = info['USERNAME'] # USING
        USER_EMAIL = info['USER_EMAIL'] # USING
        USER_GITHUB = info['USER_GITHUB'] # USING
        USER_SOCIALS = info['USER_SOCIALS'] # USING
        AGAS_PAGES = info['AGAS_PAGES'] # USING
        AGAS_BACKGROUNG = info['AGAS_BACKGROUNG'] # USING
        
        print("It's valid, good job!")
    except Exception as e:
        print("No good")
'''   
    
def validate_config(info):
    errors = []
    warnings = []

    # Helper: check URL
    def is_url(x):
        try:
            result = urlparse(x)
            return all([result.scheme, result.netloc])
        except:
            return False

    # ---------------------------------------------------------------------
    # 1. REQUIRED KEYS
    # ---------------------------------------------------------------------
    required = [
        "ONTOLOGY_FILE", "PROTEGE_PATH", "ONTOLOGY_TYPE", "ONTOLOGY_IMAGES",
        "ONTOLOGY_EDIT", "USER_TYPE", "TEMPLATES", "LANGUAGE", "RDF_VIEW",
        "VIEW_CLASSES", "SPECIFIC_PAGES", "MAKE_PRETTY", "SEE_PROPERTIES",
        "GIVE_PRIORITY", "NOT_SHOW", "BASE_QUERIES", "AGAS_NAME",
        "L_DISPOSITION", "MODULES", "ABOUT", "ONTOLOGY_SOURCE",
        "USERNAME", "USER_EMAIL", "USER_GITHUB", "USER_SOCIALS",
        "AGAS_PAGES", "AGAS_BACKGROUNG"
    ]

    for key in required:
        if key not in info:
            errors.append(f"Missing required variable: {key}")

    if errors:
        return errors, warnings

    # ---------------------------------------------------------------------
    # 2. SEMANTIC & TYPE CHECKS
    # ---------------------------------------------------------------------

    # ONTOLOGY_FILE must exist as well as it's SOURCE
    if info["ONTOLOGY_SOURCE"].startswith("http"):
        if not is_url(info["ONTOLOGY_SOURCE"]):
            errors.append("ONTOLOGY_SOURCE must be a valid URL.")
    
    if not os.path.exists(info["ONTOLOGY_FILE"]):
            errors.append(f"Ontology file not found: {info['ONTOLOGY_FILE']}")

    # PROTEGE_PATH must exist
    if not os.path.exists(info["PROTEGE_PATH"]):
        warnings.append(f"Protégé path seems invalid: {info['PROTEGE_PATH']}")

    # ONTOLOGY_TYPE
    allowed_types = ["A", "B", "C1", "C2"]
    if info["ONTOLOGY_TYPE"] not in allowed_types:
        errors.append(f"ONTOLOGY_TYPE must be one of {allowed_types}.")

    # ONTOLOGY_IMAGES
    if info["ONTOLOGY_IMAGES"] != "NONE":
        if not os.path.isdir(info["ONTOLOGY_IMAGES"]):
            errors.append(f"ONTOLOGY_IMAGES directory does not exist: {info['ONTOLOGY_IMAGES']}")

    # ONTOLOGY_EDIT
    if info["ONTOLOGY_EDIT"] not in ["ALL", "LOGIN"]:
        errors.append("ONTOLOGY_EDIT must be 'ALL' or 'LOGIN'.")

    # USER_TYPE
    if info["USER_TYPE"] not in ["EXP", "NONEXP"]:
        errors.append("USER_TYPE must be 'EXP' or 'NONEXP'.")

    # LANGUAGE
    if info["LANGUAGE"] not in ["EN", "PT"]:
        errors.append("LANGUAGE must be EN or PT.")

    # RDF_VIEW
    if not (info["RDF_VIEW"] == "ALL" or isinstance(info["RDF_VIEW"], list)):
        errors.append("RDF_VIEW must be 'ALL' or a list.")

    # VIEW_CLASSES
    allowed_view = ["ALL", "TREE", "STARS"]
    if not (info["VIEW_CLASSES"] in allowed_view or isinstance(info["VIEW_CLASSES"], list)):
        errors.append("VIEW_CLASSES must be 'ALL', 'TREE', 'STARS' or a list.")

    # SPECIFIC_PAGES
    if not (info["SPECIFIC_PAGES"] == "STARS" or isinstance(info["SPECIFIC_PAGES"], list)):
        errors.append("SPECIFIC_PAGES must be 'STARS' or a list.")

    # MAKE_PRETTY, SEE_PROPERTIES, GIVE_PRIORITY, NOT_SHOW
    list_like = ["MAKE_PRETTY", "SEE_PROPERTIES", "GIVE_PRIORITY", "NOT_SHOW"]
    for key in list_like:
        val = info[key]
        if not (val == "NONE" or isinstance(val, list)):
            errors.append(f"{key} must be 'NONE' or a list.")

    # BASE_QUERIES
    BASE_QUERIES = info['BASE_QUERIES']
    for value, query in BASE_QUERIES:
        warnings.append(f"Found QUERY: {value} -> {query[0]}")
    
    # L_DISPOSITION
    if info["L_DISPOSITION"] not in ["up", "side"]:
        errors.append("L_DISPOSITION must be 'up' or 'side'.")

    # MODULES
    if not (info["MODULES"] == "NONE" or isinstance(info["MODULES"], list)):
        errors.append("MODULES must be 'NONE' or a list.")

    # ABOUT
    if info["ABOUT"] != "NONE" and not os.path.exists(info["ABOUT"]):
        warnings.append(f"ABOUT file not found: {info['ABOUT']}")

    # USER_EMAIL simple regex
    if info["ABOUT"] != "NONE" and re.match(r"[^@]+@[^@]+\.[^@]+", info["USER_EMAIL"]):
        warnings.append("USER_EMAIL appears invalid.")

    # AGAS_PAGES
    if info["AGAS_PAGES"] not in ["BLOG", "PAGES"]:
        errors.append("AGAS_PAGES must be 'BLOG' or 'PAGES'.")

    # AGAS_BACKGROUNG
    if info["AGAS_BACKGROUNG"] != "NONE":
        if not os.path.exists(info["AGAS_BACKGROUNG"]):
            warnings.append("AGAS_BACKGROUNG path not found.")


    return errors, warnings











def assess(file):
    #Detect encoding
    blob = open(file, 'rb').read()
    m = magic.Magic(mime_encoding=True)
    encoding = m.from_buffer(blob)  # "utf-8", "us-ascii", etc.
    
    correct_file = file
    
    # Not UTF-8, convert it
    if encoding != "utf-8":
        #Where to save the proper encoding
        temp_file = os.path.expanduser("~/agas/dsl_utf8.txt")
        # Make sure directory exists
        os.makedirs(os.path.dirname(temp_file), exist_ok=True)
        
        with open(file, "rb") as fin, open(temp_file, "w", encoding="utf-8") as fout:
            for line_bytes in fin:
                # decode from original encoding
                line = line_bytes.decode(encoding, errors="replace")
                # write in utf-8
                fout.write(line)
        
        correct_file = temp_file
        
    #Read correct file -> UTF-8 guaranteed
    with open(correct_file, "r", encoding="utf-8") as f:
        config_data = f.read()

    #with open(file) as f:
    #    config_data = f.read()

    tree = parser.parse(config_data)
    info = ConfigTransformer().transform(tree)

    errors, warnings = validate_config(info)

    if errors:
        print("❌ Configuration is invalid.\n")
        for err in errors:
            print(f"  - {err}")
    else:
        print("✅ Configuration is valid!")
        if warnings:
            print("\n⚠️ Warnings:")
            for w in warnings:
                print(f"  - {w}")


