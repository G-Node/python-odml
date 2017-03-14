import odml
import unittest

class TestMultiAppendDoc(unittest.TestCase):

    def test_msec(self):
        # Test case for odml_msec
        section_bulls = odml.Section(
                                     name="Chicago_Bulls",
                                     definition="NBA team based in Chicago, IL",
                                     type="team"
                                    )
       
        section_bulls0 = odml.Section(
                                      name="Chicago_Bulls",
                                      definition="NBA team based in Chicago, IL",
                                      type="team"
                                      )

        section_bulls2  = odml.Section(
                                       name="Chicago_City_Pub",
                                       definition="NBA team pub",
                                       type="pub"
                                      )

        section_bull3 = odml.Section(
                                     name="Bill_Clinton",
                                     definition="President supporter",
                                     type="fan"
                                    )

        prop1 = odml.Property(
                              name="Coach",
                              value="Phil Jackson",
                              definition="Run the team."
                             )
        
        prop2 = odml.Property(
                              name="Euro_player",
                              value="Tony Kukoc",
                              definition="European Player"
                             )

        section_bulls.append(
                             section_bulls2,
                             section_bull3,
                             prop1,
                             prop2
                            )
        
        section_bulls0.append(section_bulls2)
        section_bulls0.append(section_bull3)
        section_bulls0.append(prop1)
        section_bulls0.append(prop2)
         
        self.assertTrue(section_bulls.sections[0].name == section_bulls0.sections[0].name)
        self.assertTrue(section_bulls.sections[1].name == section_bulls0.sections[1].name)
        self.assertTrue(section_bulls.properties[0].name == section_bulls0.properties[0].name)
        self.assertTrue(section_bulls.properties[1].name == section_bulls0.properties[1].name)