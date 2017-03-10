import odml
import unittest
import datetime as dt

class TestAppendProperty(unittest.TestCase):

	def test_mdoc_property_add(self):
         jordan = odml.Document(
                                author="Michael Jordan",
                                date=dt.date(1991,9,1),
                                version=0.01
                               )
 
          
         prop1 = odml.Property(
                              name="Coach",
                              value="Phil Jackson",
                              definition="Run the team."
                             ) 

     
         self.assertRaises(KeyError, lambda: jordan.append(prop1))
   
        
