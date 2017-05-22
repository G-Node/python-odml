import odml
import unittest
import datetime as dt


class TestMultiAppendDoc(unittest.TestCase):

    def test_mdoc(self):
        jordan = odml.Document(
            author="Michael Jordan",
            date=dt.date(1991, 9, 1),
            version=0.01
        )

        mjordan = odml.Document(
            author="Michael Jordan",
            date=dt.date(1991, 9, 1),
            version=0.01
        )

        section_bulls = odml.Section(
            name="Chicago_Bulls",
            definition="NBA team based in Chicago, IL",
            type="team"
        )

        section_nc = odml.Section(
            name="North_Caroline",
            definition="NCAA team based in Wilmington, NC",
            type="team"
        )
        jordan.append(section_bulls)
        jordan.append(section_nc)
        mjordan.append(
            section_bulls,
            section_nc,
        )
        self.assertTrue(jordan.sections[0].name == mjordan.sections[0].name)
        self.assertTrue(jordan.sections[1].name == mjordan.sections[1].name)
