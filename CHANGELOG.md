# Changelog

Used to document all changes from previous releases and collect changes 
until the next release.

# Version 1.5.1

# RDF Subclassing feature
RDF subclasses are now properly added by default to any written RDF document. The RDF document will now also include RDF Subclass definitions in addition to the actual data to enable Subclass specific queries. See PR #400 and issue #397 for details.

# Minor changes and updates
- Section properties can now be reordered. See PR #398 for details.
- Property values can now be inserted at a specified index. See PR #398 for details.
- Tuples can now be assigned using a list instead of the `"(x;x;...)"` syntax as well. See PR #393 and issue #392 for details.

# Version 1.5.0

# Python 2 deprecation warning
A Python 2 deprecation warning for August 2020 has been added. See issue #387 for details.

# Validation feature update
See issues #377, #378 and #379 as well as Pull Request #389 for details.

An `IssueID` enum class as been added to provide identifiers to individual ValidationErrors. The `Validation` class itself has been refactored to provide the option to create standalone Validation instances with a different set of registered validations than the default library validation.
The `Validation` class now features the new `register_custom_handler`, `run_validation`and `report` methods to add custom validation handlers to an instance, re-run the validations of an existing Instance and provide a brief report of encountered errors and warnings. The general `ValidationError.__repr__` string has been shortened to make the individual ValidationErrors more convenient to print and read. The default Validation is always run when a Document is saved or loaded via the `ODMLParser` and the `Validation.report` method is used to provide a `warnings.warn` message of the following format:
```
UserWarning: The saved Document contains formal issues. Run 'odml.validation.Validation(doc)' to resolve them.
Validation found 0 errors and 3 warnings in 1 Sections and 1 Properties.
```

Further changes to the Validation class and behavior include:
- an odml `Document` now provides a `validate` method that will run a default Validation and return the Validation instance to provide users with access to encountered issues.
- a `validation_id` field has been added to the `ValidationError` class.
- standalone Sections and Properties can now be validated.
- Sections and Properties are validated on init.
- the `section_repository_present` validation has been removed from the default validation list. Since Sections rarely have repositories set, this validation can lead to spam when validating a Document.

# Cardinality feature
Property and Section now provide a cardinality feature. Users can now define a range how many Values a Property and how many Properties or Sections a Section should have. A cardinality can be set and read via its accessor method and can be set via an additional convenience method. Whenever a cardinality or an affected Value, Section or Property is set, a corresponding validation is triggered. If this a set cardinality for a Property or Section is violated, a message is printed to the command line directly and a warning is issued when a Document is saved or loaded. Every cardinality is saved to and loaded from all available file formats.
The full functionality of all cardinality features are documented in the tutorial and is available via readthedocs. For additional details see pull requests #374, #382, #383, #384 and issue #361. 

# Update in Section type default behavior
With recent updates the library now respects and enforces `Section.type` as a required attribute and allows save only with documents where this requirement is satisfied.
To allow backwards file compatibility and ease usage, `Section.type` is by default set to the string `n.s.` (not specified), which means files where no `Section.type` had been specified can be loaded and saved, but will contain `n.s.` as value for every `Sections.type` that was previously not specified.
Further the validation run before a document can be saved will issue a warning, if a `Section.type` with value `n.s.` is encountered and will still refuse to save with an error, if an empty `Section.type` is encountered. See PR #376 for details.

# DictParser and ODMLParser fully support ignore errors
- the `DictParser.DictReader` is now able to ignore errors, collect warnings and print corresponding notifications and works now analogous to the `xmlparser.XMLReader` behaviour. See issue #367 for details.
- the `ODMLParser.ODMLReader` for JSON and YAML now uses `ignore_errors` by default e.g. when using the `odml.load` function for JSON and YAML odml files.

# Fixes
- fixes an exception when trying to append or extend a `Property` with dtype `tuple`. See issue #364 for details.
- when trying to set the `name` attribute to `None`, it now silently sets the name to `id` instead, since `name` must not be empty. It would be set to `id` on load and can cause `AttributeError` exceptions with some methods if its not set.
- a bug was fixed in `format.revmap` where the reverse mapping of an odml attribute would always return the case that the attribute is part of the format, even if it was not.

# Minor changes and updates
- all deprecation warnings now use the warnings module.
- the `Property.value` attribute deprecation warnings have been unified. See issue #360 for details.
- the `base.Sectionable.create_section` method has been updated to conform with `Section.__init__`. See issue #368 for details.
- all saved XML odML files now use the same XML header. See issue #339 for details.
- a function to manually refresh the terminology cache has been added. See issue #202 for details.
- a Validation to note non-human readable `Property` and `Section` names has been added. See issue #365 for details.
- getter and setter methods are added to the `odml.Document.origin_file_name` attribute. See issue #358 for details.
- the Exception type in `odml.tools.converters.VersionConverter` is changed to `odml.tools.parser_utils.ParserException`. See issue #359 for details.
- the `odml.Property.export_leaf` method now also includes sibling Properties on export.
- the `rdf_converter` has been cleaned up, see issues #211 and #345 for details.
- the test for the `Section`/`Property` order in documents obtained via the `RDFReader` has been expanded. See issue #265 for details.
- tests for Validation errors on `Section` or `Property` init have been added. See issue #369 for details.
- tests writing temporary files now properly clean up after themselves. See issue #381 for details.
- tests now use a common temporary directory to write files and use a constant for accessing the test/resources directory.
- the link to the odML tutorial in the README file now points to python-odml.readthedocs.org; the README file now also includes links to Travis and Coveralls.
- the tutorial now includes descriptions of the `pprint` method and a link to the odML templates hosting site. Further the tutorial has been updated to include descriptions of the cardinality feature and Validation usage. 
- introduces major PEP8 fixes to basically all files of the library. See Pull Request #385 for details.
- the class reference now includes the Template, Terminology and Validation classes.

