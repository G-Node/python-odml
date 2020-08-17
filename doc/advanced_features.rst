======================
Advanced odML features
======================

Working with odML Validations
=============================

odML Validations are a set of pre-defined checks that are run against an odML document automatically when it is saved or loaded. A document cannot be saved, if a Validation fails a check that is classified as an Error. Most validation checks are Warnings that are supposed to raise the overall data quality of the odml Document.

When an odML document is saved or loaded, tha automatic validation will print a short report of encountered Validation Warnings and it is up to the user whether they want to resolve the Warnings. The odML document provides the ``validate`` method to gain easy access to the default validations. A Validation in turn provides not only a specific description of all encountered warnings or errors within an odML document, but it also provides direct access to each and every odML entity i.e. an ``odml.Section`` or an ``odml.Property`` where an issue has been found. This enables the user to quickly access and fix an encountered issue.

A minimal example shows how a workflow using default validations might look like:

    >>> # Create a minimal document with Section issues: name and type are not assigned
    >>> doc = odml.Document()
    >>> sec = odml.Section(parent=doc)
    >>> odml.save(doc, "validation_example.odml.xml")

This minimal example document will be saved, but will also print the following Validation report:

    >>> UserWarning: The saved Document contains unresolved issues. Run the Documents 'validate' method to access them.
    >>> Validation found 0 errors and 2 warnings in 1 Sections and 0 Properties.

To fix the encountered warnings, users can access the validation via the documents' ``validate`` method:

    >>> validation = doc.validate()
    >>> for issue in validation.errors:
    >>>     print(issue)

This will show that the validation has encountered two Warnings and also displays the offending odml entity.

    >>> ValidationWarning: Section[73f29acd-16ae-47af-afc7-371d57898e28] 'Section type not specified'
    >>> ValidationWarning: Section[73f29acd-16ae-47af-afc7-371d57898e28] 'Name not assigned'

To fix the "Name not assigned" warning the Section can be accessed via the validation entry and used to directly assign a human readable name to the Section in the original document. Re-running the validation will show, that the warning has been removed.

    >>> validation.errors[1].obj.name = "validation_example_section"
    >>> # Check that the section name has been changed in the document
    >>> print(doc.sections)
    >>> # Re-running validation
    >>> validation = doc.validate()
    >>> for issue in validation.errors:
    >>>     print(issue)

Similarly the second validation warning can be resolved before saving the document again.

Please note that the automatic validation is run whenever a document is saved or loaded using the ``odml.save`` and ``odml.load`` functions as well as the ``ODMLWriter`` or the ``ODMLReader`` class. The validation is not run when using any of the lower level ``xmlparser``, ``dict_parser`` or ``rdf_converter`` classes.

List of available default validations
-------------------------------------

The following contains a list of the default odml validations, their message and the suggested course of action to resolve the issue.

| Validation: ``object_required_attributes``
| Message: "Missing required attribute 'xyz'"
| Applies to: ``Document``, ``Section``, ``Property``
| Course of action: Add an appropriate value to attribute 'xyz' for the reported odml entity.

| Validation: ``section_type_must_be_defined``
| Message: "Section type not specified"
| Applies to: ``Section``
| Course of action: Fill in the ``type`` attribute of the reported Section.

| Validation: ``section_unique_ids``
| Message: "Duplicate id in Section 'secA' and 'secB'"
| Applies to: ``Section``
| Course of action: IDs have to be unique and a duplicate id was found. Assign a new id for the reported Section.

| Validation: ``property_unique_ids``
| Message: "Duplicate id in Property 'propA' and 'propB'"
| Applies to: ``Property``
| Course of action: IDs have to be unique and a duplicate id was found. Assign a new id for the reported Property

| Validation: ``section_unique_name_type``
| Message: "name/type combination must be unique"
| Applies to: ``Section``
| Course of action: The combination of Section.name and Section.type has to be unique on the same level. Change either name or type of the reported Section.

| Validation: ``object_unique_name``
| Message: "Object names must be unique"
| Applies to: ``Document``, ``Section``, ``Property``
| Course of action: Property name has to be unique on the same level. Change the name of the reported Property.

| Validation: ``object_name_readable``
| Message: "Name not assigned"
| Applies to: ``Section``, ``Property``
| Course of action: When Section or Property names are left empty on creation or set to None, they are automatically assigned the entities uuid. Assign a human readable name to the reported entity.

| Validation: ``property_terminology_check``
| Message: "Property 'prop' not found in terminology"
| Applies to: ``Property``
| Course of action: The reported entity is linked to a repository but the repository is not available. Check if the linked content has moved.

| Validation: ``property_dependency_check``
| Message: "Property refers to a non-existent dependency object" or "Dependency-value is not equal to value of the property's dependency"
| Applies to: ``Property``
| Course of action: The reported entity depends on another Property, but this dependency has not been satisfied. Check the referenced Property and its value to resolve the issue.

| Validation: ``property_values_check``
| Message: "Tuple of length 'x' not consistent with dtype 'dtype'!" or "Property values not of consistent dtype!".
| Applies to: ``Property``
| Course of action: Adjust the values or the dtype of the referenced Propery.

| Validation: ``property_values_string_check``
| Message: "Dtype of property "prop" currently is "string", but might fit dtype "dtype"!"
| Applies to: ``Property``
| Course of action: Check if the datatype of the referenced Property.values has been loaded correctly and change the Property.dtype if required.

| Validation: ``section_properties_cardinality``
| Message: "cardinality violated x values, y found)"
| Applies to: ``Section``
| Course of action: A cardinality defined for the number of Properties of a Section does not match. Add or remove Properties until the cardinality has been satisfied or adjust the cardinality.

