# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 08:58:56 2014

Script to generate intro-example.odml

@author: zehl
"""

import odml
import datetime

# Define the odml document with its attributes
document = odml.Document(author = "Arthur Dent",
                         date = "2014-03-20",#datetime.date(2014, 3, 20),
                         version = 4.7)
#                         repository = "http://portal.g-node.org/odml/terminologies/v1.0/terminologies.xml")

# Define the top sections with their attributes
top_section_1 = odml.Section(name = "Setup",
                             definition = "Description of the used experimental setup.",
                             type = "setup")

# Connect top_sections to document
document.append(top_section_1)

# Define values and their attributes for properties of top_section_1
value_1 = odml.Value(data = "Arthur Dent",
                     dtype = "person",
                     definition = "First and last name of a person.")
value_2 = odml.Value(data = "Zaphod Beeblebrox",
                     dtype = "person",
                     definition = "First and last name of a person.")
value_3 = odml.Value(data = "Trillian Astra",
                     dtype = "person",
                     definition = "First and last name of a person.")
value_4 = odml.Value(data = "Ford Prefect",
                     dtype = "person",
                     definition = "First and last name of a person.")

# Define properties and their attributes and values of top_section_1
property_1 = odml.Property(name = "Creator",
                           definition = "The person/s who built the setup.",
                           value = value_1)
property_2 = odml.Property(name = "User",
                           definition = "The person/s who use the setup.",
                           value = [value_2, value_3, value_4])

# Connect properties (including their values) to top_section_1
top_section_1.append(property_1)
top_section_1.append(property_2)

save_to = "/home/zehl/projects/toolbox/python-odml/doc/example_odMLs/intro-example.odml"
odml.tools.xmlparser.XMLWriter(document).write_file(save_to)