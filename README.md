# 📦 AGAS Installation & User Guide

# 1. Installation

## 1.1 Requirements

Before starting, make sure you have the following installed:

- **Python 3.11+** (3.13 recommended):  
  ``` 
  python --version
  ```

- **Git**:
  ```
  git --version 
  ```
  
- **Pip**:
```
sudo apt-get install python-pip
```

- **Graphviz**:
```
sudo apt install python3-pydot graphviz
```

Do you not have them?

Just run:
```
sudo apt install python3.13-full

sudo add-apt-repository ppa:git-core/ppa
sudo apt-get update
sudo apt-get install git
```

## 1.2 Steps

1. **Grab** the code:
```
git clone https://github.com/dianamalheiro02/agas.git
cd agas
```

Or install directly from github:
```
pip install git+https://github.com/dianamalheiro02/agas.git
```

2. **Install** it:
```   
pip install .
```

3. **Test** it:
```
agas
```

If you see the help menu, congratulations! You are ready to get started.
Got stuck? Jump to the **Troubleshooting**.


## First Moves
1. **Create** your config skeleton:
```
agas -s > G0_config.txt
```

2. Next, **edit the ONTOLOGY_FILE directory** inside the G0.txt file, at least:
```
vim G0.txt

- Or your favorite text editor. -
```

3. The new directory can be obtained with the commands:
``` 
cd tests/ontos/typeC/C1/ontos_final
realpath greek_deities_ontology_complete.ttl
```

4. After editing, it should look something like this:
```
ONTOLOGY_FILE = ’/home/diana/agas/ontos/typeC/C1/ontos_final/greek_deities_
ontology_complete.tt’
```

5. If you wish to edit more fields, refer to Appendix B.

6. **Validate** it:
```
agas -c G0_config.txt
```

7. **Run** it:
```
agas -r G0_config.txt
```

8. **Open** your browser to: http://localhost:5000
   
Well done! You now have your very own ontology-powered website up and running



# 🚀 2. Overview of Features

AGAS provides a web-based interface to explore and prototype websites from ontologies, one that, with this said, has the following features:

* **Prototype Generation** → Configure and preview website structures.
 
* **Browse Ontologies** → Navigate ontology classes, individuals, and properties.
  
* **Favorites** → Bookmark ontology elements for quick access.

* **Edit (Admin only)** → Modify ontology contents (Add, Edit, Delete).

* **Run SPARQL Queries** → Search and retrieve structured information.

* **Visualization** → Generate RDF graphs and statistics about the ontology.

---

# 🔑 3. Login and Permissions

AGAS uses a lightweight login system to separate viewers and editors:

* **Viewer (default)** → Anyone can access the platform in read-only mode.

* **Editor (admin login)** → Full edit rights are granted after logging in.

## Admin Credentials (default)

**Username: AGAS_Admin**

**Password: AGAS_Admin_Password**

If **login fails**, double-check that the credentials match the defaults or your updated values, if you've edited the code.


---

# 🖥️ 4. Using AGAS
## 4.1 Home Page (Expert)
Where you can: 
* **View and edit** the different components of the ontology. **Do not be alarmed if it takes a while to load or if it needs some refreshing!**
* **Convert** the ontology between RDF, OWL and TTl;
* Get the **graph** view of it;
* Go to **Protégé** to further editing procedures;
* Start using **SPARQL**.

## 4.2 Ontology Explorer (Non-Expert)
* **Browse and add** ontology classes, data properties, object properties, and individuals;
* Star items to save them in **Favorites**;
* **Search** tab in the corner is always present and functional, allowing to look up all components related to the ontology.

## 4.3 SPARQL Queries
* **Edit and execute** SPARQL queries;
* **Results** are displayed in a separate results page.

## 4.5 Versions
Where you can:

* **Navigate** different versions of the ontology, automatically saved along the way;
* **Switch between and delete** these different versions.
 
## 4.6 About & Contacts
* One has **information about the ontology and the other about its author**;
* Offers a **ZIP** containing all application data and other information on the ontology.

# 🧩 5. Notes and Tips

1. No login needed if you only want to browse and visualize.
   
2. Login if you want to Edit/Add/Delete ontology contents.
3. Use the Favorites system to collect items for fast navigation.
4. Try changing the type of the ontology in the DSL to see different types of page renderings and templates.
5. All changes made in Edit mode are immediately reflected in the ontology file.
6. If you tried to edit the different sections of the ontology in the projection editor but it didn't work, try with the full ontology view.
7. Never delete the version of the ontology you're working with.
8. Reload the page if the projection editors load with a different light setting than the one you set previously.
9. If SPARQL queries return nothing, confirm that the ontology file is properly indicated and loaded.
  
# 🛠️ 6. Troubleshooting

## Problem 1: ’pip install .’ fails
Possible causes and solutions are:

### ’pyproject.toml’ not found:

Make sure you are inside the correct folder when running the command:
```
pip install .
```

### 'build' backend not installed:
Install it manually:
```
python3 -m pip install flit
```

### Permission denied (especially on Linux/macOS):
```
pip install --user .
```

Or try using a virtual environment to run this on.

### Old pip version:
```
pip install --upgrade pip
```

### error: externally-managed-environment:
Try and install ’pipx’ and see how your computer behaves:
```
sudo apt install pipx
pipx install .
pipx ensurepath
- And then reopen the terminal -
```

## Problem 2: Running ’agas -r tests/config.txt’ doesn’t work
Possible causes and solutions are:

### ModuleNotFoundError: No module named ’agas’
Check that installation was a success with:
```
pip show agas
```
And if not installed, re-run:
```
pip install .
```

### Wrong working directory: 
Ensure you are running the command from the project root, at the same level as the ’pyproject.toml’.