| Validation: ``section_sections_cardinality``
| Message: "cardinality violated x values, y found)"
| Applies to: ``Section``
| Course of action: A cardinality defined for the number of Sections of a Section does not match. Add or remove Sections until the cardinality has been satisfied or adjust the cardinality.

| Validation: ``property_values_cardinality``
| Message: "cardinality violated x values, y found)"
| Applies to: ``Property``
| Course of action: A cardinality defined for the number of Values of a Property does not match. Add or remove Values until the cardinality has been satisfied or adjust the cardinality.

| Validation: ``section_repository_present``
| Message: "A section should have an associated repository" or "Could not load terminology" or "Section type not found in terminology"
| Applies to: ``Section``
| Course of action: Optional validation. Will report any section that does not specify a repository. Add a repository to the reported Section to resolve.

Custom validations
------------------

Users can write their own validation and register them either with the default validation or add it to their own validation class instance.

A custom validation handler needs to ``yield`` a ``ValidationError``. See the ``validation.ValidationError`` class for details.

Custom validation handlers can be registered to be applied on "odML" (the odml Document), "section" or "property".

    >>> import odml
    >>> import odml.validation as oval
    >>>
    >>> # Create an example document
    >>> doc = odml.Document()
    >>> sec_valid = odml.Section(name="Recording-20200505", parent=doc)
    >>> sec_invalid = odml.Section(name="Movie-20200505", parent=doc)
    >>> subsec = odml.Section(name="Sub-Movie-20200505", parent=sec_valid)
    >>>
    >>> # Define a validation handler that yields a ValidationError if a section name does not start with 'Recording-'
    >>> def custom_validation_handler(obj):
    >>>     validation_id = oval.IssueID.custom_validation
    >>>     msg = "Section name does not start with 'Recording-'"
    >>>     if not obj.name.startswith("Recording-"):
    >>>         yield oval.ValidationError(obj, msg, oval.LABEL_ERROR, validation_id)
    >>>
    >>> # Create a custom, empty validation with an odML document 'doc'
    >>> custom_validation = oval.Validation(doc, reset=True)
    >>> # Register a custom validation handler that should be applied on all Sections of a Document
    >>> custom_validation.register_custom_handler("section", custom_validation_handler)
    >>> # Run the custom validation and return a report
    >>> custom_validation.report()
    >>> # Display the errors reported by the validation
    >>> print(custom_validation.errors)

Defining and working with feature cardinality
=============================================

The odML format allows users to define a cardinality for
the number of subsections and properties of Sections and
the number of values a Property might have.

A cardinality is checked when it is set, when its target is
set and when a document is saved or loaded. If a specific
cardinality is violated, a corresponding warning will be printed.

Setting a cardinality
---------------------

A cardinality can be set for sections or properties of sections
or for values of properties. By default every cardinality is None,
but it can be set to a defined minimal and/or a maximal number of
an element.

A cardinality is set via its convenience method:

    >>> # Set the cardinality of the properties of a Section 'sec' to
    >>> # a maximum of 5 elements.
    >>> sec = odml.Section(name="cardinality", type="test")
    >>> sec.set_properties_cardinality(max_val=5)

    >>> # Set the cardinality of the subsections of Section 'sec' to
    >>> # a minimum of one and a maximum of 2 elements.
    >>> sec.set_sections_cardinality(min_val=1, max_val=2)

    >>> # Set the cardinality of the values of a Property 'prop' to
    >>> # a minimum of 1 element.
    >>> prop = odml.Property(name="cardinality")
    >>> prop.set_values_cardinality(min_val=1)

    >>> # Re-set the cardinality of the values of a Property 'prop' to not set.
    >>> prop.set_values_cardinality()
    >>> # or
    >>> prop.val_cardinality = None

Please note that a set cardinality is not enforced. Users can set less or more entities than are specified allowed via a cardinality. Instead whenever a cardinality is not met, a warning message is displayed and any unment cardinality will show up as a Validation warning message whenever a document is saved or loaded.

View odML documents in a web browser
====================================

By default all odML files are saved in the XML format without the capability to view
the plain files in a browser. By default you can use the command line tool ``odmlview``
to view saved odML files locally. Since this requires the start of a local server,
there is another option to view odML XML files in a web browser.

You can use an additional feature of the ``odml.tools.XMLWriter`` to save an odML
document with an embedded default stylesheet for local viewing:

    >>> import odml
    >>> from odml.tools import XMLWriter
    >>> doc = odml.Document() # minimal example document
    >>> filename = "viewable_document.xml"
    >>> XMLWriter(doc).write_file(filename, local_style=True)

Now you can open the resulting file 'viewable_document.xml' in any current web-browser
and it will render the content of the odML file.

If you want to use a custom style sheet to render an odML document instead of the default
one, you can provide it as a string to the XML writer. Please note, that it cannot be a
full XSL stylesheet, the outermost tag of the XSL code has to be
``<xsl:template match="odML"> [your custom style here] </xsl:template>``:

    >>> import odml
    >>> from odml.tools import XMLWriter
    >>> doc = odml.Document() # minimal example document
    >>> filename = "viewable_document.xml"
    >>> own_template = """<xsl:template match="odML"> [your custom style here] </xsl:template>"""
    >>> XMLWriter(doc).write_file(filename, custom_template=own_template)

Please note that if the file is saved using the '.odml' extension and you are using
Chrome, you will need to map the '.odml' extension to the browsers Mime-type database as
'application/xml'.

Also note that any style that is saved with an odML document will be lost, when this
document is loaded again and changes to the content are added. In this case the required
style needs to be specified again when saving the changed file as described above.
