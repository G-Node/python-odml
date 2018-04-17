# odml data model

Data exchange requires that also annoations, metadata, are
exchanged. In oder to allow interoperability we need both a common
(meta) data model, the format in which the metadata are exchanged, and
a common terminology.

Here we briefly describe the data model of the odML. It is based on
the idea of key-value pairs like temperature = 26°C.

We tried to keep the model as simple as possible while being flexible,
allowing interoperability, and being customizable. The model defines
four entities (Property, Section, Value, RootSection) who's relations
and elements are shown in the figure below.

![odml_logo](./images/erModel..png "odml data model")

Property and Section entities are the core of the odml. A Section
contains Properties and can further have subsection thus building a
tree-like structure. The model further does not control the content
which is a risk, on the one hand, but offers the flexibility we
consider essential.