### Flask not installed:
```
pip install flask
```

# 7. DSL Structure
## 1. Ontology Configuration

This section defines the ontology file path, its type (A, B, C1, or C2), and the Protégé executable location for ontology editing.
```
ONTOLOGY_FILE: Points to the ontology file used for the website generation.

PROTEGE_PATH: Allows AGAS to launch Protégé for ontology modifications.

ONTOLOGY_TYPE: Determines how AGAS interprets the ontology (e.g., structured vs complex knowledge representation).

ONTOLOGY_IMAGES: To specify if the ontology has images that are from your own
desktop (’NONE’ if it doesn’t), if it does, please give the path to the folder you have them in.

ONTOLOGY_EDIT: Specify who can edit the ontology exactly (e.g, every single person can edit it and its information with the keyword ’ALL’ or only people who ’LOGIN’).
```

## 2. User Experience Customization
The DSL allows the system to tailor the website generation experience based on the user type parameter, called USER_TYPE and that can have two different specifications:
```
’EXP’ (Experienced user): Provides advanced customization options.
’NONEXP’ (Non-experienced user): Offers a simpler, more guided experience.
```

## 3. Template and Language Selection
Users can specify which Jinja templates should be used for rendering the website and what language they want to use.
```
TEMPLATES: Specifies which Jinja templates define the page layouts. 

LANGUAGE: Define what language you want to use, ’PT’ or ’EN’.
```

## 4. Visualization Preferences
Users can define what elements should be displayed on generated pages.

```
RDF_VIEW: What you want to see in the Graph, which classes you want present. You can write down ’ALL’ if you want them all, but if not, please list the classes you want.

VIEW_CLASSES: Specifies which ontology classes are important to be visualized.

SPECIFIC_PAGES: Where users can list which pages are more important to generate, pages of specific individuals or entities.

MAKE_PRETTY: Specifies which properties the user would like to ’prettify’ and highlight, giving them their own designated card later on in the Individuals.html.

SEE_PROPERTIES: Allows for users to point out which properties they’d like to see a list of individuals that share the same information presented (e.g., instead of only seeing who your father is with the property ’hasFather’, you can see the list of other identities that share the same father as you).

GIVE_PRIORITY: To specify the order of the cards/highlights of the Individual.html page, the user can always just appoint ’NONE’ if they don’t want any priority assigned and just wants to see things in alphabetic order.

NOT_SHOW: Allows users to pinpoint what classes, individuals or even properties they do not want present in the rendered pages. 
```

A star-based mechanism was introduced as well, to allow users to mark ontology classes and individuals as favorites. This system is activated through the STARS keyword in the DSL configuration, specifically within these parameters. 

Besides this keyword, the VIEW_CLASSES also has a TREE keyword where, if specified, the user sees the taxonomy as a JQuery Tree widget.

## 5. Base SPARQL Queries
A predefined list of SPARQL queries is included in the DSL to extract essential ontology information.
```
BASE_QUERIES = [ """ SELECT ?class WHERE ?class a owl:Class . """,
""" SELECT ?property WHERE ?property a owl:ObjectProperty . """,
""" SELECT ?property WHERE ?property a owl:DatatypeProperty . """,
""" SELECT ?individual WHERE ?individual rdf:type owl:NamedIndividual . """ ]
```

These queries allow AGAS to fetch ontology classes, object properties, datatype properties, and named individuals, forming the basis for dynamic page generation.

## 6. Metadata Focused Variables
Where users can appoint and fill in necessary metadata for visualization and rendering of the information on the ontology.
```
AGAS_NAME: Which corresponds to the name they want to give the ’home’ page and to
the ontology itself.

L_DISPOSITION: Defines the layout orientation (e.g., vertical or horizontal) for list-based content.

MODULES: Enables users to specify which properties should be expanded and rendered
directly, rather than shown as simple links. This allows greater control over the display of ontology information.

ABOUT: Allows users to instruct the file with the information they need and want to showcase in the ’about.html’ page.

ONTOLOGY_SOURCE: For users to indicate where the ontology came from. And if user-made, can just fill in with the url from the AGAS platform or the prefix of the ontology.
```

Example:
```
MODULES = ’Description’: ’DescriptionText + DescriptionInGame’, ’EvolvesFrom’:
’EvolvesTo’, ’PokemonAcquisition’: ’AcquiredBy + PokeAcquiredInGame’
```

This metadata layer empowers AGAS to tailor page content to user-defined visualization needs.

## 7. User Information
Where users can give and fill in their own information, pertinent for support pages, such as the ’about.html’ one.
```
USERNAME: So users can personalize their username, that later is displayed in the ’about.html’ page as well, as pertinent information for the ontology.

USER_EMAIL: Where users can write down their email, as to enrich their generated site and ontology information.

USER_GITHUB: Allows users to give their github information to, once again, enrich the website.

USER_SOCIALS: Which is where the users can indicate the links to their social media, professional accounts. Showcasing information and means for contact that can be pertinent when generating such a website.
```

## 8. Page Orientation Option
Users can choose the manner in which to display the NONEXP Home page by filling in the field **AGAS_PAGES** with either:
```
’BLOG’: Enables a wiki/blog-like view.
’PAGES’: Keeps to the default way of showcasing the information, following the normal pattern of page generation.
```

As a bonus, and because background pictures are something that blogs and wikis use a lot, we also allow them to tag along a .png or .jpg image in the field **AGAS_BACKGROUNG**, to make the experience more magical and immersive, but all the while optional, of course.
```
’NONE’: If you do not wish to add a background.
’image/path’: Which should be to a file in the static/images folder, so it can be used in the template more efficiently, since trying to move the image there automatically via the app.py was not working properly.
```
