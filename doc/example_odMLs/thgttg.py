# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 08:58:56 2014

Script to generate intro-example.odml

@author: zehl
"""

import datetime
import os
import odml
import sys


if len(sys.argv) != 2:
    print("Please provide an existing directory for the example odml file.")
    quit()

output_directory = sys.argv[-1]
if not os.path.isdir(output_directory):
    print("Please provide an existing directory for the example odml file.")
    quit()

save_to = os.path.join(output_directory, "THGTTG.odml")

odmlrepo = 'http://portal.g-node.org/odml/terminologies/v1.0/terminologies.xml'

# CREATE A DOCUMENT
doc = odml.Document(author="D. N. Adams",
                    date=datetime.date(1979, 10, 12),
                    version=42)
#                    repository=odmlrepo)

# CREATE AND APPEND THE MAIN SECTIONs
doc.append(odml.Section(name="TheCrew",
                        definition="Information on the crew",
                        type="crew"))

doc.append(odml.Section(name="TheStarship",
                        type="starship",
                        definition="Information on the starship"))

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
                            value=["Arthur Philip Dent",
                                   "Zaphod Beeblebrox",
                                   "Tricia Marie McMillan",
                                   "Ford Prefect"],
                            dtype=odml.DType.person,
                            definition="List of crew members names"))

parent.append(odml.Property(name="NoCrewMembers",
                            value=4,
                            dtype=odml.DType.int,
                            definition="Number of crew members",
                            uncertainty=1,
                            reference="The Hitchhiker's guide to the Galaxy (novel)"))


# SET NEW PARENT NODE
parent = doc['TheCrew']['Arthur Philip Dent']

# APPEND SUBSECTIONS

# APPEND PROPERTIES WITH VALUES
parent.append(odml.Property(name="Species",
                            value="Human",
                            dtype=odml.DType.string,
                            definition="Species to which subject belongs to"))

parent.append(odml.Property(name="Nickname",
                            value="The sandwich-maker",
                            dtype=odml.DType.string,
                            definition="Nickname(s) of the subject"))

parent.append(odml.Property(name="Occupation",
                            value=None,
                            dtype=odml.DType.string,
                            definition="Occupation of the subject"))

parent.append(odml.Property(name="Gender",
                            value="male",
                            dtype=odml.DType.string,
                            definition="Sex of the subject"))

parent.append(odml.Property(name="HomePlanet",
                            value="Earth",
                            dtype=odml.DType.string,
                            definition="Home planet of the subject"))


# SET NEW PARENT NODE
parent = doc['TheCrew']['Zaphod Beeblebrox']

# APPEND SUBSECTIONS

# APPEND PROPERTIES WITH VALUES
parent.append(odml.Property(name="Species",
                            value="Betelgeusian",
                            dtype=odml.DType.string,
                            definition="Species to which subject belongs to"))

parent.append(odml.Property(name="Nickname",
                            value=None,
                            dtype=odml.DType.string,
                            definition="Nickname(s) of the subject"))

parent.append(odml.Property(name="Occupation",
                            value="Ex-Galactic President",
                            dtype=odml.DType.string,
                            definition="Occupation of the subject"))

parent.append(odml.Property(name="Gender",
                            value="male",
                            dtype=odml.DType.string,
                            definition="Sex of the subject"))

parent.append(odml.Property(name="HomePlanet",
                            value="A planet in the vicinity of Betelgeuse",
                            dtype=odml.DType.string,
                            definition="Home planet of the subject"))


# SET NEW PARENT NODE
parent = doc['TheCrew']['Tricia Marie McMillan']

# APPEND SUBSECTIONS

# APPEND PROPERTIES WITH VALUES
parent.append(odml.Property(name="Species",
                            value="Human",
                            dtype=odml.DType.string,
                            definition="Species to which subject belongs to"))

parent.append(odml.Property(name="Nickname",
                            value="Trillian Astra",
                            dtype=odml.DType.string,
                            definition="Nickname(s) of the subject"))

parent.append(odml.Property(name="Occupation",
                            value=None,
                            dtype=odml.DType.string,
                            definition="Occupation of the subject"))

parent.append(odml.Property(name="Gender",
                            value="female",
                            dtype=odml.DType.string,
                            definition="Sex of the subject"))

parent.append(odml.Property(name="HomePlanet",
                            value="Earth",
                            dtype=odml.DType.string,
                            definition="Home planet of the subject"))

# SET NEW PARENT NODE
parent = doc['TheCrew']['Ford Prefect']

# APPEND SUBSECTIONS

# APPEND PROPERTIES WITH VALUES
parent.append(odml.Property(name="Species",
                            value="Betelgeusian",
                            dtype=odml.DType.string,
                            definition="Species to which subject belongs to"))

parent.append(odml.Property(name="Nickname",
                            value="Ix",
                            dtype=odml.DType.string,
                            definition="Nickname(s) of the subject"))

parent.append(odml.Property(name="Occupation",
                            value="Researcher/Reporter",
                            dtype=odml.DType.string,
                            definition="Occupation of the subject"))

parent.append(odml.Property(name="Gender",
                            value="male",
                            dtype=odml.DType.string,
                            definition="Sex of the subject"))

parent.append(odml.Property(name="HomePlanet",
                            value="A planet in the vicinity of Betelgeuse",
                            dtype=odml.DType.string,
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
                            value="Heart of Gold",
                            dtype=odml.DType.string,
                            definition="Name of person/device"))

parent.append(odml.Property(name="OwnerStatus",
                            value="stolen",
                            dtype=odml.DType.string,
                            definition="Owner status of device"))

parent.append(odml.Property(name="DriveType",
                            value="Infinite Propability Drive",
                            dtype=odml.DType.string,
                            definition="Type of drive"))

parent.append(odml.Property(name="Technology",
                            value="secret",
                            dtype=odml.DType.string,
                            definition="Technology used to built device"))

parent.append(odml.Property(name="Length",
                            value=150.00,
                            dtype=odml.DType.float,
                            unit='m',
                            definition="Length of device"))

parent.append(odml.Property(name="Shape",
                            value="various",
                            dtype=odml.DType.string,
                            definition="Shape of device"))

parent.append(odml.Property(name="FactoryPlanet",
                            value="Damogran",
                            dtype=odml.DType.string,
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
parent.append(odml.Property(name="NoOfCybernetics",
                            value=2,
                            dtype=odml.DType.int,
                            definition="Number of cybernetic robots on the ship"))

parent.append(odml.Property(name="NamesOfCybernetics",
                            value=["Marvin",
                                   "Eddie"],
                            dtype=odml.DType.string,
                            definition="Names of cybernetic robots on the ship"))

# SET NEW PARENT NODE
parent = doc['TheStarship']['Cybernetics']['Marvin']

# APPEND SUBSECTIONS

# APPEND PROPERTIES WIHT VALUES
parent.append(odml.Property(name="Type",
                            value="Genuine People Personality",
                            dtype=odml.DType.string,
                            definition="Type of robot"))

parent.append(odml.Property(name="Manufacturer",
                            value="Sirius Cybernetics Corporation",
                            dtype=odml.DType.string,
                            definition="Manufacturer of robots"))

# SET NEW PARENT NODE
parent = doc['TheStarship']['Cybernetics']['Eddie']

# APPEND SUBSECTIONS

# APPEND PROPERTIES WIHT VALUES
parent.append(odml.Property(name="Type",
                            value="Genuine People Personality",
                            dtype=odml.DType.string,
                            definition="Type of robot"))

parent.append(odml.Property(name="Manufacturer",
                            value="Sirius Cybernetics Corporation",
                            dtype=odml.DType.string,
                            definition="Manufacturer of robots"))

odml.save(doc, save_to)

