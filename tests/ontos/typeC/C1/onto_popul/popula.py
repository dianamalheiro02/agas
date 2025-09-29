# Re-import necessary modules after code execution state reset
import json
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, OWL

# Load the updated JSON file
with open("/mnt/data/deities.json", "r", encoding="utf-8") as f:
    updated_deities = json.load(f)

# Namespaces
NS = Namespace("http://www.semanticweb.org/diana-teixeira/ontologies/2025/GreekDeities/")
g = Graph()
g.bind("", NS)
g.bind("owl", OWL)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)

# Function to add deity individuals safely
def add_deity_safe(name, data):
    deity_uri = NS[name.replace(" ", "_")]
    g.add((deity_uri, RDF.type, NS.Deity))

    # Classification
    if "classification" in data:
        class_uri = NS[data["classification"]]
        g.add((deity_uri, RDF.type, class_uri))

    # Data properties
    if "hasDescription" in data:
        g.add((deity_uri, NS.hasDescription, Literal(data["hasDescription"], datatype=XSD.string)))
    if "hasImage" in data:
        g.add((deity_uri, NS.hasImage, Literal(data["hasImage"], datatype=XSD.anyURI)))
    if "hasPower" in data:
        powers = data["hasPower"]
        if isinstance(powers, str):
            powers = [p.strip() for p in powers.split(",")]
        for power in powers:
            g.add((deity_uri, NS.hasPower, Literal(power, datatype=XSD.string)))

    # Object properties (single)
    if "hasFather" in data:
        g.add((deity_uri, NS.hasFather, NS[data["hasFather"].replace(" ", "_")]))
    if "hasMother" in data:
        g.add((deity_uri, NS.hasMother, NS[data["hasMother"].replace(" ", "_")]))

    # Object properties (multiple)
    for prop in ["hasChild", "hasLover"]:
        if prop in data:
            for value in data[prop]:
                g.add((deity_uri, NS[prop], NS[value.replace(" ", "_")]))

    # Stories
    if "hasStory" in data:
        for idx, story in enumerate(data["hasStory"], 1):
            story_uri = NS[f"{name.replace(' ', '_')}_Story{idx}"]
            g.add((story_uri, RDF.type, NS.Story))
            if "hasTitle" in story:
                g.add((story_uri, NS.hasTitle, Literal(story["hasTitle"], datatype=XSD.string)))
            if "hasAbstract" in story:
                g.add((story_uri, NS.hasAbstract, Literal(story["hasAbstract"], datatype=XSD.string)))
            g.add((deity_uri, NS.hasStory, story_uri))

# Process each deity
for deity_name, deity_info in updated_deities.items():
    add_deity_safe(deity_name, deity_info)

# Save ontology to Turtle file
output_path = "/mnt/data/greek_deities_ontology_complete.ttl"
g.serialize(destination=output_path, format="turtle")

output_path
