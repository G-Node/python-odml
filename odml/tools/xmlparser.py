"""
The xmlparser module provides access to the XMLWriter and XMLReader classes.
Both handle the conversion of odML documents from and to XML files and strings.

The parser can be invoked standalone:
    python -m odml.tools.xmlparser file.odml
"""
import csv
import sys

from os.path import basename

from lxml import etree as ET
from lxml.builder import E
# this is needed for py2exe to include lxml completely
from lxml import _elementpath as _dummy
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from .. import format as ofmt
from ..info import FORMAT_VERSION
from .parser_utils import InvalidVersionException, ParserException, odml_tuple_export


XML_HEADER = """<?xml version="1.0" encoding="UTF-8"?>"""
EXTERNAL_STYLE_HEADER = """<?xml-stylesheet  type="text/xsl" href="odmlDocument.xsl"?>"""
INFILE_STYLE_HEADER = """<?xml-stylesheet type="text/xsl" href="#odml_local_style"?>
<!DOCTYPE odML [ <!ATTLIST xsl:stylesheet id ID #REQUIRED> ]>"""
INFILE_TEMPLATE_WRAPPER = """<xsl:stylesheet id="odml_local_style" version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fn="http://www.w3.org/2005/02/xpath-functions" xmlns:odml="http://www.g-node.org/odml">%s</xsl:stylesheet>"""
INFILE_STYLE_TEMPLATE = """<xsl:template match="odML"><xsl:variable name="repository" select="repository"/><html><head><meta charset="utf-8" /><title>odML | The Open metaData Markup Language</title><meta name="description" content="Markup language for the storage of scientific metadata" /></head><style>article,aside,details,figcaption,figure,footer,header,hgroup,nav,sec,summary{display:block}audio,canvas,video{display:inline-block;*display:inline;*zoom:1}audio:not([controls]){display:none}[hidden]{display:none}html{font-size:100%;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%}button,html,input,select,textarea{font-family:sans-serif}body{margin:0}a:focus{outline:thin dotted}a:active,a:hover{outline:0}h1{font-size:2em;margin:0.67em 0}h2{font-size:1.5em;margin:0.83em 0}h3{font-size:1.17em;margin:1em 0}h4{font-size:1em;margin:1.33em 0}h5{font-size:0.83em;margin:1.67em 0}h6{font-size:0.75em;margin:2.33em 0}abbr[title]{border-bottom:1px dotted}b,strong{font-weight:bold}blockquote{margin:1em 40px}dfn{font-style:italic}mark{background:#ff0;color:#000}p,pre{margin:1em 0}code,kbd,pre,samp{font-family:monospace, serif;_font-family:'courier new', monospace;font-size:1em}q{quotes:none}q:after,q:before{content:'';content:none}small{font-size:75%}sub,sup{font-size:75%;line-height:0;position:relative;vertical-align:baseline}sup{top:-0.5em}sub{bottom:-0.25em}dl,menu,ol,ul{margin:1em 0}dd{margin:0 0 0 40px}menu,ol,ul{padding:0 0 0 40px}nav ol,nav ul{list-style:none;list-style-image:none}img{border:0;-ms-interpolation-mode:bicubic}svg:not(:root){overflow:hidden}figure{margin:0}form{margin:0}fieldset{border:1px solid #c0c0c0;margin:0 2px;padding:0.35em 0.625em 0.75em}legend{border:0;padding:0;white-space:normal;*margin-left:-7px}button,input,select,textarea{font-size:100%;margin:0;vertical-align:baseline;*vertical-align:middle}button,input{line-height:normal}button,input[type="button"],input[type="reset"],input[type="submit"]{cursor:pointer;-webkit-appearance:button;*overflow:visible}button[disabled],input[disabled]{cursor:default}input[type="checkbox"],input[type="radio"]{box-sizing:border-box;padding:0;*height:13px;*width:13px}input[type="search"]{-webkit-appearance:textfield;-moz-box-sizing:content-box;-webkit-box-sizing:content-box;box-sizing:content-box}input[type="search"]::-webkit-search-decoration,input[type="search"]::-webkit-search-cancel-button{-webkit-appearance:none}button::-moz-focus-inner,input::-moz-focus-inner{border:0;padding:0}textarea{overflow:auto;vertical-align:top}table{border-collapse:collapse;border-spacing:0}.highlight table td{padding:5px}.highlight table pre{margin:0}.highlight,.highlight .w{color:#d0d0d0}.highlight .err{color:#151515;background-color:#ac4142}.highlight .c,.highlight .c1,.highlight .cd,.highlight .cm,.highlight .cs{color:#888}.highlight .cp{color:#f4bf75}.highlight .nt{color:#f4bf75}.highlight .o,.highlight .ow{color:#d0d0d0}.highlight .p,.highlight .pi{color:#d0d0d0}.highlight .gi{color:#90a959}.highlight .gd{color:#ac4142}.highlight .gh{color:#6a9fb5;font-weight:bold}.highlight .k,.highlight .kn,.highlight .kp,.highlight .kr,.highlight .kv{color:#aa759f}.highlight .kc{color:#d28445}.highlight .kt{color:#d28445}.highlight .kd{color:#d28445}.highlight .s,.highlight .s1,.highlight .s2,.highlight .sb,.highlight .sc,.highlight .sd,.highlight .sh,.highlight .sx{color:#90a959}.highlight .sr{color:#75b5aa}.highlight .si{color:#8f5536}.highlight .se{color:#8f5536}.highlight .nn{color:#f4bf75}.highlight .nc{color:#f4bf75}.highlight .no{color:#f4bf75}.highlight .na{color:#6a9fb5}.highlight .il,.highlight .m,.highlight .mb,.highlight .mf,.highlight .mh,.highlight .mi,.highlight .mo,.highlight .mx{color:#90a959}.highlight .ss{color:#90a959}body{font:14px/22px 'Quattrocento Sans', "Helvetica Neue", Helvetica, Arial, sans-serif;color:#666;font-weight:300;margin:0;padding:0 0 20px;background:#eae6d1}h1,h2,h3,h4,h5,h6{color:#333;margin:0 0 10px}dl,ol,p,pre,table,ul{margin:0 0 20px}ol.nested{margin:0}h1,h2,h3{line-height:1.1}a{color:#3399cc;font-weight:400;text-decoration:none}a small{font-size:11px;color:#666;margin-top:-0.6em;display:block}a.white{color:white}strong{font-weight:bold;color:#333}.wrapper{width:800px;margin:0 auto;position:relative}sec img{max-width:100%}blockquote{border-left:1px solid #ffcc00;margin:0;padding:0 0 0 20px;font-style:italic}code{font-family:'Lucida Sans', Monaco, Bitstream Vera Sans Mono, Lucida Console, Terminal;font-size:13px;color:#efefef;text-shadow:0 1px 0 #000;margin:0 4px;padding:2px 6px;background:#333;border-radius:2px}pre{padding:8px 15px;background:#333333;border-radius:3px;border:1px solid #c7c7c7;overflow:auto;overflow-y:hidden}pre code{margin:0;padding:0}table{width:100%;border-collapse:collapse}th{text-align:left;padding:5px 10px;border-bottom:1px solid #e5e5e5;color:#444}td{text-align:left;padding:5px 10px;border-bottom:1px solid #e5e5e5;border-right:1px solid #ffcc00}td:first-child{border-left:1px solid #ffcc00}hr{border:0;outline:none;height:11px;background:transparent center center repeat-x;margin:0 0 20px}hr.fatline{color:yellow;background-color:#336699;height:4px;margin-right:0;text-align:right;border:1px dashed black}hr.thinline{background-color:#336699;height:1px;margin-right:0;text-align:right}dt{color:#444;font-weight:700}header{padding:25px 20px 40px;margin:0;position:fixed;top:0;left:0;right:0;width:100%;text-align:center;background:#4276b6;box-shadow:1px 0 2px rgba(0, 0, 0, 0.75);z-index:99;-webkit-font-smoothing:antialiased;min-height:76px}header h1{font:40px/48px 'Copse', "Helvetica Neue", Helvetica, Arial, sans-serif;color:#f3f3f3;text-shadow:0 2px 0 #235796;margin:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;-o-text-overflow:ellipsis;-ms-text-overflow:ellipsis}header p{color:#d8d8d8;text-shadow:rgba(0, 0, 0, 0.2) 0 1px 0;margin:0}#banner{z-index:100;left:0;right:50%;height:50px;margin-right:-382px;position:fixed;top:115px;background:#1876dfff;border:1px solid #00000000;box-shadow:0 1px 3px rgba(0, 0, 0, 0.25);border-radius:0 2px 2px 0;padding-right:10px}#banner .button{border:1px solid #dba500;background:linear_gradient(#ffe788, #ffce38);border-radius:2px;box-shadow:inset 0 1px 0 rgba(255, 255, 255, 0.4), 0 1px 1px rgba(0, 0, 0, 0.1);background-color:#FFE788;margin-left:5px;padding:10px 12px;margin-top:6px;line-height:14px;font-size:14px;color:#333;font-weight:bold;display:inline-block;text-align:center}#banner .button:hover{background:linear_gradient(#ffe788, #ffe788);background-color:#ffeca0}#banner .fork{position:fixed;left:50%;margin-left:-325px;padding:10px 12px;margin-top:6px;line-height:14px;font-size:14px;background-color:#FFE788}#banner .downloads{float:right;margin:0 45px 0 0}#banner .downloads span{float:left;line-height:52px;font-size:90%;color:#9d7f0d;text-transform:uppercase;text-shadow:rgba(255, 255, 255, 0.2) 0 1px 0}#banner ul{list-style:none;height:40px;padding:0;float:left;margin-left:10px}#banner ul li{display:inline}#banner ul li a.button{background-color:#FFE788}#banner #logo{position:absolute;height:36px;width:36px;right:7px;top:7px;display:block}.navWrapper{margin-top:190px;position:relative}sec{width:800px;padding:30px 30px 50px;margin:190px 0 20px;position:relative;background:#fbfbfb;border-radius:3px;border:1px solid #cbcbcb;box-shadow:0 1px 2px rgba(0, 0, 0, 0.09), inset 0 0 2px 2px rgba(255, 255, 255, 0.5), inset 0 0 5px 5px rgba(255, 255, 255, 0.4)}navigationContainer{width:75%;padding:30px 30px 50px;margin:0 auto;display:block;background:#fbfbfb;box-shadow:0 1px 2px rgba(0, 0, 0, 0.09), inset 0 0 2px 2px rgba(255, 255, 255, 0.5), inset 0 0 5px 5px rgba(255, 255, 255, 0.4)}small{font-size:12px}nav{width:230px;position:fixed;top:220px;left:50%;margin-left:-580px;text-align:right}nav ul{list-style:none;list-style-image:none;font-size:14px;line-height:24px}nav ul li{padding:5px 0;line-height:16px}nav ul li.tag-h1{font-size:1.2em}nav ul li.tag-h1 a{font-weight:bold;color:#333}nav ul li.tag-h2+.tag-h1{margin-top:10px}nav ul a{color:#666}nav ul a:hover{color:#999}footer{width:180px;position:fixed;left:50%;margin-left:-530px;bottom:20px;text-align:right;line-height:16px}@media print, screen and (max-width: 1060px){div.wrapper{width:auto;margin:0}nav{display:none}footer,header,sec{float:none}footer h1,header h1,sec h1{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;-o-text-overflow:ellipsis;-ms-text-overflow:ellipsis}#banner{width:100%}#banner .downloads{margin-right:60px}#banner #logo{margin-right:15px}sec{border:1px solid #e5e5e5;border-width:1px 0;padding:20px auto;margin:190px auto 20px;max-width:600px}footer{text-align:center;margin:20px auto;position:relative;left:auto;bottom:auto;width:auto}}@media print, screen and (max-width: 720px){body{word-wrap:break-word}header{padding:20px;margin:0}header h1{font-size:32px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;-o-text-overflow:ellipsis;-ms-text-overflow:ellipsis}header p{display:none}#banner{top:80px}#banner .fork{float:left;display:inline-block;margin-left:0;position:fixed;left:20px}sec{margin-top:130px;margin-bottom:0;width:auto}header p.view,header ul{position:static}}@media print, screen and (max-width: 480px){header{position:relative;padding:5px 0;min-height:0}header h1{font-size:24px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;-o-text-overflow:ellipsis;-ms-text-overflow:ellipsis}sec{margin-top:5px}#banner{display:none}header ul{display:none}}@media print{body{padding:0.4in;font-size:12pt;color:#444}}@media print, screen and (max-height: 680px){footer{text-align:center;margin:20px auto;position:relative;left:auto;bottom:auto;width:auto}}@media print, screen and (max-height: 480px){nav{display:none}footer{text-align:center;margin:20px auto;position:relative;left:auto;bottom:auto;width:auto}}
</style><body><header><h1><a class="white" href="https://templates.g-node.org/templates.xml">odML metadata document</a></h1></header><div class="navWrapper"><navigationContainer><div id="navigationContainer"><hr class="fatline" /><p><h2>Document info</h2><b>Author: </b><xsl:if test="author"><xsl:value-of select="author"/></xsl:if><br/><b>Date: </b><xsl:if test="date"><xsl:value-of select="date"/></xsl:if><br/><b>Version: </b><xsl:if test="version"><xsl:value-of select="version"/></xsl:if><br/><b>Repository: </b><xsl:if test="repository"><xsl:value-of select="repository"/></xsl:if><br/></p><hr class="fatline" /><h2>Structure</h2><font size ="-1" ><xsl:if test="section"><xsl:for-each select="section"><xsl:call-template name="sectionTemplate"><xsl:with-param name="navigation">1</xsl:with-param><xsl:with-param name="anchorBase">Sec</xsl:with-param><xsl:with-param name="url" select="$repository"/></xsl:call-template></xsl:for-each></xsl:if></font><br/></div><div id="contentContainer"><hr class="fatline" /><h2>Content</h2><xsl:if test="section"><xsl:for-each select="section"><xsl:call-template name="sectionTemplate"><xsl:with-param name="navigation">0</xsl:with-param><xsl:with-param name="anchorBase">Sec</xsl:with-param><xsl:with-param name="url" select="$repository"/></xsl:call-template></xsl:for-each></xsl:if></div></navigationContainer></div></body></html></xsl:template><xsl:template name="sectionTemplate" match="section"><xsl:param name="navigation"/><xsl:param name="anchorBase"/><xsl:param name="url"/><xsl:variable name="anchorName" select="concat($anchorBase,position())"/><xsl:variable name="repository"><xsl:choose><xsl:when test="repository"><xsl:value-of select ="repository"/></xsl:when><xsl:otherwise><xsl:value-of select ="$url"/></xsl:otherwise></xsl:choose></xsl:variable><xsl:choose><xsl:when test="$navigation = 1"><ol class="nested"><font size="normal"><a href="#{$anchorName}"><xsl:value-of select="name"/> (type: <xsl:value-of select="type"/>)</a></font><xsl:if test="section"><xsl:for-each select="section"><xsl:call-template name="sectionTemplate"><xsl:with-param name="navigation" select="$navigation"/><xsl:with-param name="anchorBase" select="concat($anchorName,'SubSec')"/><xsl:with-param name="url" select="$repository"/></xsl:call-template></xsl:for-each></xsl:if></ol></xsl:when><xsl:otherwise><a name="{$anchorName}"><h3><xsl:value-of select="name"/> Section</h3></a><p><b>Type: </b><xsl:value-of select="type"/><br/><xsl:choose><xsl:when test ="repository"><b>Repository: </b><xsl:value-of select="repository"/><br/></xsl:when><xsl:otherwise><b>Repository: </b><xsl:value-of select="$repository"/><br/></xsl:otherwise></xsl:choose><b>Link: </b><xsl:if test="link"><xsl:value-of select="link"/></xsl:if><br/><b>Include:</b><xsl:if test="include"><font color="red"><xsl:value-of select="include"/></font></xsl:if><br/><b>Definition: </b><xsl:if test="definition"><xsl:value-of select="definition"/></xsl:if><br/></p><xsl:if test="property"><table border="1" rules="rows" width="100%"><font size="-1"><tr bgcolor="#336699" align="left" valign="middle"><th><font size="+1" color="white"><b>Name</b></font></th><th><font size="+1" color="white"><b>Value</b></font></th><th><font size="+1" color="white"><b>Unit</b></font></th><th><font size="+1" color="white"><b>Type</b></font></th><th><font size="+1" color="white"><b>Uncertainty</b></font></th><th><font size="+1" color="white"><b>Definition</b></font></th><th><font size="+1" color="white"><b>Dependency</b></font></th><th><font size="+1" color="white"><b>Dependency Value</b></font></th></tr><xsl:for-each select="property"><xsl:variable name="anchor"><xsl:value-of select ="name"/></xsl:variable><tr><td width="15%"><a name="{$anchor}"/><p><xsl:value-of select="name"/></p></td><td width="10%"><p><xsl:value-of select="value"/></p></td><td width="5%"><p><xsl:value-of select="unit"/><br/></p></td><td width="5%"><p><xsl:value-of select="type"/></p></td><td width="5%"><p><xsl:value-of select="uncertainty"/><br/></p></td><td width="22.5%"><p><xsl:value-of select="definition"/></p></td><td width="5%"><p><xsl:value-of select="dependency"/></p></td><td width="5%"><p><xsl:value-of select="dependencyValue"/></p></td></tr></xsl:for-each></font></table></xsl:if><a href="#top"><tiny>top</tiny></a><hr class="thinline" /><xsl:if test="section"><xsl:for-each select="section"><xsl:call-template name="sectionTemplate"><xsl:with-param name="navigation" select="$navigation"/><xsl:with-param name="anchorBase" select="concat($anchorName,'SubSec')"/><xsl:with-param name="url" select="$repository"/></xsl:call-template></xsl:for-each></xsl:if></xsl:otherwise></xsl:choose></xsl:template>
"""


