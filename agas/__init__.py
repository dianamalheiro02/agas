#!/usr/bin/env python3  

'''
NAME
   agas - Web platform for automatic site generation

SYNOPSIS
   agas [options] [input_file]
   options:
        -s: Show a skeleton for the DSL configuration file
        -c: Validates a DSL config file
        -r: Run the AGAS Flask app with given input file

DESCRIPTION
   AGAS is a research platform for automatic web prototype generation.
   It follows the following magic formula: DSL + Ontology = Website.
   This script launches the AGAS application/platform and in doing so, allows the user to navigate the generated website, allowing BREAD (Browse, Read, Edit, Add, Delete).
   It's important to mention that it needs a configuration file to run.
   If this file is not given, you will be asked to provide it (ERROR), and only then will it work properly.
'''



__version__="0.0.1"