# Version 1.4.5

## Minor changes, updates and fixes.
- all usages of the unsafe `yaml.load` calls are replaced with `yaml.save_load`. This also prepares for Python 3.9 compatibility. See also issue #350 and pull request #356 for details.
- dtype tests now use both `assertRegexpMatches` and `assertRegex` depending on the Python version used to prepare for Python 3.9 compatibility while still keeping the Python 2 tests running.
- odml style tuple handling is refactored. Now lists of odml style tuples are properly saved to file and can be loaded again. If an invalid format is used to add an odml style tuple, more detailed exception messages are available. Also adds more odml style tuples tests. See issues #250, #353 and #354 for details.
- a deprecation warning is displayed when importing the odml module if a Python version <3.6 is used.
- introduces minor PEP8 fixes to all files and completes docstrings for full documentation.

# Version 1.4.4

## Introduction of inline style sheet

The `XMLWriter` can now be used to save an XML odML document with an inline XSL stylesheet for rendered viewing via a web browser.
The document can be saved with the current default G-Node odML document style or with a custom style. When a document containing such a stylesheet is loaded, the style is lost and needs to be provided again as described above. See issue #331 for details.

## Export leaf feature

Subsets of odML documents can now be exported using the introduced `export_leaf` features for `Section` and `Property`.
When invoked on a `Section` or a `Property`, the method will return all direct ancestor `Sections` including all their direct `Properties` up to the root of the document and return a new, cloned document containing only this particular direct branch. See issue #340 for details.

## Major pyyaml dependency fix

Since issue #291 the odml package had its pyyaml dependency fixed to version `4.2b4`.
This release fixes the original problem with the pyyaml distribution and removes the fix to pyyaml version `4.2b4`.
See issue #343 and pull request #344 for details. 

## odML package structure changes to reduce import cycles

The package structure was changed to reduce the number of import cycles and make various parser classes more easily available via the `__init__` files. See issues #317 and #333 for details.

The changes to the package structure should not affect any of the main parsers and how they were previously imported nor affect any of the command line scripts provided with this package.

The following changes have been introduced to the package structure:
- a new subdirectory `odml.tools.converters` is added.
- `format_converter` and `version_converter` are moved into this directory.
- since [odml-ui](https://github.com/G-Node/odml-ui) depends on the `version_converter`, a dummy file is left at its original location. It imports the `VersionConverter` class from its new location and prints a deprecation warning.
- the dict `RDFConversionFormats` from file `tools.utils` has been moved to `RDF_CONVERSION_FORMATS` in file `tools.parser_utils` and all usages have been switched to the new dict.
- the dict `ConversionFormats` from file `tools.utils` has been moved to the only file its using it, `tools.converters.format_converter`.
- the now unused file `tools.utils` has been removed.
- a new subdirectory `odml.rdf` was added and the files `fuzzy_finder` and `query_creator` were moved into this directory. Both files provide convenience and additional functions for odML specific RDF and are fairly independent from the rest of the library. Conceptually they are best kept separate from other convenience tools and parsers.

## Minor changes, updates and fixes

- The `section_subclasses.yaml` file is moved from the `doc` folder to the new `odml/resources` folder. This allows usage of the file with all install options. See issue #212 for details.
- The RDF subclasses now also support DataCite Section types.
- The `rdf_converter` now features a new `load_rdf_subclasses` function, that either provides the content of the `resources/subclasses.yml` file or, if it cannot be accessed, deals with it without breaking the `RDFWriter`.
- Fixes calling the deprecated `odml.Property.value` attribute in the `rdf_converter`.
- The `RDFWriter` will now call every odml documents `finalize` method to ensure that all `links` and `includes` are resolved before exporting to RDF.
- The OWL odml ontology file is moved from `doc/root-ontology.ttl` to `odml/resources/odml-ontology.ttl` and included in `Manifest.in`.
- The RDF namespace is changed from https://g-node.org/projects/odml-rdf# to https://g-node.org/odml-rdf#. This step is taken since the odml-rdf ontology OWL file will be available under this URL. This change includes changes in all code and documentation occurrences in the project.
- Typos and minor inconsistencies where fixed in the odml - RDF subclasses mapping file `resources/section_subclasses.yaml`.
- The OWL odml ontology file `resources/odml-ontology.ttl` has been restructured:
  - all available subclasses where moved to their own file section.
  - all subclasses that are created via the `resources/section_subclasses.yaml` file have been added to the ontology file as well.
- Value errors concerning `date`, `time` and `datetime` now contain a message providing the required format. See issue #341 for details.

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
