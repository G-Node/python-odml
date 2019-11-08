# Changelog

Used to document all changes from previous releases and collect changes 
until the next release.

# Latest changes in master

## Minor changes, updates and fixes
- The `section_subclasses.yaml` file is moved from the `doc` folder to the new `odml/resources` folder. This allows usage of the file with all install options. See issue #212 for details.

# Version 1.4.3

## Introduction of odML templates support and update in odML terminology handling

Support for importing and working with odML templates is added:
- the core library now features the `TemplateHandler` class to handle import and usage of odML templates.
- the default URL to fetch templates from has been set to `https://templates.g-node.org`.
- all terminology URLs are updated to the new terminology deployment at `https://terminology.g-node.org`.

## Additional console script: 'odmlview'

Currently most web browsers no longer support viewing local files that include further local files like stylesheets; check [here](https://developer.mozilla.org/en-US/docs/Archive/Misc_top_level/Same-origin_policy_for_file:_URIs) for additional details. The console script `odmlview` provides a local webserver that is able to properly serve odML XML files from a local directory and render them correctly, if the appropriate stylesheets are present in the same directory.

```
'odmlview' sets up a minimal webserver to view odml files saved in the
XML format via the webbrowser. After it is started, the webserver will
open a new tab in the default webbrowser and display the content of
the directory the server was started from. odML files can then be
viewed from there.
To properly render XML, an odML file may contain the element
'<?xml-stylesheet  type="text/xsl" href="odmlDocument.xsl"?>' where the
'odmlDocument.xsl' stylesheet should reside in the same directory as the
odML file to be rendered. By using the '--fetch' flag the latest version
of this stylesheet will be downloaded from `templates.g-node.org` to
the current directory when starting up the service.
```

## Console script 'odmlconversion' is renamed
The console script `odmlconversion` is renamed to `odmlconvert`. For backwards compatibility the script will be available as `odmlconversion` with a deprecation notice.

## 'pyyaml' dependency update
The `pyyaml` dependency has been changed to the non-breaking beta version 4.2b4. See issue #291 for details.

## Minor changes, updates and fixes
- odML entity IDs are automatically added when converting from odML version 1 to odMl version 1.1 for `Document`, `Section` and `Property` elements. If an ID already exists, it stays the same, if it is compatible with the Python UUID types. Otherwise (also if empty) a new ID is created for the odML entity.
- `Property` can now be set as `int` with value `0`. See issue #314 for details.
- appending and extending of `Property` values of dtypes `person`, `url` and `text` is now possible. See issue #318 for details.
- the default `RDFWriter` format is set to `turtle`. See issue #214 for details.
- the `RDFWriter` now checks for a given file extension within the RDF document name if accidentally given there. See issue #213 for details.
- the `RDFWriter` now throws a `ValueError` if an unsupported RDF format is given. See issue #215 for details.
- the `XMLReader` now properly handles entity creation failures when started with option `ignore_errors=True`. See issue #276 for details.
- the `pprint` method has been added to `Document` to print while document section. See issue #319 for details.
- the README file has been changed from `rst` to the `md` format.
- the current tutorial has been updated to include latest changes.
- the automated builds have been updated to include Python versions 3.7 and 3.8; version 3.4 has been removed since it is no longer supported on travis.


# Version 1.4.2

## Print methods

`pprint` methods have been added to both `Section` and `Property`
to print whole Section trees with their child sections and properties.
The `__repr__` style of `Section` and `Property` has been changed to
be more similar to the [nixpy](https://github.com/G-Node/nixpy) `__repr__` style.
Printing a `Section` now also features the immediate `Property` child count
in addition to the immediate `Section` child count. See #309.

## Deprecation of 'Property.value' in favor of 'Property.values'

To make working with odML more similar to working with the 
metadata part of [nixpy](https://github.com/G-Node/nixpy), the `Property.value` 
attribute has been marked deprecated and the `Property.values` 
attribute has been added. See #308. 

## Uncertainty changes

Uncertainty is now limited to float only. See #294.

## Version converter changes

The VersionConverter dealt with an edge case of XML test files with opening <B0> tags 
that were missing their closing tag rendering them broken. Catching this one edge case 
circumvented opening XML files via lxml, leaving the resulting document open to various 
encoding problems.

Support to resolve the specific tag edge cases is dropped in favour of properly opening 
XML files via lxml. See #301.

## Additional console script

The `odmlconversion` convenience console script has been added to convert multiple 
previous odML version files to the latest odML version.

## Changes in cloning behaviour

When cloning a `Section` or a `Property` by default the id of any object is changed
to a new UUID. The cloning methods now feature a new `keep_id` attribute. If set to
`True`, the cloned object and any cloned children retain their original id. This
is meant to create exact copies of Section-Property trees in different documents.

## Additional validation

When a document is saved, a new validation check makes sure, that a document
contains only unique UUIDs this is required due to the introduction of creating
clones with identical ids. 


# Version 1.4.1

## Dependency changes

- `pyyaml` was version fixed on 3.13 to circumvent introduced breaking changes in the library. See #291, #292, #296, #298.
- `docopt` was added to support console scripts

## Converter and Parser fixes

- Fixes that an XML file with an UTF-8 encoding file header was not being properly parsed by the `VersionConverter` XML parser. See #288, #296.
- Fixes the `XMLParser` that when reading a single string value from csv which contains commata, it now remains a single value and is not split up at each comma. See #295, #296.
- In the `XMLParser` any leading or trailing whitespaces are removed from any string values when it is written to csv. Along the same lines, multiple values that are saved to file via the `VersionConverter` do not contain leading whitespaces any longer. See #296.
- Thorough encoding and usage of `unicode` has been introduced to all Parsers and Converters to avoid encoding errors with Python 2 and Python 3. See #297.

## Changes in `Section` and `Property` SmartList

- Adds `SmartList.sort()`. By default `Document` and `Section` child lists will retain the order in which child elements were added, but now a sort by name can be manually triggered. See #290.
- Adds `SmartList` comparison magic methods to partially address #265. The introduction of the RDF backend led to an issue when comparing odML entities. The used RDF library `rdflib` does not respect child order upon loading of a file, odML entities with children can not be compared without sorting the child elements. The added magic methods sort child elements by name before comparison without changing the actual order of the child elements. This only addresses the issue for `Section` and `Property` child lists, but does not solve the problem for the order of `Property.values`. See #290.

## Document format update

- A new private attribute `_origin_file_name` is added to the `Document` entity. When an odML document is loaded from file, this attribute is now set with the file name from whence the document was loaded. See #297.

## RDF format changes

- The RDF class `Seq` is now used instead of `Bag` to store `odml.Property` values to respect the order of values. See #292.
- Since `rdflib` currently does not support proper `Seq` behaviour with RDF `li` items, for now the index of the value items will be manually written as RDF properties, which `rdflib` supports when reading an RDF file. See #292.
- When writing an RDF file from an odML document that features an `_origin_file_name`, the value is exported as `odml:hasFileName`. See #297.
- `xml` is now the default `ODMLWriter` format when writing a document to RDF since the XML format of RDF is still the format with the broadest acceptance. See #297.

## Addition of console scripts

- The `odmltordf` convenience console script has been added to convert multiple odML files to the RDF format from any odML format or version. See #298.


# Version 1.4.0
## Breaking changes

The switch from odML version 1.3 to 1.4 contains many cool updates which should make work more comfortable, but also includes some breaking changes.

### Update of the odML file format version
- The odML format version number in odML files has changed from "1" to "1.1".

### Changes in odML classes
- The odML class hierarchy has been flattened:
  - removing `base._baseobj` class, leaving `BaseObject` as the root odML class.
  - removing `doc.Document` class, leaving `BaseDocument` as the only odML Document class.
  - removing `section.Section` class, leaving `BaseSection` as the only odML Section class.
  - removing `property.Property` class leaving `BaseProperty` as the only odML Property class.
- `baseobject` and `sectionable` are renamed to `BaseObject` and `Sectionable` respectively.
- `base.SafeList` and `base.SmartList` have been merged, `base.SafeList` has been removed.
- `base.SmartList` can now only contain Sections or Properties. See #272.
- The `reorder` method is moved from the `base` to the `Section` class. See #267.

### Changes in Value handling: 
- The `Value` class has been removed.
- `Property.value` now always holds a list of uniform values. `Property.value` always 
    returns a copy of the actual value list. See #227.
- Values can only be changed directly via the `__setitem__` method of a `Property`
- `Value` attributes `uncertainty`, `unit`, `dtype` and `reference` have been moved to 
    `Property` and now apply to all values of the `Property.value` list.
- The `Value` attributes `filename`, `encoder` and `checksum` have been removed.

### DType changes:
- The `binary` dtype has been removed. Providing binary content via odML files is 
    discouraged in favor of providing a reference to the origin files using the `URL` 
    dtype instead.

### Mapping
- Any `mapping` functionality has been removed.

### Minor breaking changes
- `XMLReader.fromFile()` and `.fromString()` have been renamed to `.from_file()` and `.from_string()` respectively.


## Features and changes

### Required odML entity attributes handling
- Required attributes of odML entities in `odml.format` where changed: `Section.name`, 
    `Section.type` and `Property.name` are the only attributes set to be required for 
    their respective odML entities. See #240.
- `Section.name` and `Property.name` can now be `None` on init. If this is the case, the 
    entities' `id` value is used as `name` value.
- Hardcoded checks for existing `name` attributes in the XML Parser are removed. Only 
    attributes set as required in `format` are now used to check for missing required odML 
    entity attributes. See #241.
- The `name` attribute of a `Section` or a `Property` can now only be rewritten if there 
    is no sibling with the same name on the same hierarchical level. See #283.

### Addition of the 'id' attribute
- `Document`, `Section` and `Property` now have an `id` attribute to uniquely identify any 
    entity. If no valid id is provided when an entity is initialized, an id is 
    automatically generated and assigned.
- Adding the `new_id()` method to `Document`, `Section` and `Property` which generates 
    and sets a new valid id for any entity. See #262.

### Changes in DType handling
- Setting a dtype now also supports odML style tuple types. See #254.
- DTypes now always return the defined default values if a value is `None` or `""`.
- Any boolean dtype value other than `"false", "f", 0, False, "true", "t", 1` or `True` 
    will now raise a `ValueError`. See #224

### 'base.Sectionable' (Document and Section) changes
- Adds a `base.Sectionable.extend` method for child Sections and Properties. See #237.
- Refactors the `base.Sectionable.insert` and `.append` methods. Only proper 
    `BaseSections` with a unique name can be added to the Section child list of a 
    `Sectionable`.
- Appending multiple Sections or Properties has been removed from the `append` method to 
    mirror Property `append` functionality and since `extend` now serves this need.

### 'Section' and 'Property' merge 
- `Property` now provides a `merge` method to merge two properties. This will sync all but 
    the dependency and dependencyValue attributes. ValueErrors are raised, if information 
    is set in both properties but are in conflict. See #221.
- Adds a `Section.merge_check()` method which validates whether a Section including all 
    its sub-sections and sub-properties can properly be merged. A `ValueError` is raised 
    if any potential merge problem arises. This is necessary since a recursive Section 
    merge cannot be easily rolled back once begun.
- A Section merge imports `reference` and `definition` from the "source" Section if they 
    were `None` in the "destination" Section. See #273.
- Adds a `strict` flag to any `merge` method. Now all `Section` and `Property` attribute 
    checks during a merge will only be done, if `strict=True`. On `strict=False` a 
    `Section` or `Property` attribute will only be replaced with the "source" value, if 
    the "destination" value is `None`. Otherwise the "destination" value will be kept and 
    the "source" value lost. See #270.

### Changes of 'Section' and 'Property' clone
- When a `Section` or a `Property` is cloned, a new id is set for the clone and of any 
    cloned children. See #259.

### 'Document' changes
- Tuples of Sections can now no longer be used with `Document.append` since 
    `Document.extend` should be used to add multiple new Sections to a Document.

### 'Section' changes
- Adds a `Section.extend` method.

### 'Property' changes
- `Property` has the new attribute `value_origin` which may contain the origin of the 
    property's value e.g. a filename.
- `Property` init now supports setting all attributes as well as its parent.
- `Property` now provides `append`, `extend` and `remove` methods to change the actual 
    value list. This approach is required to ensure DType checks when adding new values 
    to an existing list. See #223. 
- Only valid dtypes can now be set on `Property` init. See #253.

### Terminology changes
- The default odML terminology repository is set to `http://portal.g-node.org/odml/terminologies/v1.1/terminologies.xml`.

### Changes in Tools and IO
- The `XMLParser` can now be run in warning mode: any errors encountered during parsing 
    will just print a warning, but will not stop and exit during the parsing process.
- An odML document can now only be saved, if the validation does not show any errors. 
    Saving an invalid document will stop the process before saving and print all 
    encountered errors.
- All parsers are now more relaxed when encountering unsupported or missing tags and only 
    print warnings instead of ending with an exception. Warnings are collected and can be 
    accessed via the parser object.
- When trying to open a file with any of the odML parsers, the document format version 
    number is checked. If the version number does not match the supported one, file 
    loading will fail with an exception. 

## New tools
- Added the `tools.RDFWriter` and `toosl.RDFReader` classes, which enable the export of 
    odML documents to RDF and also provides the used ontology OWL file at `doc/odml_terminology/`.
- Added the `tools.ODMLWriter` and `tools.ODMLReader` classes which serve as an easy 
    entry point to saving and loading for all the supported file formats `XML`, `YAML`, 
    `JSON` and `RDF`.
- Added the `tools.DictWriter` and `tools.DictReader` classes which convert Python 
    dictionary data to odML data and vice versa, which in turn is required for both YAML 
    and JSON format loading and saving.
- Removed the `tools.jsonparser` file which is no longer required due to the classes in 
    `tools.odmlparser` and `tools.dict_parser`. 
- Added the `tools.FormatConverter` class which enables batch conversion of one odML 
    format into another.
- Added the `tools.VersionConverter` class which enables conversion of pre-v1.4 odML files 
    into valid v1.4 odML.
  - The `VersionConverter` converts `XML`, `JSON` and `YAML` based odML files of odML file 
        version 1.0 to odML file version 1.1.
  - Only attributes supported by `Document`, `Section` and `Property` are exported. Any 
        non supported attribute will produce a warning message, the content will be 
        discarded.
  - The value content is moved from a `Value` object to its parent `Property` value list.
  - The first encountered `unit` or `uncertainty` of values of a `Property` will be moved 
        to its parent `Property`. Any differing subsequent `unit` or `uncertainty` of 
        values of the same `Property` will produce a warning message, the content will be 
        discarded.
  - The first `filename` attribute content of a `Value` is moved to the `value_origin` 
        attribute of its parent `Property`.
  - Any g-node terminology URL in `repository` or `link` is updated from v1.0 to their 
        v1.1 counterparts if available. 
  - A `VersionConverter` object provides a `.conversion_log` list attribute to access all 
        info and warning messages after a conversion has taken place. See #234.

## Fixes
- Various installation issues have been resolved for Linux and MacOS.
- `False` as well as `F` are now properly converted to bool values in both 
    Python 2 and 3. See #222.
- Fixes saving datetime related values to JSON. See #248.
- odML style custom tuples can now properly be saved using the `XMLParser`.
- `Document` now properly uses the dtypes date setter on init. See #249.
- Fixes load errors on Empty and `None` boolean and datetime related values. See #245.
- Excludes `id` when comparing odML entities for equality. See #260.
- When a `Property` is cloned, the parent of the clone is now properly set to `None`.
- Avoids an `AttributeError` on `get_path()` when a `Property` has no parent. See #256.
- Avoids an `AttributeError` on `get_merged_equivalent()` when a `Property` 
    has no parent. See #257.
- Avoids an error on `Property.append()`, if the dtype was not set. See #266.
- Makes sure that `Property.append()` exits on empty values but accepts `0` and `False`.
- Sets `Property.uncertainty` to `None` if an empty string is passed to it.
- Changes the `Property.__init__` set attributes order: In the previous set attribute 
    order, the repository attribute was overwritten with `None` by the `super.__init__` 
    after it had been set.
- Fixes set `Property.parent = None` bugs in `remove()` and `insert()` methods.
- Consistently use relative imports to address circular imports and remove code that 
    circumvents previous circular import errors in the `ODMLParser` class. See #199.
- Consistently uses `BaseSection` or `BaseDocument` for isinstance checks throughout 
    `base` instead of a mixture of `BaseSection` and `Section`.


# Version 1.3.4

## Fixes
- Potential installation issues due to import from `info.py`.


# Version 1.3.3
## Features

- Terminology caching and loading update.
- Terminology section access and type listing functions.
- Define and use common format version number for all parsers.
- Supported format version check: When trying to open a file with any of the odml parsers, 
    first the document format version number is checked. If the found version number does 
    not match the supported one, file loading will fail an exception, since this is the 
    oldest format version. If anyone tries to open a newer format, they should first 
    update their odML package and not use this one.
- Document saving: An odML document can now only be saved, if the validation does not show 
    any errors. Saving an invalid document will exit while printing all encountered 
    errors.
- Parser: All parsers are now more relaxed when encountering unsupported tags or missing 
    tags and only print warnings instead of ending with an exception. Warnings are 
    collected and can be accessed via the parser object (required for display in 
    [odml-ui](https://github.com/G-Node/odml-ui) to avoid potential loss of information).
- Package and format information added or updated: `Version`, `Format version`, `Contact`, 
    `Homepage`, `Author`, PyPI `Classifiers`, `Copyright`.
- Removes the license text from `setup.py`. The license text interfered with the PyPI 
    process in a way, that the description was not displayed on PyPI.
- Removes the image folder from the project, since they are exclusively used in the 
    outsourced [odml-ui](https://github.com/G-Node/odml-ui) project.

## Fixes
- Fixes a bug that prohibits the parsing of `json` or `yaml` files; #191.
- Fixes a bug that fails parsing of `json` or `yaml` files when `Section.repository`, `Section.link` or `Section.include` are present; #194.


# Version 1.3.2
- Expose load, save, and display functions to top level module
    - These functions accept a `backend` argument that specifies the parser or writer. 
        Can be one of `XML`, `JSON`, or `YAML`.


# Version 1.3.1
- move ui to a separate repository https://github.com/g-node/odml-ui
- python3 compatibility
- add json and yaml storage backends
