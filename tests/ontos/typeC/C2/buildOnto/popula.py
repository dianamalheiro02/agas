from rdflib import Graph, Namespace, URIRef, RDF, OWL, Literal, XSD
import json
from urllib.parse import quote
import uuid

print("Started")

#Initialize vars
authors = {}
topics = {}
ttl_entries = []

#Get info from ttl
ontology_file = "typec2.ttl"  # This should be the path to your ontology file

with open(ontology_file, 'r') as f:
    for line in f:
        ttl_entries.append(line)

print("Got ontologia")

# JSON data load
with open("bookAll.json", 'r') as f:
    book_data = json.load(f)

with open("bookAll1.json", 'r') as f:
    book1_data = json.load(f)

with open("bookAll2.json", 'r') as f:
    book2_data = json.load(f)

print("Got it all!")

#Get the entries for the new ttl
for title, details in book_data.items():
    author_name, topic_details = details.split(" ; ")
    #topic_name = topic_details.split(".")[0] #caso queira só pequena description do tipo
    
    author_id = authors.setdefault(author_name, f"Author_{uuid.uuid4().hex[:8]}")
    topic_id = topics.setdefault(topic_details, f"Topic_{uuid.uuid4().hex[:8]}")
    text_id = f"Text_{uuid.uuid4().hex[:8]}"
    
    ttl_entries.append(f":{author_id} rdf:type :Author ; \n\t:auth_name \"{author_name}\" .\n\n")
    ttl_entries.append(f":{topic_id} rdf:type :Topic ; \n\t:subject \"{topic_details}\" .\n\n")
    ttl_entries.append(f":{text_id} rdf:type :Text ; \n\t:title \"{title}\" ; :hasAuthor :{author_id} ; :hasTopic :{topic_id} .\n\n")
    
for title, details in book1_data.items():
    author_name, topic_details = details.split(" ; ")
    #topic_name = topic_details.split(".")[0] #caso queira só pequena description do tipo
    
    author_id = authors.setdefault(author_name, f"Author_{uuid.uuid4().hex[:8]}")
    topic_id = topics.setdefault(topic_details, f"Topic_{uuid.uuid4().hex[:8]}")
    text_id = f"Text_{uuid.uuid4().hex[:8]}"
    
    ttl_entries.append(f":{author_id} rdf:type :Author ; \n\t:auth_name \"{author_name}\" .\n\n")
    ttl_entries.append(f":{topic_id} rdf:type :Topic ; \n\t:subject \"{topic_details}\" .\n\n")
    ttl_entries.append(f":{text_id} rdf:type :Text ; \n\t:title \"{title}\" ; :hasAuthor :{author_id} ; :hasTopic :{topic_id} .\n\n")

for title, details in book2_data.items():
    author_name, topic_details = details.split(" ; ")
    #topic_name = topic_details.split(".")[0] #caso queira só pequena description do tipo
    
    author_id = authors.setdefault(author_name, f"Author_{uuid.uuid4().hex[:8]}")
    topic_id = topics.setdefault(topic_details, f"Topic_{uuid.uuid4().hex[:8]}")
    text_id = f"Text_{uuid.uuid4().hex[:8]}"
    
    ttl_entries.append(f":{author_id} rdf:type :Author ; \n\t:auth_name \"{author_name}\" .\n\n")
    ttl_entries.append(f":{topic_id} rdf:type :Topic ; \n\t:subject \"{topic_details}\" .\n\n")
    ttl_entries.append(f":{text_id} rdf:type :Text ; \n\t:title \"{title}\" ; :hasAuthor :{author_id} ; :hasTopic :{topic_id} .\n\n")


with open("ontology_population.ttl", "w") as f:
    f.write("".join(ttl_entries))

print("Turtle file generated: ontology_population.ttl")