def parse_cardinality(val):
    """
    Parses an odml specific cardinality from a string.

    If the string content is valid, returns an appropriate tuple.
    Returns None if the string is empty or the content cannot be
    properly parsed.

    :param val: string
    :return: None or 2-tuple
    """
    if not val:
        return None

    # Remove parenthesis and split on comma
    parsed_vals = val.strip()[1:-1].split(",")
    if len(parsed_vals) == 2:
        min_val = parsed_vals[0].strip()
        max_val = parsed_vals[1].strip()

        min_int = min_val.isdigit() and int(min_val) >= 0
        max_int = max_val.isdigit() and int(max_val) >= 0

        if min_int and max_int and int(max_val) > int(min_val):
            return int(min_val), int(max_val)

        if min_int and max_val == "None":
            return int(min_val), None

        if max_int and min_val == "None":
            return None, int(max_val)

    # Todo we were not able to properly parse the current cardinality
    # add an appropriate Error/Warning
    return None


def to_csv(val):
    """
    Modifies odML values for serialization to strings and files.

    :param val: odML value.
    :return: modified value string.
    """
    # Make sure all individual values do not contain
    # leading or trailing whitespaces.
    unicode_values = list(map(str.strip, map(str, val)))
    stream = StringIO()
    writer = csv.writer(stream, dialect="excel")
    writer.writerow(unicode_values)
    # Strip any csv.writer added carriage return line feeds
    # and double quotes before saving.
    csv_string = stream.getvalue().strip().strip('"')
    if len(unicode_values) > 1:
        csv_string = "[" + csv_string + "]"
    return csv_string


