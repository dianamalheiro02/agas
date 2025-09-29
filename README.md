# 📦 1. Installation
## Requirements

Python 3.10+

pip

## Steps

### Clone the repository:

git clone https://github.com/yourusername/AGAS.git
cd AGAS


## Run AGAS:



# 🚀 2. Overview of Features

* AGAS provides a web-based interface to explore and prototype websites from ontologies.

* Prototype Generation → Configure and preview website structures.
 
* Browse Ontologies → Navigate ontology classes, individuals, and properties.
  
* Favorites → Bookmark ontology elements for quick access.

* Edit (Admin only) → Modify ontology contents (Add, Edit, Delete).

* Run SPARQL Queries → Search and retrieve structured information.

* Visualize → Generate RDF graphs and statistics about the ontology.

---

# 🔑 3. Login and Permissions

AGAS uses a lightweight login system to separate viewers and editors:

* Viewer (default) → Anyone can access the platform in read-only mode.

* Editor (admin login) → Full edit rights are granted after logging in.

## Admin Credentials (default)

**Username: AGAS_Admin**

**Password: AGAS_Admin_Password**

---

# 🖥️ 4. Using AGAS
## 4.1 Prototype Generation

* Fill out a DSL configuration file.

* Define templates, ontology type, visualization settings.

* Preview generated website structures.
  
## 4.1 Home Page (Expert)

* Shows navigation options: Ontology Explorer, SPARQL Queries, Favorites, Prototype Generation.

* Displays current role (Viewer or Editor).

## 4.2 Ontology Explorer (Non-Expert)

* Browse ontology classes, data properties, object properties, and individuals.

* Star items to save them in Favorites.

## 4.3 SPARQL Queries

* Enter and execute SPARQL queries.

* Results are displayed in a separate results page.


## 4.5 Editing Mode (Admin Only)

* Add new ontology classes or individuals.

* Edit existing entries.

* Delete items when necessary.

* Editing is only available if logged in as Editor.

# ⚙️ 5. Configuration

AGAS uses a DSL configuration file to control:

1. Ontology type

2. Templates

3. Viewable classes

4. Base SPARQL queries

5. Visualization options

Load this file via the interface or command-line arguments.

# 🧩 6. Shortcuts and Tips

No login needed if you only want to browse and visualize.

Login if you want to Edit/Add/Delete ontology contents.

Use the Favorites system to collect items for fast navigation.

All changes made in Edit mode are immediately reflected in the ontology file.

# 🛠️ 7. Troubleshooting

If the **server does not start**, ensure you are running the correct Python version.

If **login fails**, double-check that the credentials match the defaults or your updated values.

If **SPARQL queries return nothing**, confirm that the ontology file is properly indicated and loaded.

# 📚 8. Future Improvements

* Multi-user role support.

* External authentication (OAuth2, institutional login).

* Collaborative editing.

* More visualization options (timelines, interactive graphs).