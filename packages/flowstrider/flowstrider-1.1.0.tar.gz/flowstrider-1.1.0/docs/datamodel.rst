=================
Data-Flow Diagram
=================

FlowStrider takes a **Data-Flow Diagram (DFD)** of the software system under analysis as input.
The DFD representation in FlowStrider follows the STRIDE threat modeling framework, originally developed by Microsoft.


What is a Data-Flow Diagram?
----------------------------

A DFD provides a high-level view of how data moves through a system:

- where it is processed,
- where it is stored,
- and where it enters or leaves the system.

A DFD typically consists of five main elements:


.. image:: images/dfd_elements.png
   :alt: DFD elements visualization
   :width: 800px
   :align: center

.. tip::
   For a step-by-step tutorial and detailed explanations of each element, see
   `Microsoft Learn – Create a threat model using foundational DFD elements <https://learn.microsoft.com/en-us/training/modules/tm-create-a-threat-model-using-foundational-data-flow-diagram-elements/>`__
   and the `Wikipedia article on Data-flow diagrams <https://en.wikipedia.org/wiki/Data-flow_diagram>`__.

FlowStrider’s Data-Flow Diagram Format
--------------------------------------

General Structure
~~~~~~~~~~~~~~~~~

To be processed by FlowStrider, a DFD must be provided as a json file using FlowStrider’s Data-Flow Diagram format.
This format borrows terminology from graph theory:

- **Nodes** represent processes, data stores, or external entities.
- **Edges** represent data flows (connections) between nodes.
- **Clusters** group nodes together, typically to define trust boundaries.

The mapping to STRIDE’s DFD elements is preserved through **tags** on nodes (explained further below).

The core component of this format is the data class ``DataflowDiagram``, which contains the three element types listed above.
The figure below illustrates the format’s overall structure using a simple example, alongside the corresponding DFD visualization.

.. image:: images/dfd_json_structure.png
   :alt: JSON structure
   :width: 450px
   :align: center

Inside the diagram, the objects ``"nodes": {}``, ``"edges": {}``, and ``"clusters": {}`` hold the respective entities.
The array ``tags`` lists the rule sets that FlowStrider should apply when analyzing this diagram.
Detailed field descriptions are provided in the tables further below.


Representing DFD Elements
~~~~~~~~~~~~~~~~~~~~~~~~~

Each of the main DFD elements can be represented in the format as shown below:

.. image:: images/dfd_json_mapping.png
   :alt: DFD element visualization and json structure
   :width: 800px
   :align: center

Note: When creating nodes, edges, or clusters, always assign the correct **element type** as a tag.

Adding Metadata to Elements
~~~~~~~~~~~~~~~~~~~~~~~~~~~

All three element types (nodes, edges, and clusters) include a generic
``attributes`` dictionary for additional metadata.
The next figure shows examples of each element with possible values.

.. image:: images/dfd_json_attributes.png
   :alt: DFD elements with context information
   :width: 800px
   :align: center

The supported metadata values are described in **Supported metadata** table below.

Custom Prioritization
~~~~~~~~~~~~~~~~~~~~~

Both **nodes** and **clusters** can include an additional field called ``severity_multiplier``.
This field takes a float number used to customize prioritization:

- Default: if not set, the multiplier is ``1.0``.
- Use higher values to increase the priority of specific elements (e.g., critical assets or highly exposed components).

The prioritization influences the **sorting of findings in the final report**.

Examples
~~~~~~~~

- The complete json example can be found in ``test/resources/example_readme.json``.
- Additional examples are available in the same folder.

.. tip::
   For more background on the underlying json format itself, see
   `Wikipedia – JSON <https://en.wikipedia.org/wiki/JSON>`__ or
   `MDN – Working with JSON <https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/JSON>`__.

Detailed Field Reference
------------------------

The following section provides a complete list of all fields in the relevant data classes, along with their descriptions.

Data-flow diagram
~~~~~~~~~~~~~~~~~

.. include:: _generated/dfd_class_table.rst

Node
~~~~

.. include:: _generated/node_class_table.rst

Edge
~~~~

.. include:: _generated/edge_class_table.rst

Cluster
~~~~~~~

.. include:: _generated/cluster_class_table.rst

Supported Metadata
~~~~~~~~~~~~~~~~~~

.. include:: _generated/attributes_dict_table.rst