def from_csv(value_string):
    """
    Reads a string containing odML values and parses them into a list.

    :param value_string: string of odML values.
    :return: list of values.
    """
    if not value_string:
        return []
    if value_string[0] == "[" and value_string[-1] == "]":
        value_string = value_string[1:-1]
    else:
        # This is a single string entry, any comma contained
        # is part of the value and must not be used to
        # split up the string.
        return [value_string]

    if not value_string:
        return []
    stream = StringIO(value_string)
    stream.seek(0)
    reader = csv.reader(stream, dialect="excel")
    return list(reader)[0]


class XMLWriter:
    """
    Creates XML nodes storing the information of an odML Document.
    """
    header = "%s\n%s\n" % (XML_HEADER, EXTERNAL_STYLE_HEADER)

    def __init__(self, odml_document):
        self.doc = odml_document

    @staticmethod
    def save_element(curr_el):
        """
        Returns an XML node for the odML object curr_el.

        :param curr_el: odML object. Supported objects are odml.Document, odml.Section,
                        odml.Property.
        :returns: parsed XML Node.
        """
        fmt = curr_el.format()
        cur = E(fmt.name)

        # generate attributes
        if isinstance(fmt, ofmt.Document.__class__):
            cur.attrib['version'] = FORMAT_VERSION

        # generate elements
        for k in fmt.arguments_keys:
            if not hasattr(curr_el, fmt.map(k)):
                continue

            val = getattr(curr_el, fmt.map(k))
            if val is None:
                continue

            if isinstance(fmt, ofmt.Property.__class__) and k == "value":
                # Custom odML tuples require special handling for save loading from file.
                if curr_el.dtype and curr_el.dtype.endswith("-tuple") and val:
                    ele = E(k, odml_tuple_export(val))
                else:
                    ele = E(k, to_csv(val))
                cur.append(ele)
            else:
                if isinstance(val, list):
                    for curr_val in val:
                        if curr_val is None:
                            continue
                        ele = XMLWriter.save_element(curr_val)
                        cur.append(ele)
                else:
                    ele = E(k, str(val))
                    cur.append(ele)
        return cur

    def __str__(self):
        return ET.tounicode(self.save_element(self.doc), pretty_print=True)

    def __unicode__(self):
        return ET.tounicode(self.save_element(self.doc), pretty_print=True)

    def write_file(self, filename, local_style=False, custom_template=None):
        """
        write_file saves the XMLWriters odML document to an XML file.

        :param filename: location and name where the file will be written to.
        :param local_style: Optional boolean. By default an odML XML document is saved
                            with a default header containing an external stylesheet for
                            viewing with a local or remote server. Set up for local
                            viewing with the 'odmlview' command line script.
                            When set to True, the saved XML file will contain a default
                            XSL stylesheet to render the XML file in a web-browser.
                            Note that Chrome requires the '.odml' extension to be
                            registered as "application/xml" in the Mime-type database.
        :param custom_template: Optional string. Provide a custom XSL template to render
                                the odML XML file in a web-browser.
                                Please note, that the custom XSL template must not be a
                                full XSL stylesheet, but has to start and end with the
                                tag: '<xsl:template match="odML">[custom]</xsl:template>'.
        """
        # calculate the data before opening the file in case we get any exception
        data = str(self)

        with open(filename, "w", encoding = "utf-8") as file:
            file.write("%s\n" % XML_HEADER)
            if not local_style and not custom_template:
                file.write("%s\n" % EXTERNAL_STYLE_HEADER)
            else:
                file.write("%s\n" % INFILE_STYLE_HEADER)

                template = INFILE_TEMPLATE_WRAPPER % INFILE_STYLE_TEMPLATE
                if custom_template:
                    template = INFILE_TEMPLATE_WRAPPER % custom_template

                replace = """<odML version="%s">""" % FORMAT_VERSION
                replacement = """<odML version="%s">\n%s\n""" % (FORMAT_VERSION, template)
                data = data.replace(replace, replacement)

            file.write(data)


