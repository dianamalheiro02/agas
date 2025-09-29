#!/usr/bin/env python3  

import argparse
import sys
from .dsl_parser import load_config, show_skeleton, assess
from .flask_app import create_app

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

from rdflib import Graph


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

def manual():
    """
    NAME
        agas - Application for automatic website generation

    SYNOPSIS
        agas [options] [input_file]

    OPTIONS
        -s, --skeleton   Show a skeleton for the DSL configuration file
        -c, --check      Validate a DSL config file
        -r, --run        Run the AGAS Flask app with the given input file
        --manual         Show this detailed manual

    DESCRIPTION
        AGAS is a research platform for automatic web prototype generation.
        It follows the following magic formula: DSL + Ontology = Website.
        This script launches the AGAS application/platform and allows the user
        to navigate the generated website, supporting BREAD operations 
        (Browse, Read, Edit, Add, Delete).
        
    GETTING STARTED
        1. Create your skeleton:
            agas -s > G0_config.txt
            
        2. Next, you can now run AGAS with the file as is or edit the information 
        first, with your preferred text editor (e.g., Vim, VSCode).
        
        3. Validate it:
            agas -c G0_config.txt
            
        4. Run it:
            agas -r G0_config.txt
            
        5. Open your browser to: http://localhost:5000
        
        Well done! You now have your very own ontology-powered website up and running.
        Otherwise, if you already have a config file in mind, simply run AGAS with it and
        get to navigating and exploring!
        
    MORE
        Venture to '/agas/static/AGAS_manual.md' for more information if this was
        not clear enough, please and thank you <3 
    """

def main():
    parser = argparse.ArgumentParser(
        prog="agas",
        description="AGAS - Application for automatic website generation"
    )
    parser.add_argument("input_file", nargs="?", help="Configuration DSL file")
    parser.add_argument("-s", "--skeleton", action="store_true", help="Show DSL config skeleton")
    parser.add_argument("-c", "--check", action="store_true", help="Check DSL config file")
    parser.add_argument("-r", "--run", action="store_true", help="Run Flask app with config")
    parser.add_argument("--manual", action="store_true", help="Show detailed manual")

    args = parser.parse_args()

    if args.skeleton:
        if not args.input_file:
            file = 'NONE'
            show_skeleton(file)
            sys.exit(0)
        else:
            show_skeleton(args.input_file)
            sys.exit(0)

    if args.check:
        if not args.input_file:
            print("ERROR: No file provided for --check")
            sys.exit(1)
        assess(args.input_file)
        sys.exit(0)

    if args.manual:
        print(manual.__doc__)
        sys.exit(0)

    if args.run:
        if not args.input_file:
            print("ERROR: No configuration file provided")
            sys.exit(1)

        info = load_config(args.input_file)
        app = create_app(info)
        app.run(debug=True)
        sys.exit(0)

    parser.print_help()
