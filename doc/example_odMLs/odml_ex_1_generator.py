import datetime
import os

import odml

odml_pythonpath = "./g-node/python-odml"
odmlrepo = 'http://portal.g-node.org/odml/terminologies/v1.0/terminologies.xml'

# CREATE A DOCUMENT
doc = odml.Document(author="D. N. Adams",
                    date=datetime.date(1979, 10, 12),
                    version=42,
                    repository=odmlrepo)

# CREATE AND APPEND THE MAIN SECTIONs
doc.append(odml.Section(name="TheCrew",
                        definition="Information on the crew",
                        type="crew"))

# SET NEW PARENT NODE
parent = doc['TheCrew']

# APPEND SUBSECTIONS
parent.append(odml.Section(name="Arthur Philip Dent",
                           type="crew/person",
                           definition="Information on Arthur Dent"))


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
                            value=None,
                            dtype=odml.DType.string,
                            definition="Nickname(s) of the subject"))

save_to = os.path.join(odml_pythonpath, "doc", "example_odMLs", "ex_1.odml")

odml.save(doc, save_to)