def load(filename):
    """
    Shortcut function for XMLReader().from_file(filename).
    """
    return XMLReader().from_file(filename)


class XMLReader(object):
    """
    A reader to parse XML files or strings into odML data structures.

    Usage:
        >>> doc = XMLReader().from_file("file.odml")
    """

    def __init__(self, ignore_errors=False, show_warnings=True, filename=None):
        """
        :param ignore_errors: To allow loading and fixing of invalid odml files
                              encountered errors can be converted to warnings
                              instead. Such a document can only be saved when
                              all errors have been addressed though.
        :param show_warnings: Toggle whether to print warnings to the command line.
                              Any warnings can be accessed via the Reader's class
                              warnings attribute after parsing is done.
        :param filename: Path to an odml file.
        """
        self.parser = ET.XMLParser(remove_comments=True)
        self.tags = dict([(obj.name, obj) for obj in ofmt.__all__])
        self.ignore_errors = ignore_errors
        self.show_warnings = show_warnings
        self.filename = filename
        self.warnings = []

    @staticmethod
    def _handle_version(root):
        """
        Checks if the odML version of a handed in parsed lxml.etree is supported
        by the current library and raise a ParserException otherwise. If the
        lxml.etree contains an XML file of a previous odML format version,
        an InvalidVersionException is raised.

        :param root: Root node of a parsed lxml.etree. The root tag has to
                     contain a supported odML version number, otherwise it is not
                     accepted as a valid odML file.
        """
        if root.tag != 'odML':
            raise ParserException("Expecting <odML> tag but got <%s>.\n" % root.tag)

        if 'version' not in root.attrib:
            msg = "Could not find format version attribute in <odML> tag.\n"
            raise ParserException(msg)

        if root.attrib['version'] != FORMAT_VERSION:
            msg = ("Cannot parse odML document with format version '%s'. \n"
                   "\tUse the 'VersionConverter' from 'odml.tools.converters' "
                   "to import previous odML formats."
                   % root.attrib['version'])
            raise InvalidVersionException(msg)

    def from_file(self, xml_file):
        """
        Parses the datastream from a file like object and return an odML data structure.
        If the file cannot be parsed, a ParserException is raised.

        :param xml_file: file path to an XML input file or file like object.
        :returns: a parsed odml.Document.
        """
        try:
            root = ET.parse(xml_file, self.parser).getroot()
            if hasattr(xml_file, "close"):
                xml_file.close()
        except ET.XMLSyntaxError as exc:
            raise ParserException(exc.msg)

        self._handle_version(root)
        doc = self.parse_element(root)

        # Provide original file name via the in memory document
        if isinstance(xml_file, str):
            doc.origin_file_name = basename(xml_file)

        return doc

    def from_string(self, string):
        """
        Parses an XML string and return an odML data structure.
        If the string cannot be parsed, a ParserException is raised.

        :param string: XML string.
        :returns: a parsed odml.Document.
        """
        try:
            root = ET.XML(string, self.parser)
        except ET.XMLSyntaxError as exc:
            raise ParserException(exc.msg)

        self._handle_version(root)
        return self.parse_element(root)

    def check_mandatory_arguments(self, data, arg_class, tag_name, node):
        """
        Checks if a passed attribute is required for a specific odML class.
        If the attribute is required and not present in the data, the
        parsers error method is called.

        :param data: list of mandatory arguments.
        :param arg_class: odML class corresponding to the content of the parent node.
        :param tag_name: name of the current XML node.
        :param node: XML node.
        """
        for k, val in arg_class.arguments:
            if val != 0 and not arg_class.map(k) in data:
                self.error("missing element <%s> within <%s> tag\n" %
                           (k, tag_name) + repr(data), node)

    def is_valid_argument(self, tag_name, arg_class, parent_node, child=None):
        """
        Checks if an argument is valid in the scope of a specific odML class.
        If the attribute is not valid, the parsers error method is called.

        :param tag_name: string containing the name of the current XML node.
        :param arg_class: odML class corresponding to the content of the parent node.
        :param parent_node: the parent XML node.
        :param child: current XML node.
        """
        if tag_name not in arg_class.arguments_keys:
            self.error("Invalid element <%s> inside <%s> tag\n" %
                       (tag_name, parent_node.tag),
                       parent_node if child is None else child)

    def error(self, msg, elem):
        """
        If the parsers ignore_errors property is set to False, a ParserException
        will be raised. Otherwise the message is passed to the parsers warning
        method.

        :param msg: Error message.
        :param elem: XML node corresponding to the error.
        """
        if elem is not None:
            msg += " (line %d)" % elem.sourceline
        if self.ignore_errors:
            return self.warn(msg, elem)
        raise ParserException(msg)

    def warn(self, msg, elem):
        """
        Adds a message to the parsers warnings property. If the parsers show_warnings
        property is set to True, an additional error message will be written
        to sys.stderr.

        :param msg: Warning message.
        :param elem: XML node corresponding to the warning.
        """
        if elem is not None:
            msg = "warning[%s:%d:<%s>]: %s\n" % (
                self.filename, elem.sourceline, elem.tag, msg)
        else:
            msg = "warning: %s\n" % msg

        self.warnings.append(msg)
        if self.show_warnings:
            sys.stderr.write(msg)

    def parse_element(self, node):
        """
        Identifies the odML object corresponding to the current XML node e.g.
        odml.Document, odml.Section or odml.Property. It will call the
        parsers method corresponding to the identified odML object e.g. parse_odML,
        parse_section, parse_property and return the results.

        :param node: XML node.
        """
        if node.tag not in self.tags:
            self.error("Invalid element <%s> " % node.tag, node)
            return None  # won't be able to parse this one
        return getattr(self, "parse_" + node.tag)(node, self.tags[node.tag])

    def parse_tag(self, root, fmt, insert_children=True):
        """
        Parse an odml node based on the format description *fmt*
        and instantiate the corresponding object.
        :param root: lxml.etree node containing an odML object or object tree.
        :param fmt: odML class corresponding to the content of the root node.
        :param insert_children: Bool value. When True, child elements of the root node
                                will be parsed to their odML equivalents and appended to
                                the odML document. When False, child elements of the
                                root node will be ignored.
        """
        arguments = {}
        extra_args = {}
        children = []

        for k, val in root.attrib.iteritems():
            k = k.lower()
            # 'version' is currently the only supported XML attribute.
            if k == 'version' and root.tag == 'odML':
                continue

            # We currently do not support XML attributes.
            self.error("Attribute not supported, ignoring '%s=%s' " % (k, val), root)

        for node in root:
            node.tag = node.tag.lower()
            self.is_valid_argument(node.tag, fmt, root, node)
            if node.tag in fmt.arguments_keys:
                # this is a heuristic, but works for now
                if node.tag in self.tags and node.tag in fmt.map_keys:
                    sub_obj = self.parse_element(node)
                    if sub_obj is not None:
                        extra_args[fmt.map(node.tag)] = sub_obj
                        children.append(sub_obj)
                else:
                    tag = fmt.map(node.tag)
                    if tag in arguments:
                        self.warn("Element <%s> is given multiple times in "
                                  "<%s> tag" % (node.tag, root.tag), node)

                    # Special handling of values;
                    curr_text = node.text.strip() if node.text else None
                    if tag == "values" and curr_text:
                        content = from_csv(node.text)
                        arguments[tag] = content
                    # Special handling of cardinality
                    elif tag.endswith("_cardinality") and curr_text:
                        arguments[tag] = parse_cardinality(node.text)
                    else:
                        arguments[tag] = curr_text
            else:
                self.error("Invalid element <%s> in odML document section <%s> "
                           % (node.tag, root.tag), node)

        check_args = dict(list(arguments.items()) + list(extra_args.items()))
        self.check_mandatory_arguments(check_args, fmt, root.tag, root)

        # Instantiate the current odML object with the parsed attributes.
        obj = fmt.create()
        try:
            obj = fmt.create(**arguments)
        except Exception as exc:
            self.error(str(exc), root)

        if insert_children:
            for child in children:
                obj.append(child)

        return obj

    # function 'parse_element' requires the captialisation of 'parse_odML'
    # to properly parse the root of an odML document.
    def parse_odML(self, root, fmt):
        """
        Parses the content of an XML node into an odml.Document including all
        subsections and odml.Properties.

        :param root: XML node
        :param fmt: odML class corresponding to the content of the XML node.
        :return: parsed odml.Document
        """
        doc = self.parse_tag(root, fmt)
        return doc

    def parse_section(self, root, fmt):
        """
        Parses the content of an XML node into an odml.Section including all subsections
        and odml.Properties.

        :param root: XML node
        :param fmt: odML class corresponding to the content of the XML node.
        :return: parsed odml.Section
        """
        return self.parse_tag(root, fmt)

    def parse_property(self, root, fmt):
        """
        Parses the content of an XML node into an odml.Property.

        :param root: XML node
        :param fmt: odML class corresponding to the content of the XML node.
        :return: parsed odml.Property
        """
        return self.parse_tag(root, fmt, insert_children=False)


if __name__ == '__main__':
    import argparse
    import odml.tools.dumper as dumper

    args = sys.argv[1:]

    desc = "Print content of an odml xml file to the stdout"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("odml_file", help="Path to odml xml file")
    args = parser.parse_args(args)

    dumper.dump_doc(load(args.odml_file))
