# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 08:58:56 2014

Script to generate intro-example.odml

@author: zehl
"""

import odml
import datetime


# CREATE A DOCUMENT
doc = odml.Document(author="Douglas Adams",
                    date=datetime.date(1979, 10, 12),
                    version=42)

# CREATE AND APPEND THE MAIN SECTIONs
doc.append(odml.Section(name="TheCrew",
                        definition="Information on the crew",
                        type="crew"))

doc.append(odml.Section(name="TheStarship",
                        definition="Information on the crew",
                        type="crew"))


# SET NEW PARENT NODE
parent = doc['TheCrew']

# APPEND SUBSECTIONS
parent.append(odml.Section(name="Arthur Philip Dent",
                           type="crew/person",
                           definition="Information on Arthur Dent"))

parent.append(odml.Section(name="Zaphod Beeblebrox",
                           type="crew/person",
                           definition="Information on Zaphod Beeblebrox"))

parent.append(odml.Section(name="Tricia Marie McMillan",
                           type="crew/person",
                           definition="Information on Trillian Astra"))

parent.append(odml.Section(name="Ford Prefect",
                           type="crew/person",
                           definition="Information on Ford Prefect"))


# APPEND PROPERTIES WITH VALUES
parent.append(odml.Property(name="NameCrewMembers",
                            value=[odml.Value(data="Arthur Philip Dent",
                                              dtype=odml.DType.person),
                                   odml.Value(data="Zaphod Beeblebrox",
                                              dtype=odml.DType.person),
                                   odml.Value(data="Tricia Marie McMillan",
                                              dtype=odml.DType.person),
                                   odml.Value(data="Ford Prefect",
                                              dtype=odml.DType.person)],
                            definition="List of crew members names"))

parent.append(odml.Property(name="NoCrewMembers",
                            value=odml.Value(data=4,
                                             dtype=odml.DType.int),
                            definition="Number of crew members"))


# SET NEW PARENT NODE
parent = doc['TheCrew']['Arthur Philip Dent']

# APPEND SUBSECTIONS

# APPEND PROPERTIES WITH VALUES
parent.append(odml.Property(name="Species",
                            value=odml.Value(data="Human",
                                             dtype=odml.DType.string),
                            definition="Species to which subject belongs to"))

parent.append(odml.Property(name="Nickname",
                            value=odml.Value(data="The sandwich-maker",
                                             dtype=odml.DType.string),
                            definition="Nickname(s) of the subject"))

parent.append(odml.Property(name="Occupation",
                            value=odml.Value(data="-",
                                             dtype=odml.DType.string),
                            definition="Occupation of the subject"))

parent.append(odml.Property(name="Gender",
                            value=odml.Value(data="male",
                                             dtype=odml.DType.string),
                            definition="Sex of the subject"))

parent.append(odml.Property(name="HomePlanet",
                            value=odml.Value(data="Earth",
                                             dtype=odml.DType.string),
                            definition="Home planet of the subject"))


# SET NEW PARENT NODE
parent = doc['TheCrew']['Zaphod Beeblebrox']

# APPEND SUBSECTIONS

# APPEND PROPERTIES WITH VALUES
parent.append(odml.Property(name="Species",
                            value=odml.Value(data="Betelgeusian",
                                             dtype=odml.DType.string),
                            definition="Species to which subject belongs to"))

parent.append(odml.Property(name="Nickname",
                            value=odml.Value(data="-",
                                             dtype=odml.DType.string),
                            definition="Nickname(s) of the subject"))

parent.append(odml.Property(name="Occupation",
                            value=odml.Value(data="Ex-Galactic President",
                                             dtype=odml.DType.string),
                            definition="Occupation of the subject"))

parent.append(odml.Property(name="Gender",
                            value=odml.Value(data="male",
                                             dtype=odml.DType.string),
                            definition="Sex of the subject"))

parent.append(odml.Property(name="HomePlanet",
                            value=odml.Value(data="A planet in the vicinity "
                                                  "of Betelgeuse",
                                             dtype=odml.DType.string),
                            definition="Home planet of the subject"))


# SET NEW PARENT NODE
parent = doc['TheCrew']['Tricia Marie McMillan']

# APPEND SUBSECTIONS

# APPEND PROPERTIES WITH VALUES
parent.append(odml.Property(name="Species",
                            value=odml.Value(data="Betelgeusian",
                                             dtype=odml.DType.string),
                            definition="Species to which subject belongs to"))

parent.append(odml.Property(name="Nickname",
                            value=odml.Value(data="Trillian Astra",
                                             dtype=odml.DType.string),
                            definition="Nickname(s) of the subject"))

parent.append(odml.Property(name="Occupation",
                            value=odml.Value(data="-",
                                             dtype=odml.DType.string),
                            definition="Occupation of the subject"))

parent.append(odml.Property(name="Gender",
                            value=odml.Value(data="female",
                                             dtype=odml.DType.string),
                            definition="Sex of the subject"))

parent.append(odml.Property(name="HomePlanet",
                            value=odml.Value(data="Earth",
                                             dtype=odml.DType.string),
                            definition="Home planet of the subject"))


# SET NEW PARENT NODE
parent = doc['TheCrew']['Ford Prefect']

# APPEND SUBSECTIONS

# APPEND PROPERTIES WITH VALUES
parent.append(odml.Property(name="Species",
                            value=odml.Value(data="Betelgeusian",
                                             dtype=odml.DType.string),
                            definition="Species to which subject belongs to"))

parent.append(odml.Property(name="Nickname",
                            value=odml.Value(data="Ix",
                                             dtype=odml.DType.string),
                            definition="Nickname(s) of the subject"))

parent.append(odml.Property(name="Occupation",
                            value=odml.Value(data="Researcher for the "
                                                  "Hitchhiker's Guide to the "
                                                  "Galaxy",
                                             dtype=odml.DType.string),
                            definition="Occupation of the subject"))

parent.append(odml.Property(name="Gender",
                            value=odml.Value(data="male",
                                             dtype=odml.DType.string),
                            definition="Sex of the subject"))

parent.append(odml.Property(name="HomePlanet",
                            value=odml.Value(data="A planet in the vicinity "
                                                  "of Betelgeuse",
                                             dtype=odml.DType.string),
                            definition="Home planet of the subject"))

# SET NEW PARENT NODE
parent = doc['TheStarship']

# APPEND SUBSECTIONS
parent.append(odml.Section(name='Cybernetics',
                           type="starship/cybernetics",
                           definition="Information on cybernetics present on "
                                      "the ship"))

# APPEND PROPERTIES WITH VALUES
parent.append(odml.Property(name="Name",
                            value=odml.Value(data="Heart of Gold",
                                             dtype=odml.DType.string),
                            definition="Name of person/device"))

parent.append(odml.Property(name="OwnerStatus",
                            value=odml.Value(data="stolen",
                                             dtype=odml.DType.string),
                            definition="Owner status of device"))

parent.append(odml.Property(name="DriveType",
                            value=odml.Value(data="Infinite Propability Drive",
                                             dtype=odml.DType.string),
                            definition="Type of drive"))

parent.append(odml.Property(name="Technology",
                            value=odml.Value(data="secret",
                                             dtype=odml.DType.string),
                            definition="Technology used to built device"))

parent.append(odml.Property(name="Length",
                            value=odml.Value(data=150.00,
                                             dtype=odml.DType.float,
                                             unit='m'),
                            definition="Length of device"))

parent.append(odml.Property(name="Shape",
                            value=odml.Value(data="various",
                                             dtype=odml.DType.string),
                            definition="Shape of device"))

parent.append(odml.Property(name="FactoryPlanet",
                            value=odml.Value(data="Damogran",
                                             dtype=odml.DType.string),
                            definition="Planet where device was constructed"))

# SET NEW PARENT NODE
parent = doc['TheStarship']['Cybernetics']

# APPEND SUBSECTIONS
parent.append(odml.Section(name='Marvin',
                           type="starship/cybernetics",
                           definition="Information on Marvin"))

parent.append(odml.Section(name='Eddie',
                           type="starship/cybernetics",
                           definition="Information on Eddie"))

# APPEND PROPERTIES WITH VALUES
parent.append(odml.Property(name="RobotType",
                            value=odml.Value(data="Genuine People "
                                                  "Personalities",
                                             dtype=odml.DType.string),
                            definition="Type of robots"))

parent.append(odml.Property(name="Manufacturer",
                            value=odml.Value(data="Sirius Cybernetics "
                                                  "Corporation",
                                             dtype=odml.DType.string),
                            definition="Manufacturer of robots"))

parent.append(odml.Property(name="NoOfCybernetics",
                            value=odml.Value(data=2,
                                             dtype=odml.DType.int),
                            definition="Number of cybernetic robots on the "
                                       "ship"))

homedir = "/home/zehl/Projects/toolbox/"
save_to = homedir + "/python-odml/doc/example_odMLs/THGTTG.odml"
odml.tools.xmlparser.XMLWriter(doc).write_file(save_to)
