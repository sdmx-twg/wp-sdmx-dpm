"""Direction-agnostic mapping rules, one module per spec layer.

Each module implements both directions of one layer of the
``docs/transformation-guidelines`` spec:

* :mod:`glossary`        -- Category/Item <-> Codelist/Code; Property <-> Concept
* :mod:`data_definition` -- Module/Table <-> Dataflow+DSD; Variables <-> Components
* :mod:`constraints`     -- SubCategory <-> ContentConstraint CubeRegion
"""
