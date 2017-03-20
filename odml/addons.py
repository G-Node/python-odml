import odml.tools.xmlparser as xml
import odml.tools.jsonparser as json
 
parsers = ["xml","json"]

def load(filename, backend="xml"):
	if backend in parsers:
	 	if backend == "xml":
	 		return xml.load(filename)
	 	elif backend == "json":
	 		return json.JSONReader().fromFile(open(filename))
	else:
		raise ValueError("No such parser")
 		
def save(obj, filename, backend="xml"):
	if backend in parsers:
	 	if backend == "xml":
	 		xml.XMLWriter(obj).write_file(filename)
	 	elif backend == "json":
	 		json.JSONWriter(obj).write_file(filename)
	else:
		raise ValueError("No such parser")		 

def display(obj, backend = "xml"):
	if backend in parsers:
	 	if backend == "xml":
	 		print (str(xml.XMLWriter(obj)))
	 	elif backend =="json":
	 		print (str(json.JSONWriter(obj)))
	else:
		raise ValueError("No such parser")		
  

 