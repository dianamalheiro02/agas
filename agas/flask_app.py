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

#For JQuery Widgets
import json
from collections import defaultdict
from rdflib import RDF, RDFS, OWL, URIRef

from werkzeug.utils import secure_filename

from rdflib import BNode

from rdflib import Graph, RDF, OWL, URIRef, Literal, XSD
from collections import defaultdict

from itertools import product

#For add on templates
from jinja2 import ChoiceLoader, FileSystemLoader

#For zip
from flask import send_file
import os, zipfile, tempfile

#For .md manual
#from flask import Flask, render_template_string
import markdown

#For no secrets
from dotenv import load_dotenv
#import os


def create_app(info):
    #templates = info.get("app.config["TEMPLATES"]", "templates")
    ##app = Flask(__name__, template_folder=templates)
    #app.secret_key = "goddess-has-power-123"

    # TODO: add your routes here+
    
    
    ##########################################################################################
    #                             FLASK APP - INFO                                           #
    ##########################################################################################
    #TEMPLATES = info['TEMPLATES']
    
    # Expand the '~' present in the directory
    #TEMPLATES = os.path.expanduser(TEMPLATES)
    
    #print(TEMPLATES)

    #app = Flask(__name__) -> BEFORE USING app.config["TEMPLATES"] VAR
    #app = Flask(__name__, template_folder= TEMPLATES)
    
    # Default template folder (inside your project)
    DEFAULT_TEMPLATES = os.path.join(os.path.dirname(__file__), "templates")

    # Optional template folder from config
    EXTRA_TEMPLATES = info['TEMPLATES']

    # Initialize Flask with the default folder
    app = Flask(__name__, template_folder=DEFAULT_TEMPLATES)

    # If EXTRA_TEMPLATES is valid and not "NONE", add it
    if EXTRA_TEMPLATES != "NONE" and os.path.isdir(EXTRA_TEMPLATES):
        app.jinja_loader = ChoiceLoader([
            FileSystemLoader(EXTRA_TEMPLATES),
            app.jinja_loader,  # keep the default one too
        ])
    
    # store ontology file and graph in config
    # Get info from the DSL into global variables
    app.config["ONTOLOGY_FILE"] = info['ONTOLOGY_FILE'] # USING
    app.config["PROTEGE_PATH"] = info['PROTEGE_PATH'] # USING
    app.config["ONTOLOGY_TYPE"] = info['ONTOLOGY_TYPE'] # USING
    app.config["ONTOLOGY_IMAGES"] = info['ONTOLOGY_IMAGES'] # USING
    app.config["ONTOLOGY_EDIT"] = info['ONTOLOGY_EDIT'] # USING
    app.config["USER_TYPE"] = info['USER_TYPE'] # USING
    #app.config["TEMPLATES"] = info['TEMPLATES'] # USING
    app.config["LANGUAGE"] = info['LANGUAGE'] # USING
    app.config["RDF_VIEW"] = info['RDF_VIEW'] # USING
    app.config["VIEW_CLASSES"] = info['VIEW_CLASSES'] # USING 
    app.config["SPECIFIC_PAGES"] = info['SPECIFIC_PAGES'] # USING
    app.config["BASE_QUERIES"] = info['BASE_QUERIES'] # USING
    app.config["MAKE_PRETTY"] = info['MAKE_PRETTY'] # USING
    app.config["SEE_PROPERTIES"] = info['SEE_PROPERTIES'] # USING
    app.config["GIVE_PRIORITY"] = info['GIVE_PRIORITY'] # USING
    app.config["AGAS_NAME"] = info['AGAS_NAME'] # USING
    app.config["L_DISPOSITION"] = info['L_DISPOSITION'] # USING
    app.config["NOT_SHOW"] = info['NOT_SHOW'] # USING
    app.config["MODULES"] = info['MODULES'] # USING
    app.config["ABOUT"] = info['ABOUT'] # USING
    app.config["ONTOLOGY_SOURCE"] = info['ONTOLOGY_SOURCE'] # USING
    app.config["USERNAME"] = info['USERNAME'] # USING
    app.config["USER_EMAIL"] = info['USER_EMAIL'] # USING
    app.config["USER_GITHUB"] = info['USER_GITHUB'] # USING
    app.config["USER_SOCIALS"] = info['USER_SOCIALS'] # USING
    app.config["AGAS_PAGES"] = info['AGAS_PAGES'] # USING
    app.config["AGAS_BACKGROUNG"] = info['AGAS_BACKGROUNG'] # USING


    # Debug
    #print(ONTOLOGY_FILE)
    #print(PROTEGE_PATH)
    #print(ONTOLOGY_TYPE)
    #print(USER_TYPE)
    #print(TEMPLATES)
    #print(VIEW_CLASSES)
    #print(SPECIFIC_PAGES)
    #print(BASE_QUERIES)
    #print(TREAT_MD)

    load_dotenv()  # loads variables from .env
    app.secret_key = os.getenv("OPENAI_API_KEY")

    #For LogIn 
    # Single admin account
    app.config["ADMIN_USERNAME"] = "AGAS_Admin"
    app.config["ADMIN_PASSWORD_HASH"] = generate_password_hash("AGAS_Admin_Password")

    # Load the ontology once
    app.config["GRAPH"] = Graph()
    g = app.config["GRAPH"]
    #g.parse(ONTOLOGY_FILE) NO WORK!!!

    # List of conversions (3 max)
    conversions = []

    # Directory to store results
    app.config["RESULTS_DIR"] = "results"
    os.makedirs(app.config["RESULTS_DIR"], exist_ok=True)

    app.config["PREFIX"] = ""

    #print(ONTOLOGY_FILE)
    if app.config["ONTOLOGY_FILE"]:
        if app.config["ONTOLOGY_FILE"].endswith('.rdf'):
            g.parse(app.config["ONTOLOGY_FILE"], format="xml")

        elif app.config["ONTOLOGY_FILE"].endswith('.ttl'):
            g.parse(app.config["ONTOLOGY_FILE"], format="turtle")

        elif app.config["ONTOLOGY_FILE"].endswith('.owl'):
            g.parse(app.config["ONTOLOGY_FILE"], format="xml")

        conversions.append(app.config["ONTOLOGY_FILE"])
        with open(app.config["ONTOLOGY_FILE"], 'r') as f:
            first_line = f.readline()

            match = re.search(r'<([^>]+)>', first_line)
            if match:
                uri = match.group(1)
                print("Extracted URI:", uri)
                app.config["PREFIX"] = uri
            else:
                print("No URI found.")
    else:
        print("ONTOLOGY_FILE not found in config.\n----- ERROR -----")

    app.config["TAXONOMY"] = []

    # For the RDF Graph -> WRONG APPROACH
    #os.makedirs("static/graphs", exist_ok=True)

    # For the versions -> saving the ontology as a copy first
    app.config["VERSIONS_DIR"] = "versions"

    os.makedirs(app.config["VERSIONS_DIR"], exist_ok=True)

    # timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if app.config["ONTOLOGY_FILE"].endswith('.rdf'):
        version_file = os.path.join(app.config["VERSIONS_DIR"], f"ontology_{timestamp}.rdf")
    elif app.config["ONTOLOGY_FILE"].endswith('.owl'):
        version_file = os.path.join(app.config["VERSIONS_DIR"], f"ontology_{timestamp}.owl")
    elif app.config["ONTOLOGY_FILE"].endswith('.ttl'):
        version_file = os.path.join(app.config["VERSIONS_DIR"], f"ontology_{timestamp}.ttl")
        
    # copy original into versions (if folder is empty included)
    shutil.copy(app.config["ONTOLOGY_FILE"], version_file)

    # the most recent version becomes ONTOLOGY_FILE
    versions = sorted(os.listdir(app.config["VERSIONS_DIR"]))
    app.config["ONTOLOGY_FILE"] = os.path.join(app.config["VERSIONS_DIR"], versions[-1])

    #For pictures from the Desktop
    if app.config["ONTOLOGY_IMAGES"] != "NONE" and app.config["ONTOLOGY_IMAGES"] != "none":
        source_directory = app.config["ONTOLOGY_IMAGES"]
        destination_directory = os.path.join(app.static_folder, "images/ontology")

        # make sure destination exists
        os.makedirs(destination_directory, exist_ok=True)

        # copy files one by one (avoids copytree overwrite errors)
        for filename in os.listdir(source_directory):
            src = os.path.join(source_directory, filename)
            dst = os.path.join(destination_directory, filename)
            if os.path.isfile(src):
                shutil.copy2(src, dst)  # copy with metadata
                
    ##########################################################################################
    #                                DEF'S NEEDED                                            #
    ##########################################################################################

    # Pretty print function that removes the PREFIX from the query results
    def pretty_print(response):
        final = []
        for elem in response:
            res = re.split(re.escape(app.config["PREFIX"]), elem[0]) #because the prefix contains special characters like / that could be misinterpreted by the regex engine. 're.escape()' makes sure they're treated literally.
            if len(res) > 1:
                final.append(res[1])

        return final

    # Pretty print function that removes the PREFIX from URIs
    def pretty_print_uri(list):
        final = []
        for elem in list:
            uri = str(elem)  # Ensure elem is a string
            if uri.startswith(app.config["PREFIX"]):
                final.append(uri[len(app.config["PREFIX"]):])
            else:
                final.append(uri)  # Keep as-is if not prefixed
        return final

    # To get a base of the Taxonomy of the Ontology given (classes - the classes that have subclasses)
    def build_class_taxonomy(graph):
        #print(app.config["ONTOLOGY_FILE"])
        # Map each class to its subclasses
        subclass_map = defaultdict(list)

        for subclass, _, superclass in graph.triples((None, RDFS.subClassOf, None)):
            if (subclass, RDF.type, OWL.Class) in graph or isinstance(subclass, URIRef):
                subclass_map[superclass].append(subclass)

        #print(pretty_print_uri(subclass_map))

        # Get all named classes (non-blank)
        all_classes = set(graph.subjects(RDF.type, OWL.Class))

        #print(pretty_print_uri(all_classes))

        # Build tree: top-level classes (with no superclasses)
        roots = [c for c in all_classes if c not in subclass_map]

        #print(pretty_print_uri(roots)) 

        def build_tree(cls, level=0):
            label = cls.split("/")[-1]
            result = [("  " * level) + label]
            for subclass in subclass_map.get(cls, []):
                result += build_tree(subclass, level + 1)
            return result

        app.config["TAXONOMY"] = []
        for root in roots:
            app.config["TAXONOMY"] += build_tree(root)

        return app.config["TAXONOMY"]

    # To build an rdf from scratch
    def build_graph_image_from_ontology(g, focus_classes=None, filename="ontology_graph"):
        dot = Digraph(comment="Ontology Graph", format="png")
        dot.attr(rankdir="LR", size='8,5')
        added_nodes = set()

        # Get classes to show
        classes_to_show = set()
        if focus_classes:
            for cls in focus_classes:
                full_uri = URIRef(app.config["PREFIX"] + cls)
                classes_to_show.add(full_uri)
                # Also include subclasses and superclasses for context
                for s, _, o in g.triples((None, RDFS.subClassOf, full_uri)):
                    classes_to_show.add(s)
                for s, _, o in g.triples((full_uri, RDFS.subClassOf, None)):
                    classes_to_show.add(o)
        else:
            classes_to_show = set(g.subjects(RDF.type, OWL.Class))

        # Add nodes
        for cls in classes_to_show:
            if (cls, RDF.type, OWL.Class) in g:
                cname = str(cls).replace(app.config["PREFIX"], "")
                if cname not in added_nodes:
                    dot.node(cname, shape="ellipse", color="lightblue", style="filled")
                    added_nodes.add(cname)

        # Subclass edges
        for subclass, _, superclass in g.triples((None, RDFS.subClassOf, None)):
            if focus_classes:
                # Only draw edges between focus URIs (not blank nodes)
                if isinstance(subclass, URIRef) and isinstance(superclass, URIRef):
                    if subclass in classes_to_show and superclass in classes_to_show:
                        sname = str(subclass).replace(app.config["PREFIX"], "")
                        oname = str(superclass).replace(app.config["PREFIX"], "")
                        dot.edge(sname, oname, label="subClassOf")
            else:
                if isinstance(superclass, URIRef) and str(superclass).startswith(app.config["PREFIX"]):
                    sname = str(subclass).replace(app.config["PREFIX"], "")
                    oname = str(superclass).replace(app.config["PREFIX"], "")
                    dot.edge(sname, oname, label="subClassOf")


        # ObjectProperty edges
        for prop in g.subjects(RDF.type, OWL.ObjectProperty):
            domain = next(g.objects(prop, RDFS.domain), None)
            range_ = next(g.objects(prop, RDFS.range), None)

            if domain in classes_to_show and range_ in classes_to_show:
                pname = str(prop).replace(app.config["PREFIX"], "")
                dname = str(domain).replace(app.config["PREFIX"], "")
                rname = str(range_).replace(app.config["PREFIX"], "")
                dot.edge(dname, rname, label=pname, style="dashed")

        # Render image -> 1st approach
        #path = f"static/graphs/{filename}"
        #dot.render(path, cleanup=True)
        #dot.render(path, format="pdf", cleanup=False)
        
        #print("Graph written to:", os.path.abspath(path + ".png"))
        #print("Exists?", os.path.exists(path + ".png"))
        #return f"/static/graphs/{filename}.png"


        # Make sure we save inside the app’s static folder
        graphs_dir = os.path.join(app.static_folder, "graphs")
        os.makedirs(graphs_dir, exist_ok=True)

        file_path = os.path.join(graphs_dir, filename)

        # Render PNG + PDF into the right static folder
        dot.render(file_path, format="png", cleanup=True)
        dot.render(file_path, format="pdf", cleanup=False)

        # Return URL Flask can serve
        return url_for("static", filename=f"graphs/{filename}.png")


    # To get the DP and OP of the Onto
    def data_object_properties(graph):
        results = []

        for s in graph.subjects(RDF.type, OWL.DatatypeProperty):
            label = str(s).split("#")[-1] if "#" in str(s) else str(s).split("/")[-1]
            results.append(label)

        for s in graph.subjects(RDF.type, OWL.ObjectProperty):
            label = str(s).split("#")[-1] if "#" in str(s) else str(s).split("/")[-1]
            results.append(label)

        return results

    # To get the placeholders in a query that needs modifying to work
    def extract_placeholders(query):
        #print("HERE")
        #print(query[0])
        #print(re.findall(r'<([^>]+)>', query[0]))

        return re.findall(r'<([^>]+)>', query[0])  # returns list

    #To get all the 'about' information of the ontology
    ontology_node = next(iter(g.subjects(RDF.type, OWL.Ontology)), None)
    # Helper function
    def get_prop(predicate, fallback="N/A"):
        return str(next(g.objects(ontology_node, predicate), fallback))

    def get_about():
        taxonomy = build_class_taxonomy(g) 
        
        t_indivs = []

        for cls in taxonomy:
            class_uri = NS[cls]
            individuals = sorted(g.subjects(RDF.type, class_uri))

            for ind in individuals:
                #print(ind)
                if ind not in t_indivs:
                    t_indivs.append(ind)

        t_indivs = pretty_print_uri(t_indivs)
        
        stats = {
            "classes": len(list(g.subjects(RDF.type, OWL.Class))),
            "individuals": len(t_indivs),
            "data_properties": len(list(g.subjects(RDF.type, OWL.DatatypeProperty))),
            "object_properties": len(list(g.subjects(RDF.type, OWL.ObjectProperty))),
            "annotation_properties": len(list(g.subjects(RDF.type, OWL.AnnotationProperty))),
            "namespaces": list(dict(g.namespaces()).keys()),
            "name": app.config["AGAS_NAME"],
            "version": g.value(None, OWL.versionInfo) or "1.0",
            "iri": g.identifier,
            "Frdf": "NOT_GENERATED",
            "Fttl": "NOT_GENERATED",
            "Fowl": "NOT_GENERATED",
            "imports": [str(o) for o in g.objects(None, OWL.imports)],
            "citation": "@misc{" + f'''
    {app.config["AGAS_NAME"]},
    author = {get_prop(NS.creatorName) if get_prop(NS.createdDate) != "N/A" else app.config["USERNAME"]},
    title = {app.config["AGAS_NAME"]},
    year = {date.today().year},
    url = {app.config["ONTOLOGY_SOURCE"]},
    ''' + "note = {Accessed via AGAS}"+ "\n}"
        }
        
        # Metadata using the prefix
        stats["creator_name"] = get_prop(NS.creatorName) if get_prop(NS.createdDate) != "N/A" else app.config["USERNAME"]
        stats["creator_email"] = get_prop(NS.creatorEmail) if get_prop(NS.createdDate) != "N/A" else app.config["USER_EMAIL"]
        stats["created_date"] = get_prop(NS.createdDate) if get_prop(NS.createdDate) != "N/A" else date.today().year #date.today().strftime("%Y-%m-%d")
        stats["description"] = get_prop(RDFS.comment)
        
        for c in conversions:
            if c.endswith('.rdf'):
                stats['Frdf'] = c
                
            elif c.endswith('.ttl'):
                stats['Fttl'] = c

            elif c.endswith('.owl'):
                stats['Fowl'] = c
                
        about = app.config["ABOUT"]
        if about != 'NONE' or about != 'None':
            if os.path.exists(about):
                with open(about, "r", encoding="utf-8") as file:
                    md_content = file.read()
                    stats["about"] = markdown.markdown(md_content, extensions=["fenced_code", "tables"])
            else:
                stats["about"] = "<p>No about file provided.</p>"
        
        return stats

    #To get the contacts information
    def get_contacts():
        stats = {
            "user_name": app.config["USERNAME"],
            "user_type": app.config["USER_TYPE"],
            "user_email": app.config["USER_EMAIL"],
            "user_github": app.config["USER_GITHUB"],
            "socials": app.config["USER_SOCIALS"]
        }
        
        return stats

    #To make a copy of the ontology into the versions folder
    def save_new_version(ontology_graph):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        #version_file = os.path.join(app.config["VERSIONS_DIR"], f"ontology_{timestamp}.owl")
        if app.config["ONTOLOGY_FILE"].endswith('.rdf'):
            version_file = os.path.join(app.config["VERSIONS_DIR"], f"ontology_{timestamp}.rdf")
            ontology_graph.serialize(destination=version_file, format="xml")
        elif app.config["ONTOLOGY_FILE"].endswith('.owl'):
            version_file = os.path.join(app.config["VERSIONS_DIR"], f"ontology_{timestamp}.owl")
            ontology_graph.serialize(destination=version_file, format="xml")
        elif app.config["ONTOLOGY_FILE"].endswith('.ttl'):
            version_file = os.path.join(app.config["VERSIONS_DIR"], f"ontology_{timestamp}.ttl")
            ontology_graph.serialize(destination=version_file, format="turtle")
        #ontology_graph.save(file=version_file, format="xml")  # or ttl, etc.
        return version_file


    def taxonomy_with_individuals(graph, ns):
        subclass_map = defaultdict(list)

        # Map subclasses to superclasses
        for subclass, _, superclass in graph.triples((None, RDFS.subClassOf, None)):
            if (subclass, RDF.type, OWL.Class) in graph or isinstance(subclass, URIRef):
                subclass_map[superclass].append(subclass)

        # Find all declared classes
        all_classes = set(graph.subjects(RDF.type, OWL.Class))
        roots = [c for c in all_classes if c not in subclass_map]

        def pretty_label(uri):
            return str(uri).split("/")[-1]

        def build_node(cls):
            cls_label = pretty_label(cls)

            # Node for this class (with link)
            node = {
                "label": f"<a href='/class/{cls_label}'>{cls_label}</a>",
                "type": "class",
                "items": []
            }

            # Add subclasses
            for child in subclass_map.get(cls, []):
                node["items"].append(build_node(child))

            # Add individuals under this class
            for ind in graph.subjects(RDF.type, cls):
                ind_label = pretty_label(ind)
                node["items"].append({
                    "label": f"<a href='/individual/{ind_label}'>{ind_label}</a>",
                    "type": "individual"
                })

            return node

        return [build_node(root) for root in roots]


    ##########################################################################################
    #                                FLASK ROUTES                                            #
    ##########################################################################################
    NS = Namespace(app.config["PREFIX"])

    #BASIC ONE
    #@app.route("/login")
    # def login():
    #    session["logged_in"] = True
    #    return redirect(url_for("home"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            if username == app.config["ADMIN_USERNAME"] and check_password_hash(app.config["ADMIN_PASSWORD_HASH"], password):
                session["logged_in"] = True
                return redirect(url_for("home"))
            else:
                return "<p>Invalid credentials. Try again.</p>", 401

        # Inline login form (can replace with login.html later)
        return render_template("LOGIN.html")


    @app.route("/logout")
    def logout():
        if app.config["ONTOLOGY_EDIT"] != "LOGIN":
            session["logged_in"] = True
            return redirect(url_for("home"))

        session.pop("logged_in", None)
        return redirect(url_for("home"))


    ################################# HOME PAGES #############################################
    @app.route('/')
    def home():         
        taxonomy = build_class_taxonomy(g) 
        results = data_object_properties(g)
        
        t_indivs = []

        for cls in taxonomy:
            class_uri = NS[cls]
            individuals = sorted(g.subjects(RDF.type, class_uri))

            for ind in individuals:
                #print(ind)
                if ind not in t_indivs:
                    t_indivs.append(ind)

        t_indivs = pretty_print_uri(t_indivs)

        #print(taxonomy)
        #print(t_indivs)
        #print(results)

        if app.config["USER_TYPE"] == "EXP":
            return render_template("jinjaT/homeEXP.html", language = app.config["LANGUAGE"],
                                u_type=app.config["USER_TYPE"],
                                taxonomy=sorted(taxonomy),
                                view_classes=app.config["VIEW_CLASSES"],
                                specific_pages=app.config["SPECIFIC_PAGES"])
        else:
                if app.config["AGAS_PAGES"] == "BLOG":
                    classes_with_indivs = taxonomy_with_individuals(g, NS)

                    return render_template("jinjaT/blog.html", language = app.config["LANGUAGE"], taxonomy_json=json.dumps(classes_with_indivs),
                                        u_type=app.config["USER_TYPE"],
                                        taxonomy=sorted([tax for tax in taxonomy if tax not in app.config["NOT_SHOW"]]),
                                        view_classes=app.config["VIEW_CLASSES"],
                                        dop=[res for res in results if res not in app.config["NOT_SHOW"]],
                                        individuals=[t_i for t_i in t_indivs if t_i not in app.config["NOT_SHOW"]],
                                        specific_pages=app.config["SPECIFIC_PAGES"],
                                        name=app.config["AGAS_NAME"],
                                        about=get_about(),
                                        contacts=get_contacts(),
                                        background=app.config["AGAS_BACKGROUNG"])
                else:    
                    classes_with_indivs = taxonomy_with_individuals(g, NS)
                    #print(classes_with_indivs)
                    return render_template("jinjaT/home.html", language = app.config["LANGUAGE"], taxonomy_json=json.dumps(classes_with_indivs),
                                        u_type=app.config["USER_TYPE"],
                                        taxonomy=sorted([tax for tax in taxonomy if tax not in app.config["NOT_SHOW"]]),
                                        view_classes=app.config["VIEW_CLASSES"],
                                        dop=[res for res in results if res not in app.config["NOT_SHOW"]],
                                        individuals=[t_i for t_i in t_indivs if t_i not in app.config["NOT_SHOW"]],
                                        specific_pages=app.config["SPECIFIC_PAGES"],
                                        name=app.config["AGAS_NAME"])

    @app.route('/home')
    def homeEXP():         
        taxonomy = build_class_taxonomy(g) 
        results = data_object_properties(g)

        #print(app.config["ONTOLOGY_FILE"])
        #print(taxonomy)
        
        t_indivs = []

        for cls in taxonomy:
            class_uri = NS[cls.split('#')[-1]]
            individuals = sorted(g.subjects(RDF.type, class_uri))
            
            #print(class_uri)
            #print(individuals)
            
            for ind in individuals:
                #print(ind)
                if ind not in t_indivs:
                    t_indivs.append(ind)
        
        individuals2 = sorted(g.subjects(RDF.type, OWL.NamedIndividual))
        #print(individuals2)    
        
        #print("HERE")
        
        for ind in individuals2:
            i = ind.split("#")[-1] if "#" in ind else ind.split("/")[-1] 
            for cls in taxonomy:
                cls = cls.split("#")[-1] if "#" in ind else ind.split("/")[-1]
                #print(f"{cls} -> {i}")
                if i == cls:
                    #print(i)
                    t_indivs.append(ind+"_IND")
        
        t_indivs = pretty_print_uri(t_indivs)
        
        #print(taxonomy)
        #print(t_indivs)
        #print(results)
        
        #print(app.config["NOT_SHOW"])
        #print([res for res in results if res not in app.config["NOT_SHOW"]])
        
        #for t in taxonomy:
        #    print(t.split('#')[0].isalpha())

        if app.config["USER_TYPE"] == "EXP":
            if app.config["AGAS_PAGES"] == "BLOG":
                    classes_with_indivs = taxonomy_with_individuals(g, NS)

                    return render_template("jinjaT/blog.html", language = app.config["LANGUAGE"], taxonomy_json=json.dumps(classes_with_indivs),
                                        u_type=app.config["USER_TYPE"],
                                        taxonomy=sorted([tax for tax in taxonomy if tax not in app.config["NOT_SHOW"]]),
                                        view_classes=app.config["VIEW_CLASSES"],
                                        dop=[res for res in results if res not in app.config["NOT_SHOW"]],
                                        individuals=[t_i for t_i in t_indivs if t_i not in app.config["NOT_SHOW"]],
                                        specific_pages=app.config["SPECIFIC_PAGES"],
                                        name=app.config["AGAS_NAME"],
                                        about=get_about(),
                                        contacts=get_contacts(),
                                        background=app.config["AGAS_BACKGROUNG"])
            else: 
                classes_with_indivs = taxonomy_with_individuals(g, NS)
                
                #print(classes_with_indivs)
                
                return render_template("jinjaT/home.html", language = app.config["LANGUAGE"], taxonomy_json=json.dumps(classes_with_indivs),
                                    u_type=app.config["USER_TYPE"],
                                    taxonomy=sorted([tax for tax in taxonomy if tax not in app.config["NOT_SHOW"]]),
                                    view_classes=app.config["VIEW_CLASSES"],
                                    dop=[res for res in results if res not in app.config["NOT_SHOW"]],
                                    individuals=[t_i for t_i in t_indivs if t_i not in app.config["NOT_SHOW"]],
                                    specific_pages=app.config["SPECIFIC_PAGES"],
                                    name=app.config["AGAS_NAME"])
        else:
            return render_template("jinjaT/homeEXP.html", language = app.config["LANGUAGE"],
                                u_type=app.config["USER_TYPE"],
                                taxonomy=sorted(taxonomy),
                                view_classes=app.config["VIEW_CLASSES"],
                                specific_pages=app.config["SPECIFIC_PAGES"])


    ############################### Classes page #############################################
    @app.route("/class/<cls>")
    def show_class(cls):   
            class_uri = NS[cls]
            #print(class_uri)
            individuals = sorted(g.subjects(RDF.type, class_uri))

            #for individual in individuals:
                #print(individual.split('/')[-1])

            properties = []

            if app.config["SEE_PROPERTIES"]:
                for prop in app.config["SEE_PROPERTIES"]:
                    if prop.startswith("has"):
                        properties.append(prop[3:])
                        
            individuals2 = sorted(g.subjects(RDF.type, OWL.NamedIndividual))
            #print(individuals2)    
            
            for ind in individuals2:
                i = ind.split("#")[-1] if "#" in ind else ind.split("/")[-1] 
                if i == cls:
                    #print(i)
                    individuals.append(ind+"_IND")
                        
            #print(individuals)
            order_path = f"{cls}.html"
            if os.path.exists(order_path):
                return render_template(order_path, cls=cls, individuals=[ind for ind in individuals if ind.split('/')[-1] not in app.config["NOT_SHOW"]], properties=properties, specific_pages=app.config["SPECIFIC_PAGES"])
            else:
                return render_template("jinjaT/class.html", cls=cls, individuals=[ind for ind in individuals if ind.split('/')[-1] not in app.config["NOT_SHOW"]], properties=properties, specific_pages=app.config["SPECIFIC_PAGES"])

    ################################ Individual page ##########################################
    @app.route("/individual/<name>")
    def show_deity(name):
        #print("HERE")
        classes = list(g.subjects(RDF.type, OWL.Class))
        pp_classes = pretty_print_uri(classes)

        prettyfy = []

        properties = []
        
        modules = {}
        
        priority = []
        
        if app.config["MODULES"] != "NONE":
            for key, value in app.config["MODULES"]:
                #print(key)
                #print(value[0])
                
                if '+' in value[0]:
                    v1=value[0].split(' + ')[0]
                    v2=value[0].split(' + ')[-1]
                    
                    modules[key]= [v1,v2]

                    #print(v1)
                    #print(v2)
                    
                else:
                    modules[key] = value[0]
                    
            #print(modules)

        if app.config["SEE_PROPERTIES"] != "NONE" or app.config["SEE_PROPERTIES"] != "None":
            for prop in app.config["SEE_PROPERTIES"]:
                properties.append(prop)
                    
        if app.config["GIVE_PRIORITY"]:
            #print("HEREGP")
            for prio in app.config["GIVE_PRIORITY"]:
                priority.append(prio)

        for thing in app.config["MAKE_PRETTY"]:
            #print("HEREMP")
            if thing.startswith("has") or thing.startswith("Has"):
                prettyfy.append(thing[3:])
            else:
                prettyfy.append(thing)

        if name in pp_classes:
            #print("HEREPP")
            class_uri = NS[name]
            individuals = sorted(g.subjects(RDF.type, class_uri))
            return render_template("jinjaT/class.html", cls=name, individuals=individuals, specific_pages=app.config["SPECIFIC_PAGES"])

        else:
            #deity_uri = NS[name.split("_")[0] if "_" in name else name]
            if app.config["ONTOLOGY_TYPE"] == "B":
                deity_uri = NS[name.split("_")[0] if "_" in name else name]
            else:
                deity_uri = NS[name]
            data = {}

            for p, o in g.predicate_objects(deity_uri):
                pred = p.split("#")[-1] if "#" in p else p.split("/")[-1]

                #print(pred)
                
                if pred not in app.config["NOT_SHOW"]:
                    if pred.startswith("has") or pred.startswith("Has"):
                        pred = pred[3:]
                        #print(pred)

                    #Assuming STORY is defined as having a title and an abstract 
                    if pred == "Story":
                        story_uri = o
                        story_title = ""
                        story_abstract = ""

                        for sp, so in g.predicate_objects(story_uri):
                            short_pred = sp.split("#")[-1] if "#" in sp else sp.split("/")[-1]
                            #print(short_pred)
                            if short_pred.startswith("has") or short_pred.startswith("Has"):
                                short_pred = short_pred[3:]

                            if short_pred == "Title":
                                story_title = str(so)
                            if short_pred == "Abstract":
                                story_abstract = str(so)
            
                        # Prepare a tuple with full story info
                        value = ((str(story_uri).replace(app.config["PREFIX"], ""), story_title, story_abstract), True)

                        data.setdefault(pred, []).append(value)
                        #print(value)
                    
                    #print(data)

                        
                    #Dealing with other modules - DSL 
                    if pred in modules.keys():
                        mod_uri = o  # e.g., URI of :Description_001
                        mod_title = pred  # e.g., "Description"
                        mod_info = {}

                        # Determine which subfields we want to extract (as list)
                        subfields = modules[pred] if isinstance(modules[pred], list) else [modules[pred]]
                        for field in subfields:
                            # We assume the pattern is hasX where X is the field name
                            field_pred_uri = URIRef(app.config["PREFIX"] + "has" + field)
                            
                            # Try to get all values for this subfield
                            for _, subvalue in g.predicate_objects(mod_uri):
                                subpred = _.split("#")[-1] if "#" in _ else _.split("/")[-1]
                                if subpred.endswith(field):
                                    # Treat as text or URI
                                    if isinstance(subvalue, URIRef) and str(subvalue).startswith(app.config["PREFIX"]):
                                        label = str(subvalue).replace(app.config["PREFIX"], "")
                                        mod_info[field] = (label, True)
                                    else:
                                        mod_info[field] = (str(subvalue), False)

                        # Now store all this info to render
                        value = (mod_info, "module")  # using "module" as a tag to distinguish it in HTML
                        data.setdefault(mod_title, []).append(value)
                        

                    else:
                        #print(o)
                        # Decide if object is a local URI, an external URI, or a literal (even if it's xsd:anyURI)
                        if str(o).startswith("http://www.w3.org"):
                            value = (str(o), False)  # Normal text
                            #print(value)
                        elif isinstance(o, URIRef) and str(o).startswith(app.config["PREFIX"]):
                            label = str(o).replace(app.config["PREFIX"], "")
                            value = (label, True)  # Internal link
                        elif isinstance(o, URIRef):
                            label = str(o)
                            value = (label, True)  # External URI
                            #print(value)
                        elif hasattr(o, 'datatype') and o.datatype and 'anyURI' in str(o.datatype):
                            label = str(o)
                            value = (label, True)  # Literal typed as anyURI (image, external link)
                            #print(value)
                        else:
                            value = (str(o), False)  # Normal text
                            
                        #print(value)

                        data.setdefault(pred, []).append(value)

            #print(data)
            #print(prettyfy)
            #print(properties)
            #print(app.config["MODULES"])
        
        order_path = f"static/orders/{name}.json"
        if os.path.exists(order_path):
            with open(order_path) as f:
                custom_order = json.load(f)
            # Move keys in `data` based on the custom order
            ordered = {key: data[key] for key in custom_order if key in data}
            # Append missing keys
            for key in data:
                if key not in ordered:
                    ordered[key] = data[key]
            data = ordered
        
        #print(priority)
        #print(data)
        order_path = f"{name}.html"
        if os.path.exists(order_path):
            print("HERE")
            return render_template(order_path, name=name, data=data, make_pretty=prettyfy, properties=properties, specific_pages=app.config["SPECIFIC_PAGES"], listsDirection = app.config["L_DISPOSITION"], u_type=app.config["USER_TYPE"], modules=modules,priority=priority)
        elif app.config["ONTOLOGY_TYPE"] == "A":
            print("HEREA")
            #print(data)
            return render_template("jinjaT/typeA.html", name=name, data=data, make_pretty=prettyfy, properties=properties, specific_pages=app.config["SPECIFIC_PAGES"], listsDirection = app.config["L_DISPOSITION"], u_type=app.config["USER_TYPE"], modules=modules, priority=priority)
        elif app.config["ONTOLOGY_TYPE"] == "C1":
            print("HEREC1")
            return render_template("jinjaT/individual.html", name=name, data=data, make_pretty=prettyfy, properties=properties, specific_pages=app.config["SPECIFIC_PAGES"], listsDirection = app.config["L_DISPOSITION"], u_type=app.config["USER_TYPE"], modules=modules,priority=priority)
        else:
            print("HERET")
            #print("HERE_INDIVST")
            return render_template("jinjaT/indivsT.html", name=name, data=data, make_pretty=prettyfy, properties=properties, specific_pages=app.config["SPECIFIC_PAGES"], listsDirection = app.config["L_DISPOSITION"], u_type=app.config["USER_TYPE"], modules=modules, priority=priority)
            
            
    ############################# To save the order and fix it #####################################################        
    @app.route("/save_order/<name>", methods=["POST"])
    def save_order(name):
        data = request.get_json()
        order = data.get("order", [])

        safe_name = secure_filename(name)
        path = f"static/orders/{safe_name}.json"

        # Ensure orders folder exists
        os.makedirs("static/orders", exist_ok=True)

        # Double check it's not a directory
        if os.path.isdir(path):
            return jsonify(success=False, error="Path is a directory!")

        with open(path, "w") as f:
            json.dump(order, f)

        return jsonify(success=True)

    ############################# To edit and save the code editing of an individual #####################################################
    @app.route('/get_individual_code')
    def get_individual_code():
        name1 = request.args.get("name")
        name = name1.split('_IND')[0] if '_IND' in name1 else name1
        individual_uri = NS[name.split('_IND')[0] if '_IND' in name else name]
        
        #print(individual_uri)

        query_str = f"""
            PREFIX : <{app.config["PREFIX"]}>
            SELECT ?subject ?predicate ?object WHERE {{
                {{ :{name} ?predicate ?object }} UNION {{ ?subject ?predicate :{name} }}
            }}
        """

        results = g.query(query_str)
        #print(results)

        # Now format to Turtle-style string
        lines = [f"###  {individual_uri}"]
        indiv = f":{name}"
        pred_obj_map = defaultdict(list)

        for row in results:
            s = row.subject or individual_uri
            p = row.predicate
            o = row.object

            if s != individual_uri:
                continue  # Only show triples *about* the individual

            pred_obj_map[p].append(o)

        formatted = []
        for pred, objs in pred_obj_map.items():   
            #pred_str = ":a" if pred == RDF.type else f":{pred.split('/')[-1]}"
            #print(pred)
            if pred == RDF.type:
                #print(pred)
                pred_str = ":a" 
                
            else:
                #print(pred) 
                pred_str = f":{pred.split('#')[-1] if '#' in pred else pred.split('/')[-1]}"
                #print(pred_str)
            
            obj_strs = []

            for obj in objs:
                #print(obj)
                
                if isinstance(obj, URIRef):
                    #obj_strs.append(f":{obj.split('/')[-1]}" if str(obj).startswith(PREFIX) else f"<{obj}>")
                    if str(obj).startswith(app.config["PREFIX"]):
                        obj_strs.append(f":{obj.split('#')[-1] if '#' in obj else obj.split('/')[-1]}")
                    else: 
                        obj_strs.append(f"<{obj}>")
                        
                elif isinstance(obj, Literal):
                    datatype = obj.datatype
                    if datatype == XSD.anyURI:
                        obj_strs.append(f"\"{obj}\"^^xsd:anyURI")
                    elif datatype == XSD.string or datatype is None:
                        obj_strs.append(f"\"{obj}\"^^xsd:string")
                    else:
                        obj_strs.append(f"\"{obj}\"^^<{datatype}>")
                else:
                    obj_strs.append(f"\"{obj}\"")

            joined = ",\n        ".join(obj_strs)
            if pred == RDF.type:
                formatted.insert(0, f"a {joined}")
            else:
                formatted.append(f"{pred_str} {joined}")

        if formatted:
            indiv += " " + " ;\n    ".join(formatted) + " ."

        lines.append(indiv)
        return "\n".join(lines), 200

    @app.route("/save_individual_code", methods=["POST"])
    def save_individual_code():
        data = request.get_json()
        name1 = data.get("name")
        name = name1.split('_IND')[0] if '_IND' in name1 else name1
        content = data.get("content")

        if not name or not content:
            return jsonify({"error": "Missing name or content"}), 400

        try:
            uri = NS[name]
            print(uri)

            # Remove old triples related to the individual
            g.remove((uri, None, None))
            g.remove((None, None, uri))

            # Wrap the fragment with proper Turtle syntax (prefix + code)
            ttl = f"""
    @prefix : <{app.config["PREFIX"]}> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix xml: <http://www.w3.org/XML/1998/namespace> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

    {content}
    """

            # Parse it into a temporary graph
            temp_g = Graph()
            temp_g.parse(data=ttl, format="turtle")
            
            print(temp_g)

            # Add only the relevant triples to the main graph
            for triple in temp_g.triples((uri, None, None)):
                g.add(triple)

            # Save the full updated graph TODO -> Nothing, this works fine, so far
            #g.serialize(destination="~/Desktop/AGAS_FILES/saved_ontology.ttl", format="turtle")
            g.serialize(destination=app.config["ONTOLOGY_FILE"])
            
            app.config["ONTOLOGY_FILE"] = save_new_version(g)
            #g.parse(app.config["ONTOLOGY_FILE"])
                
            if app.config["ONTOLOGY_FILE"].endswith('.rdf'):
                g.parse(app.config["ONTOLOGY_FILE"], format="xml")  # Assuming the input file is in RDF/XML format
                # Serialize the graph to RDF/XML
                output_path = os.path.expanduser("~/agas/output.rdf")
                # Make sure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                g.serialize(destination=output_path, format="xml")

            elif app.config["ONTOLOGY_FILE"].endswith('.ttl'):
                g.parse(app.config["ONTOLOGY_FILE"], format="turtle")
                # Serialize the graph to Turtle format
                output_path = os.path.expanduser("~/agas/output_file.ttl")
                # Make sure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                g.serialize(destination=output_path, format="turtle")

            elif app.config["ONTOLOGY_FILE"].endswith('.owl'):
                g.parse(app.config["ONTOLOGY_FILE"], format="xml")
                # Serialize to OWL/XML
                output_path = os.path.expanduser("~/agas/output_file.owl")
                # Make sure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                g.serialize(destination=output_path, format="xml")

            return jsonify({"success": True})
        
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    ############################# See relation x -> y #############################################

    @app.route("/property/<prop>/<value>")
    def show_property(prop, value):
        """
        Show all individuals that have NS[prop] → NS[value].
        E.g. /property/hasWeakness/Hydra
        """
        
        prop_uri  = NS[prop]
        value_uri = NS[value]
        
        print(prop_uri)
        print(value_uri)
        
        # find all subjects ?s with ( ?s prop_uri value_uri )
        individuals = sorted(g.subjects(prop_uri, value_uri))
        print(individuals)
        
        
        # strip the prefix for display
        individuals = [str(i).replace(app.config["PREFIX"], "") for i in individuals]
        return render_template(
            "jinjaT/property.html",
            prop=prop,
            value=value,
            individuals=individuals,
            specific_pages=app.config["SPECIFIC_PAGES"]
        )



    ################################ Support routes ##########################################
    @app.route("/search")
    def search():
        query = request.args.get("query", "").strip().lower()

        found_uri = None
        label = None

        # Search for classes and individuals by suffix match
        for s in g.subjects():
            if isinstance(s, URIRef):
                local_name = s.split("/")[-1].split("#")[-1].lower()
                if local_name == query:
                    found_uri = s
                    label = s.split("/")[-1].split("#")[-1]
                    break

        if found_uri:
            # Detect if it’s a class or an individual
            if (found_uri, RDF.type, OWL.Class) in g:
                return redirect(url_for("show_class", cls=label))
            else:
                return redirect(url_for("show_deity", name=label))

        return render_template("jinjaT/not_found.html", query=query)

    @app.route("/autocomplete")
    def autocomplete():
        term = request.args.get("q", "").lower()
        suggestions = []

        for s in g.subjects():
            if isinstance(s, URIRef):
                local_name = s.split("/")[-1].split("#")[-1]
                if term in local_name.lower() and local_name not in suggestions:
                    suggestions.append(local_name)

        return jsonify(suggestions[:10])  # Limit to 10 matches

    @app.route('/autocompleteClasses')
    def autocompleteClasses():
        q = request.args.get("q", "").lower()

        results = set()

        for s in g.subjects(RDF.type, OWL.Class):
            label = str(s).split("#")[-1] if "#" in str(s) else str(s).split("/")[-1]
            if q in label.lower():
                results.add(label)

        return jsonify(sorted(results))

    @app.route('/autocompleteDOP')
    def autocompleteDOP():
        q = request.args.get("q", "").lower()

        results = set()

        for s in g.subjects(RDF.type, OWL.DatatypeProperty):
            label = str(s).split("#")[-1] if "#" in str(s) else str(s).split("/")[-1]
            if q in label.lower():
                results.add(label)

        for s in g.subjects(RDF.type, OWL.ObjectProperty):
            label = str(s).split("#")[-1] if "#" in str(s) else str(s).split("/")[-1]
            if q in label.lower():
                results.add(label)

        return jsonify(sorted(results))


    @app.route("/about")
    def about():
        stats = get_about()
                    
        return render_template("about.html", stats=stats)


    @app.route('/contacts')
    def contacts():
        stats = get_contacts()

        return render_template('contacts.html', stats=stats, language = app.config["LANGUAGE"])


    @app.route('/AGAS')
    def agas():     
        return render_template('AGAS.html', language = app.config["LANGUAGE"])

    ################################ Ask query via normal text ##########################################
    #@app.route('/ask', methods=['GET', 'POST'])
    # def ask_query():
    #    response = None
    #    sparql_query = "Await for query to show after asking..."
    #    if request.method == 'POST':
    #        user_question = request.form['question']
            # Step 2 will handle this function
    #        sparql_query = generate_and_run_sparql(user_question)
    #    return render_template('ask.html', query=sparql_query)

    ################################ RDF Graph page ##########################################
    @app.route('/ontology')
    def ontology():
        # Full graph
        full_graph_path = build_graph_image_from_ontology(g, filename="ontology_graph_full")

        # Filtered graph
        filtered_graph_path = None
        if app.config["RDF_VIEW"] != "ALL":
            filtered_graph_path = build_graph_image_from_ontology(g, app.config["RDF_VIEW"], filename="ontology_graph_filtered")
            
        print(full_graph_path)
        print(filtered_graph_path)

        return render_template('ontology.html', language = app.config["LANGUAGE"], filter = app.config["RDF_VIEW"],
                            full_graph_path=full_graph_path,
                            filtered_graph_path=filtered_graph_path)

    ################################ Protégé edit ###########################################
    @app.route('/edit_ontology')
    def edit_ontology():
        # Route to open Protégé and load the ontology file
        abs_path = os.path.abspath(app.config["ONTOLOGY_FILE"])
        
        try:
            subprocess.Popen([app.config["PROTEGE_PATH"], abs_path])
            return "Protégé opened successfully", 200
        except Exception as e:
            return f"Error opening Protégé: {e}", 500

    ################################ Convert ontology ##########################################
    # Ontology History applies
    @app.route('/convert_ontology')
    def convert_ontology():   
        print(app.config["ONTOLOGY_FILE"])
        
        if len(conversions) < 3: #When 
            if app.config["ONTOLOGY_FILE"].endswith('.rdf'):
                g.parse(app.config["ONTOLOGY_FILE"], format="xml")  # Assuming the input file is in RDF/XML format

                # Serialize the graph to Turtle format
                #g.serialize(destination="~/Desktop/AGAS_FILES/output_file.ttl", format="turtle")
                output_path = os.path.expanduser("~/agas/output_file.ttl")
                # Make sure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                g.serialize(destination=output_path, format="ttl")
                
                app.config["ONTOLOGY_FILE"] = output_path
                conversions.append(app.config["ONTOLOGY_FILE"])

            elif app.config["ONTOLOGY_FILE"].endswith('.ttl'):
                g.parse(app.config["ONTOLOGY_FILE"], format="turtle")

                # Serialize to OWL/XML
                output_path = os.path.expanduser("~/agas/output_file.owl")
                # Make sure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                g.serialize(destination=output_path, format="xml")
                app.config["ONTOLOGY_FILE"] = output_path
                conversions.append(app.config["ONTOLOGY_FILE"])

            elif app.config["ONTOLOGY_FILE"].endswith('.owl'):
                g.parse(app.config["ONTOLOGY_FILE"], format="xml")

                # Serialize the graph to RDF/XML
                output_path = os.path.expanduser("~/agas/output.rdf")
                # Make sure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                g.serialize(destination=output_path, format="xml")
                app.config["ONTOLOGY_FILE"] = output_path
                conversions.append(app.config["ONTOLOGY_FILE"])
        else:
            if app.config["ONTOLOGY_FILE"].endswith('.rdf'):
                for conversion in conversions:
                    if conversion.endswith('.ttl'):
                        # Serialize the graph to Turtle format
                        output_path = os.path.expanduser("~/agas/output_file.ttl")
                        g.serialize(destination=output_path, format="ttl")
                        app.config["ONTOLOGY_FILE"] = conversion

            elif app.config["ONTOLOGY_FILE"].endswith('.ttl'):
                for conversion in conversions:
                    if conversion.endswith('.owl'):
                        # Serialize to OWL/XML
                        output_path = os.path.expanduser("~/agas/output_file.owl")
                        g.serialize(destination=output_path, format="xml")
                        app.config["ONTOLOGY_FILE"] = conversion

            elif app.config["ONTOLOGY_FILE"].endswith('.owl'):
                for conversion in conversions:
                    if conversion.endswith('.rdf'):
                        # Serialize the graph to RDF/XML
                        output_path = os.path.expanduser("~/agas/output.rdf")
                        g.serialize(destination=output_path, format="xml")
                        app.config["ONTOLOGY_FILE"] = conversion
        
        print(app.config["ONTOLOGY_FILE"])
        
        app.config["ONTOLOGY_FILE"] = save_new_version(g)
        g.parse(app.config["ONTOLOGY_FILE"])

        return app.config["ONTOLOGY_FILE"]

    ################################ Sync + Save onto ##########################################
    # To format the ontology segments for Monaco
    ## Fine, I think
    def format_class_axioms(filename=None):
        ontology_path = filename or app.config["ONTOLOGY_FILE"]
        if ontology_path.endswith('.ttl'):
            g.parse(ontology_path, format="turtle")
        elif ontology_path.endswith('.rdf'):
            g.parse(ontology_path, format="xml")
        elif ontology_path.endswith('.owl'):
            g.parse(ontology_path, format="xml")
        
        lines = []
        
        for cls in g.subjects(RDF.type, OWL.Class):
            lines.append(f"###  {cls}")
            no_slash = cls.split('/')[-1]
            if "#" in cls:
                lines.append(f":{no_slash.split('#')[-1]} rdf:type owl:Class")
            else: 
                lines.append(f":{no_slash} rdf:type owl:Class")
            
            supers = list(g.objects(cls, RDFS.subClassOf))
            if supers:
                lines[-1] += " ;"
                unique_restrictions = []
                others = []

                for sup in supers:
                    if isinstance(sup, BNode):
                        restr = []
                        for p, o in g.predicate_objects(sup):
                            p_short = p.split('#')[-1] if '#' in p else p.split('/')[-1]
                            if isinstance(o, URIRef):
                                #o_short = o.split('/')[-1]
                                o_short = o.split('#')[-1] if '#' in o else o.split('/')[-1]
                            else:
                                o_short = str(o)
                            restr.append(f"owl:{p_short} :{o_short}")
                        restr_sorted = sorted(restr)
                        restr_str = "            [ rdf:type owl:Restriction ;\n              " + " ;\n              ".join(restr_sorted) + "\n            ]"
                        if restr_str not in unique_restrictions:
                            unique_restrictions.append(restr_str)
                    else:
                        others.append(f"           rdfs:subClassOf :{sup.split('#')[-1] if '#' in sup else sup.split('/')[-1]}")

                # Combine all restrictions and others for final output
                all_supers = unique_restrictions + others
                for i, item in enumerate(all_supers):
                    sep = " ," if i < len(all_supers) - 1 else " ."
                    lines.append(item + sep)
            else:
                lines[-1] += " ."

            lines.append("")
        return "\n".join(lines)

    def format_Oproperties(filename=None):
        ontology_path = filename or app.config["ONTOLOGY_FILE"]
        if ontology_path.endswith('.ttl'):
            g.parse(ontology_path, format="turtle")
        elif ontology_path.endswith('.rdf'):
            g.parse(ontology_path, format="xml")
        elif ontology_path.endswith('.owl'):
            g.parse(ontology_path, format="xml")

        lines = []
        for s in g.subjects(RDF.type, OWL.ObjectProperty):
            lines.append(f"###  {s}")
            domain = next(g.objects(s, RDFS.domain), None)
            range_ = next(g.objects(s, RDFS.range), None)
            lines.append(f":{s.split('#')[-1] if '#' in s else s.split('/')[-1]} rdf:type owl:ObjectProperty ;")
            if domain:
                lines.append(f"          rdfs:domain :{domain.split('#')[-1] if '#' in domain else domain.split('/')[-1]} ;")
            if range_:
                lines.append(f"          rdfs:range :{range_.split('#')[-1] if '#' in range_ else range_.split('/')[-1]} .")
            lines.append("")
        return "\n".join(lines)

    def format_Dproperties(filename=None):
        ontology_path = filename or app.config["ONTOLOGY_FILE"]
        if ontology_path.endswith('.ttl'):
            g.parse(ontology_path, format="turtle")
        elif ontology_path.endswith('.rdf'):
            g.parse(ontology_path, format="xml")
        elif ontology_path.endswith('.owl'):
            g.parse(ontology_path, format="xml")
            
        lines = []
        for s in g.subjects(RDF.type, OWL.DatatypeProperty):
            lines.append(f"###  {s}")
            domain = next(g.objects(s, RDFS.domain), None)
            range_ = next(g.objects(s, RDFS.range), None)
            lines.append(f":{s.split('#')[-1] if '#' in s else s.split('/')[-1]} rdf:type owl:DatatypeProperty ;")
            if domain:
                lines.append(f"             rdfs:domain :{domain.split('#')[-1] if '#' in domain else domain.split('/')[-1]} ;")
            if range_:
                lines.append(f"             rdfs:range {range_.split('/')[-1].split('#')[-1] if isinstance(range_, URIRef) else range_} .")
            lines.append("")
        return "\n".join(lines)

    def format_individuals(filename=None):
        ontology_path = filename or app.config["ONTOLOGY_FILE"]
        if ontology_path.endswith('.ttl'):
            g.parse(ontology_path, format="turtle")
        elif ontology_path.endswith('.rdf'):
            g.parse(ontology_path, format="xml")
        elif ontology_path.endswith('.owl'):
            g.parse(ontology_path, format="xml")
        
        lines = []

        seen = set()  # To track already processed individuals

        for s, p, o in g.triples((None, RDF.type, None)):
            if o not in [OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty]:
                if app.config["PREFIX"] in s and s not in seen:
                    seen.add(s)  # Mark as processed

                    lines.append(f"###  {s}")
                    indiv = f":{s.split('#')[-1] if '#' in s else s.split('/')[-1]}"
                    
                    # Collect all predicates and their objects
                    pred_obj_map = defaultdict(list)
                    for pred, obj in g.predicate_objects(subject=s):
                        pred_obj_map[pred].append(obj)

                    formatted = []

                    for pred, objs in pred_obj_map.items():
                        pred_str = ":a" if pred == RDF.type else f":{pred.split('/')[-1].split('#')[-1]}"
                        obj_strs = []

                        for obj in objs:
                            if isinstance(obj, URIRef):
                                if str(obj).startswith(app.config["PREFIX"]):
                                    obj_strs.append(f":{obj.split('/')[-1].split('#')[-1]}")
                                else:
                                    obj_strs.append(f"<{obj}>")
                            elif isinstance(obj, Literal):
                                datatype = obj.datatype
                                lang = obj.language
                                if datatype == XSD.anyURI:
                                    obj_strs.append(f"\"{obj}\"^^xsd:anyURI")
                                elif datatype == XSD.string or datatype is None:
                                    obj_strs.append(f"\"{obj}\"^^xsd:string")
                                else:
                                    obj_strs.append(f"\"{obj}\"^^<{datatype}>")
                            else:
                                obj_strs.append(f"\"{obj}\"")

                        # Comma-separated objects
                        joined_objs = ",\n        ".join(obj_strs)
                        if pred == RDF.type:
                            formatted.insert(0, f"a {joined_objs}")
                        else:
                            formatted.append(f"{pred_str} {joined_objs}")

                    # Construct the final individual block
                    if formatted:
                        indiv += " " + " ;\n    ".join(formatted) + " ."
                    lines.append(indiv)
                    lines.append("")

        return "\n".join(lines)


    @app.route("/get_raw_ontology", defaults={"filename": None})
    @app.route("/get_raw_ontology/<filename>")
    def get_raw_ontology(filename):
        """
        Returns the raw TTL content of either:
        - The currently active ontology (if no filename passed)
        - A specific version file (if filename provided)
        """
        if filename:
            # Case 1: explicit version requested
            ontology_path = os.path.join(app.config["VERSIONS_DIR"], filename)
        else:
            # Case 2: default to active ontology
            ontology_path = app.config["ONTOLOGY_FILE"]

        if not os.path.exists(ontology_path):
            return "Ontology file not found", 404

        with open(ontology_path, "r", encoding="utf-8") as f:
            return f.read()

    @app.route("/get_classes_raw", defaults={"filename": None})
    @app.route("/get_classes_raw/<filename>")
    def get_classes_raw(filename):
        return format_class_axioms(
            os.path.join(app.config["VERSIONS_DIR"], filename)
            if filename else None
        )

    @app.route("/get_data_properties_raw", defaults={"filename": None})
    @app.route("/get_data_properties_raw/<filename>")
    def get_Dproperties_raw(filename):
        return format_Dproperties(
            os.path.join(app.config["VERSIONS_DIR"], filename)
            if filename else None
        )

    @app.route("/get_object_properties_raw", defaults={"filename": None})
    @app.route("/get_object_properties_raw/<filename>")
    def get_Oproperties_raw(filename):
        return format_Oproperties(
            os.path.join(app.config["VERSIONS_DIR"], filename)
            if filename else None
        )

    @app.route("/get_individuals_raw", defaults={"filename": None})
    @app.route("/get_individuals_raw/<filename>")
    def get_individuals_raw(filename):
        return format_individuals(
            os.path.join(app.config["VERSIONS_DIR"], filename)
            if filename else None
        )

    # Route to reload the edited ontology file and sync it with the browser
    @app.route('/sync_ontology')
    def sync_ontology():
        #print(app.config["ONTOLOGY_FILE"])
        with open(app.config["ONTOLOGY_FILE"], 'r') as file:
            with open("ontology_content.txt", 'w') as ontology_content:
                for line in file:
                #    if "#    Individuals" in line:  # Stop when reaching Individuals
                #        break
                    ontology_content.write(line)

        with open("ontology_content.txt") as ontology_content:
            sync = ontology_content.read()
        return sync  # This returns the updated ontology content

    # Route to save the edited ontology file and sync it with the files 
    # TODO: change how we save because original is wrong and saving is wrong, might have to do with encoding? Not sure, we'll see. TODO:
    @app.route("/save_ontology", methods=["POST"])
    def save_ontology():
        data = request.get_json()
        content = data.get("content")
        section = data.get("section", "full")

        #print(data)
        #print(content)
        #print(section)

        if not content:
            return jsonify({"error": "No content provided"}), 400

        if section == "full":
            # Write updated text (with markers) into the editable ontology file
            with open(app.config["ONTOLOGY_FILE"], "w", encoding="utf-8") as f:
                f.write(content)

            g.remove((None, None, None))  # clears all triples
            # Re-parse so g = new ontology
            if app.config["ONTOLOGY_FILE"].endswith('.ttl'):
                g.parse(app.config["ONTOLOGY_FILE"], format="turtle")
            elif app.config["ONTOLOGY_FILE"].endswith('.rdf'):
                g.parse(app.config["ONTOLOGY_FILE"], format="xml")
            elif app.config["ONTOLOGY_FILE"].endswith('.owl'):
                g.parse(app.config["ONTOLOGY_FILE"], format="xml")

            save_new_version(g)
            
            if app.config["ONTOLOGY_FILE"].endswith('.rdf'):
                output_path = os.path.expanduser("~/agas/output.rdf")
                # Make sure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                g.serialize(destination=output_path, format="xml")
            elif app.config["ONTOLOGY_FILE"].endswith('.ttl'):
                output_path = os.path.expanduser("~/agas/output_file.ttl")
                # Make sure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                g.serialize(destination=output_path, format="ttl")
            elif app.config["ONTOLOGY_FILE"].endswith('.owl'):
                output_path = os.path.expanduser("~/agas/output_file.owl")
                # Make sure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                g.serialize(destination=output_path, format="xml")

            return jsonify({"success": True}), 200

        #print(app.config["ONTOLOGY_FILE"])
        # Read full ontology file
        with open(app.config["ONTOLOGY_FILE"], "r", encoding="utf-8") as f:
            original = f.read()
            
            #print(f.readlines())

        # Define section markers (update these if your TTL format differs)
        markers = {
            "classes": ("#    Classes", "#    Individuals"),
            "dataproperties": ("#    Data properties", "#    Classes"),
            "objectproperties": ("#    Object properties", "#    Data properties"),
            "individuals": ("#    Individuals", "### End"),
        }


        start_marker, end_marker = markers.get(section, (None, None))
        if not start_marker or not end_marker:
            return jsonify({"error": "Invalid section"}), 400

        #print(start_marker)
        #print(end_marker)
        
        # Split and replace the relevant section
        pattern = re.compile(
            f"{re.escape(start_marker)}(.*?){re.escape(end_marker)}",
            re.DOTALL
        )

        new_section = f"{start_marker}\n{content.strip()}\n{end_marker}"
        updated = re.sub(pattern, new_section, original)
        
        #print(original)
        print(pattern)
        print(new_section) #IS CORRECT
        #print(updated)

        #print(app.config["ONTOLOGY_FILE"])
        # Write updated text (with markers) into the editable ontology file
        with open(app.config["ONTOLOGY_FILE"], "w", encoding="utf-8") as f:
            f.write(updated)

        g.remove((None, None, None))  # clears all triples
        # Re-parse so g = new ontology
        if app.config["ONTOLOGY_FILE"].endswith('.ttl'):
            g.parse(app.config["ONTOLOGY_FILE"], format="turtle")
        elif app.config["ONTOLOGY_FILE"].endswith('.rdf'):
            g.parse(app.config["ONTOLOGY_FILE"], format="xml")
        elif app.config["ONTOLOGY_FILE"].endswith('.owl'):
            g.parse(app.config["ONTOLOGY_FILE"], format="xml")

        save_new_version(g)
        
        if app.config["ONTOLOGY_FILE"].endswith('.rdf'):
            output_path = os.path.expanduser("~/agas/output.rdf")
            # Make sure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            g.serialize(destination=output_path, format="xml")
        elif app.config["ONTOLOGY_FILE"].endswith('.ttl'):
            output_path = os.path.expanduser("~/agas/output_file.ttl")
            # Make sure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            g.serialize(destination=output_path, format="ttl")
        elif app.config["ONTOLOGY_FILE"].endswith('.owl'):
            output_path = os.path.expanduser("~/agas/output_file.owl")
            # Make sure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            g.serialize(destination=output_path, format="xml")

        
        return jsonify({"success": True}), 200

    ################################ SPARQL query the ontology ##########################################
    @app.route('/sparql', methods=['POST'])
    def sparql_query():
        try:
            query = request.json.get("query", "")
            if not query:
                return jsonify({"error": "No SPARQL query provided"}), 400
            
            # Auto prepend the PREFIX if it's not in the query already
            if "PREFIX" not in query.upper():
                prefix_line = f"PREFIX : <{app.config["PREFIX"]}>\n"
                query = prefix_line + query
                
            #print(query)

            results = g.query(query)

            headers = results.vars  # Variable names from SELECT -> FINAL TRY!!!
            rows = []

            for row in results:
                cells = []
                for var in headers:
                    val = row.get(var)
                    if val is not None and isinstance(val, URIRef):
                        cells.append(pretty_print_uri([val])[0])
                    else:
                        cells.append(str(val) if val is not None else "")
                rows.append(cells)

            final = {
                "head": [str(h) for h in headers],
                "rows": rows
            }

            file_path = os.path.join(app.config["RESULTS_DIR"], "results.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(final, f, indent=4)

            return jsonify({"message": "Query successful!", "redirect": "/results"})

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    ################################ BQ + SPARQL res pages -> with pagination ##########################################
    @app.route('/results')
    def show_results():
        file_path = os.path.join(app.config["RESULTS_DIR"], "results.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return render_template("jinjaT/results.html", results=data)
        else:
            return "No results found. Please run a query first."

    @app.route('/resultsBQ')
    def results_page():    
        things=[]

        for s in g.subjects():
            t= str(s).split("#")[-1] if "#" in str(s) else str(s).split("/")[-1]

            if t not in things:
                things.append(t)

        #print(f"Things: {things}")

        if app.config["USER_TYPE"] == "EXP":
            per_page = 5  # Can change to whatever feels natural
        else:
            per_page = 10

        page = int(request.args.get("page", 1))
        total = len(app.config["BASE_QUERIES"])
        total_pages = (total + per_page - 1) // per_page

        start = (page - 1) * per_page
        end = start + per_page
        paged_queries = app.config["BASE_QUERIES"][start:end]

        final_queries = []
        queries_with_placeholders = []
        placeholders = []

        for value, query in paged_queries:
            #if "PREFIX" not in query[0]:
            #    prefix_line = f"\nPREFIX : <{app.config["PREFIX"]}>"
            #    query_final = prefix_line + query[0]
                
            final_queries.append((value, query[0]))
            # In your Flask route:

            placeholders = extract_placeholders(query)
            queries_with_placeholders.append((value, query[0], placeholders))

        #print(final_queries)
        #print(placeholders)
        #print(queries_with_placeholders)

        return render_template('results.html', language = app.config["LANGUAGE"],
                            u_type=app.config["USER_TYPE"],
                            queries=final_queries,
                            page=page,
                            total_pages=total_pages,
                            start_index=start,
                            queries_with_placeholders=queries_with_placeholders,
                            things=list(things))

    @app.route('/show_bq/<int:index>', methods=['GET', 'POST'])
    def show_bq(index):
        page = int(request.args.get("page", 1))
        per_page = 25

        if index < 0 or index >= len(app.config["BASE_QUERIES"]):
            return "Invalid query", 404

        read_file = int(request.args.get("file", 0))  # Default to 0 if not provided

        file_path = os.path.join(app.config["RESULTS_DIR"], "resultsBQ.json")

        if read_file == 1:
            # Read from saved results
            with open(file_path, "r", encoding="utf-8") as f:
                info = json.load(f)
            headers = info["head"]
            all_rows = info["rows"]

        else:
            #print("HERE")

            # Load ontology
            if app.config["ONTOLOGY_FILE"].endswith('.rdf'):
                g.parse(app.config["ONTOLOGY_FILE"], format="xml")
            elif app.config["ONTOLOGY_FILE"].endswith('.ttl'):
                g.parse(app.config["ONTOLOGY_FILE"], format="turtle")
            elif app.config["ONTOLOGY_FILE"].endswith('.owl'):
                g.parse(app.config["ONTOLOGY_FILE"], format="xml")

            all_rows = []
            headers = []

            #print(request.method)

            if request.method == 'POST':
                #print("HEREPOST")
                if 'edited_query' in request.form:
                    # Handle direct query editing
                    query = request.form['edited_query']
                    if "PREFIX" not in query:
                        prefix_line = f"\nPREFIX : <{app.config["PREFIX"]}>"
                        query = prefix_line + query
                    q_result = g.query(query)

                    headers = [str(h) for h in q_result.vars]
                    for row in q_result:
                        all_rows.append([
                            pretty_print_uri([row.get(var)])[0] if isinstance(row.get(var), URIRef)
                            else str(row.get(var) or "")
                            for var in q_result.vars
                        ])

                elif any(k.startswith("placeholder_") for k in request.form.keys()):
                    # Handle placeholder-based form (non-logged-in users)
                    base_query = app.config["BASE_QUERIES"][index][1][0]  # raw query with :<...> placeholders
                    placeholder_map = {}

                    # Parse all placeholder inputs
                    for key, value in request.form.items():
                        if key.startswith("placeholder_"):
                            try:
                                parsed = json.loads(value)
                                key_name = key.replace("placeholder_", "")
                                if isinstance(parsed, list):
                                    placeholder_map[key_name] = [item["value"] for item in parsed]
                                else:
                                    placeholder_map[key_name] = [parsed["value"]]
                            except Exception as e:
                                print(f"Error parsing {key}: {e}")

                    # Replace placeholders in base_query
                    # Ensure all placeholders are present
                    placeholders = re.findall(r":<([^>]+)>", base_query)
                    value_lists = [placeholder_map.get(ph, []) for ph in placeholders]

                    # Cartesian product of all placeholder values
                    combinations = list(product(*value_lists))

                    for combo in combinations:
                        query = base_query
                        for ph, val in zip(placeholders, combo):
                            replacement = ":" + val if not val.startswith(":") else val
                            query = re.sub(rf":<{ph}>", replacement, query)

                        #print("Executing query:", query)
                        try:
                            if "PREFIX" not in query:
                                prefix_line = f"\nPREFIX : <{app.config["PREFIX"]}>"
                                query = prefix_line + query
                            q_result = g.query(query)
                            headers = [str(h) for h in q_result.vars]
                            for row in q_result:
                                all_rows.append([
                                    pretty_print_uri([row.get(var)])[0] if isinstance(row.get(var), URIRef)
                                    else str(row.get(var) or "")
                                    for var in q_result.vars
                                ])
                        except Exception as e:
                            print(f"Error executing query for combo {combo}:", e)

                else:
                    # Default GET base query
                    query = app.config["BASE_QUERIES"][index][1][0]
                    #print(query)
                    if "PREFIX" not in query:
                        prefix_line = f"\nPREFIX : <{app.config["PREFIX"]}>"
                        query = prefix_line + query
                    q_result = g.query(query)
                    headers = [str(h) for h in q_result.vars]
                    for row in q_result:
                        all_rows.append([
                            pretty_print_uri([row.get(var)])[0] if isinstance(row.get(var), URIRef)
                            else str(row.get(var) or "")
                            for var in q_result.vars
                        ])
            else:
                # Default GET base query
                query = app.config["BASE_QUERIES"][index][1][0]
                #print(query)
                if "PREFIX" not in query:
                    prefix_line = f"\nPREFIX : <{app.config["PREFIX"]}>"
                    query = prefix_line + query
                q_result = g.query(query)
                headers = [str(h) for h in q_result.vars]
                for row in q_result:
                    all_rows.append([
                        pretty_print_uri([row.get(var)])[0] if isinstance(row.get(var), URIRef)
                        else str(row.get(var) or "")
                        for var in q_result.vars
                    ])

            # Save results to file for pagination reuse
            final = {"head": headers, "rows": all_rows}
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(final, f, indent=4)

        # Pagination
        total = len(all_rows)
        start = (page - 1) * per_page
        end = start + per_page
        paged_rows = all_rows[start:end]
        total_pages = (total + per_page - 1) // per_page

        return render_template("bq.html",
                            index=index,
                            headers=headers,
                            rows=paged_rows,
                            page=page,
                            total_pages=total_pages)

    ################################ get OP, DP, C, I of onto ##########################################
    @app.route('/get_class_properties')
    def get_class_properties():
        class_name = request.args.get('class')
        if not class_name:
            return jsonify({"data_properties": [], "object_properties": []})

        g = Graph()
        g.parse(app.config["ONTOLOGY_FILE"])

        full_class_uri = URIRef(f"{app.config["PREFIX"]}{class_name}")

        # 🧠 Get superclasses (transitive)
        superclasses = set()
        to_check = [full_class_uri]
        while to_check:
            current = to_check.pop()
            superclasses.add(current)
            for sup in g.objects(current, RDFS.subClassOf):
                if sup not in superclasses:
                    to_check.append(sup)

        data_props = set()
        object_props = set()

        for cls in superclasses:
            # 🧪 Get DataProperties with matching domain
            for s in g.subjects(RDF.type, OWL.DatatypeProperty):
                for domain in g.objects(s, RDFS.domain):
                    if domain == cls:
                        data_props.add(s)

            # 🧪 Get ObjectProperties with matching domain
            for s in g.subjects(RDF.type, OWL.ObjectProperty):
                for domain in g.objects(s, RDFS.domain):
                    if domain == cls:
                        object_props.add(s)

        # Strip namespaces to return clean names
        def clean(uri): return str(uri).split("#")[-1] if "#" in str(uri) else str(uri).split("/")[-1]

        return jsonify({
            "data_properties": [clean(p) for p in data_props],
            "object_properties": [clean(p) for p in object_props]
        })

    @app.route('/get_individuals')
    def get_individuals():    
        g = Graph()
        g.parse(app.config["ONTOLOGY_FILE"])

        individuals = set()
        for s in g.subjects(RDF.type, None):
            if str(s).startswith(app.config["PREFIX"]):
                individuals.add(str(s).split("#")[-1] if "#" in str(s) else str(s).split("/")[-1])

        return jsonify(sorted(individuals))

    ################################ Add Class in Onto ########################################
    @app.route('/add_class', methods=['POST'])
    def add_class():
        #if not session.get("logged_in"):   #BEFORE MAKING IT LOCKED ON HTML
        #    abort(403)  # Forbidden
        #else:    
            class_name = request.form.get('name', '').strip()
            properties_json = request.form.get('Properties: ', '[]')
            individuals_json = request.form.get('Individuals: ', '[]')

            if not class_name:
                flash("Class name is required.", "error")
                return redirect(url_for('home'))

            # Sanitize and construct URI
            class_uri = NS[class_name.replace(" ", "_")]

            # Add the new class to the graph
            g.add((class_uri, RDF.type, OWL.Class))
            #g.add((class_uri, RDFS.label, Literal(class_name)))

            try:
                properties = json.loads(properties_json)
                #print(properties_json)
                #print(properties)
            except json.JSONDecodeError:
                properties = []

            try:
                individuals = json.loads(individuals_json)
            except json.JSONDecodeError:
                individuals = []

            for prop in properties:
                prop_label = prop.get("value", "").strip()
                if prop_label:
                    prop_uri = NS[prop_label.replace(" ", "_")]
                    
                    # ✅ Check if property already exists in ontology
                    ranges = list(g.objects(prop_uri, RDFS.range))

                    if ranges:
                        # Use the existing range
                        for r in ranges:
                            restriction = BNode()
                            g.add((restriction, RDF.type, OWL.Restriction))
                            g.add((restriction, OWL.onProperty, prop_uri))
                            g.add((restriction, OWL.someValuesFrom, r))
                            g.add((class_uri, RDFS.subClassOf, restriction))
                    else:
                        # Fallback (if range not defined)
                        restriction = BNode()
                        g.add((restriction, RDF.type, OWL.Restriction))
                        g.add((restriction, OWL.onProperty, prop_uri))
                        g.add((restriction, OWL.someValuesFrom, OWL.Thing))
                        g.add((class_uri, RDFS.subClassOf, restriction))
                    
                    #g.add((class_uri, RDFS.subClassOf, prop_uri))  # or a custom property
                    # Optionally, assert the property type:
                    #g.add((prop_uri, RDF.type, RDF.Property))

            for ind in individuals:
                ind_label = ind.get("value", "").strip()
                if ind_label:
                    ind_uri = NS[ind_label.replace(" ", "_")]
                    g.add((ind_uri, RDF.type, class_uri))

            # Save updated ontology (adjust this to your save mechanism)
            #testLocal="~/Desktop/AGAS_FILES/testClass.ttl"
            #g.serialize(destination=testLocal, format="ttl")
            
            app.config["ONTOLOGY_FILE"] = save_new_version(g)
            #g.parse(app.config["ONTOLOGY_FILE"])
            
            if app.config["ONTOLOGY_FILE"].endswith('.rdf'):
                g.parse(app.config["ONTOLOGY_FILE"], format="xml")  # Assuming the input file is in RDF/XML format
                # Serialize the graph to RDF/XML
                output_path = os.path.expanduser("~/agas/output.rdf")
                # Make sure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                g.serialize(destination=output_path, format="xml")

            elif app.config["ONTOLOGY_FILE"].endswith('.ttl'):
                g.parse(app.config["ONTOLOGY_FILE"], format="turtle")
                # Serialize the graph to Turtle format
                output_path = os.path.expanduser("~/agas/output_file.ttl")
                # Make sure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                g.serialize(destination=output_path, format="ttl")

            elif app.config["ONTOLOGY_FILE"].endswith('.owl'):
                g.parse(app.config["ONTOLOGY_FILE"], format="xml")
                # Serialize to OWL/XML
                output_path = os.path.expanduser("~/agas/output_file.owl")
                # Make sure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                g.serialize(destination=output_path, format="xml")
                

            return redirect(url_for('home'))

    ################################ Add Properties in Onto ##########################################
    @app.route('/add_property', methods=['POST'])
    def add_property():
        name   = request.form['name'].strip()
        ptype  = request.form['ptype']        # 'data' or 'object'
        domain = request.form['domain'].strip()

        # Build URIs
        prop_uri   = URIRef(app.config["PREFIX"] + name)
        domain_uri = URIRef(app.config["PREFIX"] + domain)

        # Add the property type triple
        if ptype == 'data':
            g.add((prop_uri, RDF.type, OWL.DatatypeProperty))
            # range is an XSD type
            dt = request.form['range_data']    # e.g. 'string'
            range_uri = getattr(XSD, dt)
        else:
            g.add((prop_uri, RDF.type, OWL.ObjectProperty))
            # range is another class
            rng = request.form['range_obj'].strip()
            range_uri = URIRef(app.config["PREFIX"] + rng)

        # Add domain & range
        g.add((prop_uri, RDFS.domain, domain_uri))
        g.add((prop_uri, RDFS.range, range_uri))

        # Persist and feedback
        #testLocal="~/Desktop/AGAS_FILES/testProperties.ttl"
        #g.serialize(destination=testLocal, format='turtle')
        app.config["ONTOLOGY_FILE"] = save_new_version(g)
        #g.parse(app.config["ONTOLOGY_FILE"])
            
        if app.config["ONTOLOGY_FILE"].endswith('.rdf'):
            g.parse(app.config["ONTOLOGY_FILE"], format="xml")  # Assuming the input file is in RDF/XML format
            # Serialize the graph to RDF/XML
            output_path = os.path.expanduser("~/agas/output.rdf")
            # Make sure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            g.serialize(destination=output_path, format="xml")

        elif app.config["ONTOLOGY_FILE"].endswith('.ttl'):
            g.parse(app.config["ONTOLOGY_FILE"], format="turtle")
            # Serialize the graph to Turtle format
            output_path = os.path.expanduser("~/agas/output_file.ttl")
            # Make sure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            g.serialize(destination=output_path, format="ttl")

        elif app.config["ONTOLOGY_FILE"].endswith('.owl'):
            g.parse(app.config["ONTOLOGY_FILE"], format="xml")
            # Serialize to OWL/XML
            output_path = os.path.expanduser("~/agas/output_file.owl")
            # Make sure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            g.serialize(destination=output_path, format="xml")
            
              
        flash(f"Property {name} added as a {ptype} property.", "success")
        return redirect(url_for('home'))

    ################################ Add Ind in Onto ##########################################
    @app.route("/add_individual", methods=["POST"])
    def add_individual():
        name = request.form["name"]
        class_name = request.form["class"]

        # Step 1: Define safe working copy
        #original_path = app.config["ONTOLOGY_FILE"]
        #working_path = "~/Desktop/AGAS_FILES/testAddInd.ttl"

        #if original_path != working_path:
            # Step 2: Copy original ontology to working file if it doesn't exist yet
        #    if not os.path.exists(working_path):
        #        shutil.copyfile(original_path, working_path)

            #Making it so variable updates
        #    app.config["ONTOLOGY_FILE"] = working_path

        # Step 3: Load the working file into rdflib graph
        #g = Graph()
        #if working_path.endswith('.rdf') or working_path.endswith('.owl'):
        #    g.parse(working_path, format="xml")
        #elif working_path.endswith('.ttl'):
        #    g.parse(working_path, format="turtle")
        

        # Step 4: Add new individual
        uri = NS[name]
        class_uri = NS[class_name]

        # Safety check
        if (uri, None, None) in g:
            flash("Individual already exists!", "warning")
            return redirect(url_for('home'))

        g.add((uri, RDF.type, class_uri))

        #print(uri)
        #print(class_uri)
        #RES:
        #http://www.semanticweb.org/diana-teixeira/ontologies/2025/GreekDeities/A_Rando1
        #http://www.semanticweb.org/diana-teixeira/ontologies/2025/GreekDeities/Lesser

        # Get superclasses (transitive)
        superclasses = set()
        to_check = [class_uri]
        while to_check:
            current = to_check.pop()
            superclasses.add(current)
            for sup in g.objects(current, RDFS.subClassOf):
                if sup not in superclasses:
                    to_check.append(sup)

        data_props = set()
        object_props = set()

        for cls in superclasses:
            # Get DataProperties with matching domain
            for s in g.subjects(RDF.type, OWL.DatatypeProperty):
                for domain in g.objects(s, RDFS.domain):
                    if domain == cls:
                        data_props.add(s)

            # Get ObjectProperties with matching domain
            for s in g.subjects(RDF.type, OWL.ObjectProperty):
                for domain in g.objects(s, RDFS.domain):
                    if domain == cls:
                        object_props.add(s)

        # Strip namespaces to return clean names
        def clean(uri): return str(uri).split("#")[-1] if "#" in str(uri) else str(uri).split("/")[-1]

        data_props = [clean(uri) for uri in data_props]
        object_props = [clean(uri) for uri in object_props]

        #print(data_props) -> Good
        #print(object_props) #-> Good

        # Fill data properties
        for dp in data_props:
            value = request.form.get(dp)

            if value:
                g.add((uri, NS[dp], Literal(value)))

        # Fill object properties (support multi-select)
        #for op in object_props:
            #print(op) #-> GOOD
        #    others = request.form.getlist(f"{op}[]")
            #print(others) #-> ['[{"value":"Tyche"},{"value":"Phyche"}]']
        #    for other in others:
        #        print(other)
        #        if other:
                    #other_uri = NS[other]
                    #if (other_uri, None, None) in g:   #THIS WASN'T WORKING?
                    #    #print(f"Linking {uri} -> {op} -> {other_uri}")
                    #    g.add((uri, NS[op], other_uri))
        #            other_uri = NS[other]
        #            g.add((uri, NS[op], other_uri))
        #            g.add((other_uri, RDF.type, OWL.NamedIndividual))  # ensure target is kept
                    
        #            print(f"{uri} -> {NS[op]} -> {other_uri}")
                    
        for op in object_props:
            print(op) #-> GOOD
            raw_value = request.form.getlist(f"{op}[]") #-> ['[{"value":"Achelous"}]']
            
            #value = json.loads(raw_value[0])
            #print(value) #-> [{'value': 'Achelous_Story1'}, {'value': 'Achelous_Story2'}, {'value': 'Achelous_Story3'}]
                
            #if value:
            #    indivs = []
            #    for v in value: #-> [{"value":"Achelous"}] but as str
            #        print(v) # -> {'value': 'Chaos'}
                    #print(v.items()) -> dict_items([('value', 'Chaos')])
            #        print(v.get("value")) #-> Chaos
                    
            #        indivs.append(v.get("value"))
                
            #    for other in indivs:
            #        print(other)
            #        other_uri = NS[other]
            #        g.add((uri, NS[op], other_uri))
            #        g.add((other_uri, RDF.type, OWL.NamedIndividual))
            
            if not raw_value or raw_value == ['']:  # empty or not submitted
                continue

            try:
                # Parse JSON only if something was sent
                value_list = json.loads(raw_value[0])
            except (json.JSONDecodeError, IndexError):
                continue  # ignore if invalid or empty

            for v in value_list:
                val = v.get("value")
                if val:  # only add if actual value present
                    other_uri = NS[val]
                    g.add((uri, NS[op], other_uri))
                    g.add((other_uri, RDF.type, OWL.NamedIndividual))   
                         
                    print(f"{uri} -> {NS[op]} -> {other_uri}")

        #working_path = "~/Desktop/AGAS_FILES/testAddInd.ttl"
        # Step 5: Save updates only to working copy
        #g.serialize(destination=working_path, format="turtle")

        app.config["ONTOLOGY_FILE"] = save_new_version(g)
        #g.parse(app.config["ONTOLOGY_FILE"])
            
        if app.config["ONTOLOGY_FILE"].endswith('.rdf'):
            g.parse(app.config["ONTOLOGY_FILE"], format="xml")  # Assuming the input file is in RDF/XML format
            # Serialize the graph to RDF/XML
            output_path = os.path.expanduser("~/agas/output.rdf")
            # Make sure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            g.serialize(destination=output_path, format="xml")

        elif app.config["ONTOLOGY_FILE"].endswith('.ttl'):
            g.parse(app.config["ONTOLOGY_FILE"], format="turtle")
            # Serialize the graph to Turtle format
            output_path = os.path.expanduser("~/agas/output_file.ttl")
            # Make sure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            g.serialize(destination=output_path, format="ttl")

        elif app.config["ONTOLOGY_FILE"].endswith('.owl'):
            g.parse(app.config["ONTOLOGY_FILE"], format="xml")
            # Serialize to OWL/XML
            output_path = os.path.expanduser("~/agas/output_file.owl")
            # Make sure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            g.serialize(destination=output_path, format="xml")
        
        app.config["ONTOLOGY_FILE"] = save_new_version(g)           
        
        flash(f"Added individual {name} as {class_name} to working copy.", "success")
        return redirect(url_for('home'))

    ################################ Edit Ind in onto ##########################################
    @app.route("/edit/<name>", methods=["GET"])
    def edit_individual(name):
        individual_uri = NS[name.split('_IND')[0] if '_IND' in name else name]
        #print(individual_uri) # Good
        if not individual_uri:
            return "Individual not found", 404

        classes = list(g.subjects(RDF.type, OWL.Class))
        #print(classes)

        classInd = list(g.objects(individual_uri, RDF.type))
        #print(classInd)

        #classIndT= list(g.objects(individual_uri, OWL.Class))
        #print(classIndT)

        for c in classInd:
            #print(c)
            if c.startswith(app.config["PREFIX"]):
                class_uri = c
            else:
                class_uri = individual_uri    

        #print(class_uri)

        all_individuals = set()
        for s in g.subjects(RDF.type, None):
            if str(s).startswith(app.config["PREFIX"]):
                all_individuals.add(str(s).split("#")[-1] if "#" in str(s) else str(s).split("/")[-1])

        #print(all_individuals) -> Good

        # Get superclasses (transitive)
        superclasses = set()
        to_check = [class_uri]
        while to_check:
            current = to_check.pop()
            superclasses.add(current)
            for sup in g.objects(current, RDFS.subClassOf):
                if sup not in superclasses:
                    to_check.append(sup)

        #print(superclasses)

        data_props = set()
        object_props = set()

        for cls in superclasses:
            #print(cls)
            # Object properties
            for s in g.subjects(RDF.type, OWL.ObjectProperty):
                #print(s)
                for domain in g.objects(s, RDFS.domain):
                    #print(f"Property {s} has domain {domain}")
                    if domain in superclasses:
                        object_props.add(s)
                
                if g.objects(cls,s):
                    #print("HERE")
                    data_props.add(s)

            # Data properties
            for s in g.subjects(RDF.type, OWL.DatatypeProperty):
                #print(s)
                for domain in g.objects(s, RDFS.domain):
                    #print(f"Property {s} has domain {domain}")
                    if domain in superclasses:
                        data_props.add(s)
                
                if g.objects(cls,s):
                    #print("HERE")
                    data_props.add(s)

        # Strip namespaces to return clean names
        def clean(uri): return str(uri).split("#")[-1] if "#" in str(uri) else str(uri).split("/")[-1]

        object_values = {}
        data_values = {}

        for pred, obj in g.predicate_objects(individual_uri):
            pred_str = clean(pred)

            if pred in object_props:
                # Object property → accumulate multiple values
                val = str(obj).replace(app.config["PREFIX"], "")
                object_values.setdefault(pred_str, []).append(val)

            elif pred in data_props:
                # Data property → take literal
                data_values[pred_str] = str(obj)

        #print(object_values)
        #print(data_values)

        return render_template(
            "jinjaT/edit_individual.html",
            name=name,
            classes=[clean(cls) for cls in classes],
            individuals=[clean(ind) for ind in all_individuals],
            object_values= object_values, #[clean(p) for p in object_props],
            data_values=data_values,#[clean(p) for p in data_props],
            current_classes=[clean(cls) for cls in g.objects(NS[name], RDF.type)],
        )

    @app.route("/confirm_edit/<name>", methods=["POST"])
    def confirm_edit(name):
        uri = NS[name.split('_IND')[0] if '_IND' in name else name]

        # Get original class
        old_class = None
        for _, _, o in g.triples((uri, RDF.type, None)):
            if o != OWL.NamedIndividual:  # Skip owl:NamedIndividual
                old_class = o

        # Collect old and new values
        old_data = {}
        new_data = {}

        for p, o in g.predicate_objects(subject=uri):
            prop = p.split("#")[-1] if "#" in str(p) else p.split("/")[-1]
            #print(prop)
            #print(str(o).split("/")[-1])
            val = str(o).split("/")[-1]
            old_data.setdefault(prop, []).append(val)

            #if isinstance(o, Literal) or isinstance(o, URIRef):
            #    val = str(o).split("/")[-1] if isinstance(o, URIRef) else str(o)
            #    old_data.setdefault(prop, []).append(val)

        #print(old_data)

        for key in request.form:
            values = request.form.getlist(key)

            # If the value is a JSON-encoded list of dictionaries like [{"value": "xyz"}]
            if len(values) == 1 and values[0].strip().startswith("[{"):
                try:
                    parsed_values = [entry["value"] for entry in json.loads(values[0])]
                    new_data[key] = parsed_values
                except Exception as e:
                    #print(f"Error parsing JSON for {key}: {e}")
                    new_data[key] = values  # fallback
            else:
                new_data[key] = values

        #print(new_data)

        return render_template("jinjaT/confirm_edit.html",
                            name=name,
                            old_class=old_class,
                            new_class=request.form.get("class"),
                            old_data=old_data,
                            new_data=new_data)

    @app.route("/apply_edit/<name>", methods=["POST"])
    def apply_edit(name):
        uri = NS[name.split('_IND')[0] if '_IND' in name else name]

        # Remove all triples about this individual (except owl:NamedIndividual)
        g.remove((uri, None, None))

        # Add new class
        new_class = request.form.get("class")
        if new_class and new_class != "None":
            new_class_uri = NS[new_class]
            g.add((uri, RDF.type, new_class_uri))

        # Dynamically extract object properties
        q = prepareQuery("""
            SELECT ?prop WHERE {
                ?prop a owl:ObjectProperty .
            }
        """, initNs={"owl": OWL})

        object_properties = {str(row.prop).split("#")[-1].split("/")[-1] for row in g.query(q)}

        # Re-add properties (DPs or OPs based on query result)
        ''' OLD VERSION -> EDIT HAD :type thingy that was wrong!!!!!
        for key in request.form:
            clean_key = key.replace("[]", "")
            if clean_key == "class":
                continue
            for val in request.form.getlist(key):
                if clean_key in object_properties:
                    g.add((uri, NS[clean_key], NS[val]))  # Object property (URIRef)
                else:
                    g.add((uri, NS[clean_key], Literal(val)))  # Data property (Literal)
        '''

        for key in request.form:
            clean_key = key.replace("[]", "")
            if clean_key == "class":
                continue
            for val in request.form.getlist(key):
                if clean_key == "type":
                    g.add((uri, RDF.type, NS[val]))
                elif clean_key in object_properties:
                    g.add((uri, NS[clean_key], NS[val]))  # Object property
                else:
                    print(clean_key)
                    print(val)
                    g.add((uri, NS[clean_key], Literal(val)))  # Data property

        #working_path = "~/Desktop/AGAS_FILES/testEdit.ttl"
        #g.serialize(destination=working_path, format="turtle")
        app.config["ONTOLOGY_FILE"] = save_new_version(g)
        #g.parse(app.config["ONTOLOGY_FILE"])
            
        if app.config["ONTOLOGY_FILE"].endswith('.rdf'):
            g.parse(app.config["ONTOLOGY_FILE"], format="xml")  # Assuming the input file is in RDF/XML format
            # Serialize the graph to RDF/XML
            output_path = os.path.expanduser("~/agas/output.rdf")
            # Make sure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            g.serialize(destination=output_path, format="xml")

        elif app.config["ONTOLOGY_FILE"].endswith('.ttl'):
            g.parse(app.config["ONTOLOGY_FILE"], format="turtle")
            # Serialize the graph to Turtle format
            output_path = os.path.expanduser("~/agas/output_file.ttl")
            # Make sure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            g.serialize(destination=output_path, format="ttl")

        elif app.config["ONTOLOGY_FILE"].endswith('.owl'):
            g.parse(app.config["ONTOLOGY_FILE"], format="xml")
            # Serialize to OWL/XML
            output_path = os.path.expanduser("~/agas/output_file.owl")
            output_path.mkdir(exist_ok=True)
            g.serialize(destination=output_path, format="xml")
            
        flash(f"Updated individual {name}.", "success")
        return redirect(url_for("home"))

    ################################ Delete Ind in onto ##########################################
    @app.route("/delete_individual", methods=["POST"])
    def delete_individual():
        name = request.form.get("name")
        uri = NS[name.split('_IND')[0] if '_IND' in name else name]

        # Step 1: Define safe working copy
        #original_path = app.config["ONTOLOGY_FILE"]
        #working_path = "~/Desktop/AGAS_FILES/DelInd_ontology.ttl"

        # Step 2: Copy original ontology to working file if it doesn't exist yet
        #if not os.path.exists(working_path):
        #    shutil.copyfile(original_path, working_path)

        #Making it so variable updates
        #app.config["ONTOLOGY_FILE"] = working_path

        # Remove all triples where individual is subject or object
        for triple in g.triples((uri, None, None)):
            g.remove(triple)
        for triple in g.triples((None, None, uri)):
            g.remove(triple)

        #working_path = "~/Desktop/AGAS_FILES/testDel.ttl"
        #g.serialize(destination=working_path, format="turtle")
        app.config["ONTOLOGY_FILE"] = save_new_version(g)
        #g.parse(app.config["ONTOLOGY_FILE"])
            
        if app.config["ONTOLOGY_FILE"].endswith('.rdf'):
            g.parse(app.config["ONTOLOGY_FILE"], format="xml")  # Assuming the input file is in RDF/XML format
            # Serialize the graph to RDF/XML
            output_path = os.path.expanduser("~/agas/output.rdf")
            # Make sure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            g.serialize(destination=output_path, format="xml")

        elif app.config["ONTOLOGY_FILE"].endswith('.ttl'):
            g.parse(app.config["ONTOLOGY_FILE"], format="turtle")
            # Serialize the graph to Turtle format
            output_path = os.path.expanduser("~/agas/output_file.ttl")
            # Make sure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            g.serialize(destination=output_path, format="ttl")

        elif app.config["ONTOLOGY_FILE"].endswith('.owl'):
            g.parse(app.config["ONTOLOGY_FILE"], format="xml")
            # Serialize to OWL/XML
            output_path = os.path.expanduser("~/agas/output_file.owl")
            # Make sure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            g.serialize(destination=output_path, format="xml")
            
        return redirect(url_for('home'))

    ################################ For history/versions of onto ##########################################
    @app.route("/versions")
    def versions():
        files = sorted(os.listdir(app.config["VERSIONS_DIR"]))
        files = [f for f in files]
        return render_template("jinjaT/versions.html", files=files, ofp=app.config["ONTOLOGY_FILE"], language = app.config["LANGUAGE"])

    #DONE: DOES NOT SWITCH -> NEEDED GLOBAL
    #CHANGED TO ONTOFILE: versions/ontology_20250911_044921.ttl
    # 127.0.0.1 - - [11/Sep/2025 05:10:12] "POST /switch_version/ontology_20250911_044921.ttl HTTP/1.1" 302 -
    #VIEWING -> ontology_20250911_044921.ttl
    #ONTOFILE -> versions/ontology_20250911_050901.ttl

    @app.route("/switch_version/<filename>", methods=["POST"])
    def switch_version(filename):
        version_path = os.path.join(app.config["VERSIONS_DIR"], filename)

        if not os.path.exists(version_path):
            flash("Version not found!", "error")
            return redirect(url_for("versions"))

        # update the active ontology file
        app.config["ONTOLOGY_FILE"] = version_path
        
        #reset graph
        g.remove((None, None, None))  # clears all triples
        
        g.parse(app.config["ONTOLOGY_FILE"])
        
        print(f"CHANGED TO ONTOFILE: {app.config["ONTOLOGY_FILE"]}")
        flash(f"Switched to version: {filename}", "success")
        #return redirect(url_for("view_version", filename=filename))
        return redirect(url_for("versions"))

    @app.route("/versions/<filename>")
    def view_version(filename):
        version_path = os.path.join(app.config["VERSIONS_DIR"], filename)
        g_temp = Graph()
        g_temp.parse(version_path)
        
        taxonomy = build_class_taxonomy(g_temp) 
        
        t_indivs = []

        for cls in taxonomy:
            class_uri = NS[cls]
            individuals = sorted(g_temp.subjects(RDF.type, class_uri))

            for ind in individuals:
                #print(ind)
                if ind not in t_indivs:
                    t_indivs.append(ind)

        t_indivs = pretty_print_uri(t_indivs)
        
        stats = {
            "classes": len(list(g_temp.subjects(RDF.type, OWL.Class))),
            "individuals": len(t_indivs),
            "data_properties": len(list(g_temp.subjects(RDF.type, OWL.DatatypeProperty))),
            "object_properties": len(list(g_temp.subjects(RDF.type, OWL.ObjectProperty))),
            "annotation_properties": len(list(g_temp.subjects(RDF.type, OWL.AnnotationProperty))),
            "namespaces": list(dict(g_temp.namespaces()).keys())
        }
        
        print(f"VIEWING -> {filename}")
        print(f"ONTOFILE -> {app.config["ONTOLOGY_FILE"]}")
        
        # load and display however you already render ontologies
        return render_template("jinjaT/version.html", ofp=app.config["ONTOLOGY_FILE"] ,ontology_file=filename, stats=stats, language = app.config["LANGUAGE"])

    @app.route("/clear_versions", methods=["POST"])
    def clear_versions():
        versions_dir = os.path.join(os.getcwd(), "versions")

        if not os.path.exists(versions_dir):
            flash("No versions folder found.", "warning")
            return redirect(url_for("versions"))

        files = sorted(
            [f for f in os.listdir(versions_dir) if f.endswith(".ttl") or f.endswith(".owl") or f.endswith(".rdf") ],
            key=lambda f: os.path.getctime(os.path.join(versions_dir, f))
        )

        if len(files) <= 2:
            flash("Nothing to clean, only two or fewer versions exist.", "info")
            return redirect(url_for("versions"))

        # Keep first and last
        keep = {files[0], files[-1]}
        deleted = []

        for f in files:
            if f not in keep:
                os.remove(os.path.join(versions_dir, f))
                deleted.append(f)

        flash(f"Deleted {len(deleted)} old versions: {', '.join(deleted)}", "success")
        return redirect(url_for("versions"))

    @app.route("/delete_version/<path:filename>", methods=["POST"])
    def delete_version(filename):
        versions_dir = os.path.join(os.getcwd(), "versions")
        filepath = os.path.join(versions_dir, filename)

        # Safety check: only allow deleting files inside versions_dir
        if not os.path.abspath(filepath).startswith(os.path.abspath(versions_dir)):
            flash("Invalid file path!")
            return redirect(url_for("versions"))

        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                flash(f"Deleted version: {filename}")
            except Exception as e:
                flash(f"Error deleting {filename}: {str(e)}")
        else:
            flash(f"Version not found: {filename}")

        return redirect(url_for("versions"))
    
    ################################ For downloading a zip of the ontology and everything needed ##########################################
    def safe_walk_and_add(zf, folder, arc_base):
        project_root = os.path.abspath(app.root_path)
        
        # Resolve folder to an absolute path inside your project root
        folder_abs = folder if os.path.isabs(folder) else os.path.join(project_root, folder)
        folder_abs = os.path.normpath(folder_abs)

        # Skip missing paths
        if not os.path.exists(folder_abs):
            app.logger.info("Skipping missing folder: %s", folder_abs)
            return

        # Ensure the folder is within the project root (prevents walking / or other mounts)
        try:
            if os.path.commonpath([project_root, folder_abs]) != project_root:
                app.logger.warning("Skipping folder outside project root: %s", folder_abs)
                return
        except ValueError:
            # On weird platforms / different drives - skip to be safe
            app.logger.warning("Skipping folder (commonpath error): %s", folder_abs)
            return

        # Walk and add only regular, readable files
        for root, _, files in os.walk(folder_abs):
            for file in files:
                full_path = os.path.join(root, file)

                # Skip non-regular files (devices, sockets, etc.)
                if not os.path.isfile(full_path):
                    continue

                # Skip files we can't read
                if not os.access(full_path, os.R_OK):
                    app.logger.info("Skipping unreadable file: %s", full_path)
                    continue

                # Build archive name relative to the folder base
                rel_path = os.path.relpath(full_path, start=folder_abs)
                arcname = os.path.join(arc_base, rel_path)

                try:
                    zf.write(full_path, arcname=arcname)
                except PermissionError:
                    app.logger.warning("Permission denied adding file %s - skipped", full_path)
                except Exception as e:
                    app.logger.exception("Failed adding file %s: %s", full_path, e)
                    
    @app.route('/download_package')
    def download_package():
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
            with zipfile.ZipFile(tmp.name, 'w') as zf:
                
                # --- Ontology versions ---
                filesV = sorted(os.listdir(app.config["VERSIONS_DIR"]))
                for f in filesV:
                    full_path = os.path.join(app.config["VERSIONS_DIR"], f)
                    # Put all ontology versions under versions/
                    zf.write(full_path, arcname=os.path.join("versions", f))
    
                # --- Default templates ---
                for folder in DEFAULT_TEMPLATES:
                    safe_walk_and_add(zf, folder, "templates")

                # --- Extra templates ---
                if EXTRA_TEMPLATES != "NONE":
                    for folder in EXTRA_TEMPLATES:
                        safe_walk_and_add(zf, folder, "extra_templates")

                # --- Static folder ---
                for root, _, files in os.walk(app.static_folder):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, start=app.static_folder)
                        # Keeps static/ folder structure
                        zf.write(full_path, arcname=os.path.join("static", rel_path))

                # --- README (optional) ---
                if os.path.exists("README.md"):
                    zf.write("README.md", arcname="README.md")

            return send_file(tmp.name, as_attachment=True, download_name="ontology_package.zip")

    ################################ For giving the manual.md from static ##########################################  
    @app.route("/manual")
    def manual():
        with open(f"{app.static_folder}/AGAS_manual.md", "r", encoding="utf-8") as f:
            content = f.read()
        html = markdown.markdown(content, extensions=["fenced_code", "tables", "toc"])
        return render_template_string("""
        <html>
        <head>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/github-markdown-css/github-markdown.min.css">
            <!-- Styles -->
            <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
        </head>
        <body>
            <article class="markdown-body">{{ content|safe }}</article>
        </body>
        </html>
        """, content=html)
    
    return app

