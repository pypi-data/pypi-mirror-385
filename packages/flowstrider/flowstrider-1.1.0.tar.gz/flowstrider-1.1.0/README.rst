===========
FlowStrider
===========

.. image:: https://gitlab.com/dlr-dw/automated-threat-modeling/flowstrider/badges/main/pipeline.svg
  :target: https://gitlab.com/dlr-dw/automated-threat-modeling/flowstrider/-/pipelines
  :alt: Pipeline status

.. image:: https://gitlab.com/dlr-dw/automated-threat-modeling/flowstrider/badges/main/coverage.svg
  :target: https://gitlab.com/dlr-dw/automated-threat-modeling/flowstrider/-/commits/main
  :alt: Test coverage

.. image:: https://gitlab.com/dlr-dw/automated-threat-modeling/flowstrider/-/badges/release.svg
  :target: https://gitlab.com/dlr-dw/automated-threat-modeling/flowstrider/-/releases/
  :alt: Latest release

.. image:: https://img.shields.io/badge/License-BSD_3-blue.svg?style=flat&labelColor=grey&logoColor=white
  :target: https://opensource.org/licenses/bsd-3-clause
  :alt: License

.. image:: https://img.shields.io/badge/security-bandit-yellow.svg
    :target: https://github.com/PyCQA/bandit
    :alt: Security Status


FlowStrider is an architectural threat modeling tool designed to support the identification, mitigation, documentation, and management of threats in a given software system.

**Why use FlowStrider?**

* Enables **continuous threat modeling**
* **Automates** key parts of the threat modeling process
* Follows a **practice-oriented workflow** inspired by real-world use cases
* Easily integrates into **CI/CD pipelines**
* Programming-language agnostic
* Fully **scriptable and extensible**

Features
========

🛠  **Refine System Representation:** Assists in adding relevant metadata to the system representation to enhance the quality of threat modeling.


🛡 **Identification of Threats:** Uses three built-in rule sets to identify threats based on the system representation.


📊 **Reporting:** Supports the documentation and management of identified threats in a structured report.


Documentation
=============

For the full documentation of the FlowStrider tool, please visit the `GitLab page <https://flowstrider-defe6e.gitlab.io/>`_ or build the documentation locally (using ``tox -e docs``).


Installation
============

As a prerequisite, FlowStrider requires Python (tested with versions 3.10 and 3.12) and Graphviz, which can be installed via ``apt install graphviz`` or as described on their `website <https://graphviz.org/>`_.

Install the tool directly using ``pip install flowstrider`` or clone this repository and install it (using ``git clone`` and ``pip install``).
Dependencies are handled automatically during the installation process as defined in `setup.cfg`.

.. _readme-usage:

Usage
=====

1. **Threat elicitation**

  FlowStrider takes as input a data-flow diagram (DFD) expressed as a json file that follows FlowStrider’s DFD format (example below).
  This data-flow diagram is then used to model potential threats.

  .. code-block:: python

      flowstrider elicit dataflow_diagram.json [--output-path *output-file-path*]
                                               [--management-path *management-file-path*]
                                               [--fail-on-threat (off|undecided|todo|all)]
                                               [--out-lang (en|de)]

  The results can be saved as a PDF file if the ``[--output-path]`` is set. The PDF
  includes a visual representation of the system generated with GraphViz and the details
  about the modeled threats also seen in the console.

  The ``[--management-path]`` gives the path to a json file where information about the
  management state of each existing threat can be modified. If the file doesn't exist
  yet, it will be created.

  If ``[--fail-on-threat] (default=off)`` is set to off, the tool will not fail if it
  finds threats. If set to other options, the tool will fail if there is a threat with
  an unsufficient management state to explain its presence with the set fail option.

  By default, each found threat is asigned the management state ``Undecided``. The
  management state can be modified in the management file indicated by the
  ``[--management-path]`` option. There are seven different states each threat can take
  on as seen in the left column in the table below. The table also shows which state
  will fail the tool if run with a specific option for the ``[--fail-on-threat]``
  argument.

  .. list-table::
    :widths: 20 20 20 20 20
    :header-rows: 1

    * -
      - off
      - undecided
      - todo
      - all
    * - Undecided
      - pass
      - **fail**
      - **fail**
      - **fail**
    * - Delegate
      - pass
      - pass
      - **fail**
      - **fail**
    * - Mitigate
      - pass
      - pass
      - **fail**
      - **fail**
    * - Avoid
      - pass
      - pass
      - **fail**
      - **fail**
    * - Accept
      - pass
      - pass
      - pass
      - **fail**
    * - Delegated
      - pass
      - pass
      - pass
      - **fail**
    * - Mitigated
      - pass
      - pass
      - pass
      - **fail**

  The parameter ``[--out-lang] (default=en)`` denotes the output language used for the
  threats and the report.


2. **Missing Metadata overview**

  The tool relies on metadata (stored in the attributes property of the nodes and edges)
  to accurately elicit threats. An .xlsx file can be generated to get an overview of the
  attributes stored in the metadata, as well as any relevant attributes that are
  missing.

  .. code-block:: python

      flowstrider metadata dataflow_diagram.json metadata_overview.xlsx [--out-lang (en|de)]

  The parameter ``[--out-lang] (default=en)`` denotes the output language used for the
  metadata xlsx file.

3. **Updating Metadata using the xlsx overview**

  After filling out the missing metadata in the xlsx file, that file can be used to
  update the existing json file of the data-flow diagram. The modified and added
  attributes are then being updated as metadata to the nodes and edges of the diagram.

  .. code-block:: python

      flowstrider update dataflow_diagram.json metadata_overview.xlsx


.. code-block:: html

    Tip:

    For a more in depth workflow take a look at the section *Detailed Workflow*.


Creating a System Representation
================================

FlowStrider accepts a system representation as a data-flow diagram (DFD) in its json-based FlowStrider DFD format. See the *Data-Flow Diagram* section in the documentation for more information on how do define elements and assign attributes. In the tags of the dfd at
the bottom of the json file, one can define the rule sets the tool is checking against.
See the *Rule Sets* section on the different rule sets.

Here is a minimal example of such a data-flow diagram in .json:

.. code-block:: JSON

  {
    "dfd": {
      "id": "Example",
      "nodes": {
        "node1": {
          "id": "node1",
          "name": "User",
          "tags": [
            "STRIDE:Interactor"
          ],
          "attributes": {}
        },
        "node2": {
          "id": "node2",
          "name": "Application",
          "tags": [
            "STRIDE:Process"
          ],
          "attributes": {}
        }
      },
      "edges": {
        "edge1": {
          "id": "edge1",
          "source_id": "node1",
          "sink_id": "node2",
          "name": "http_request",
          "tags": [
            "STRIDE:Dataflow"
          ],
          "attributes": {}
        }
      },
      "clusters": {
        "cluster1":{
          "id": "cluster1",
          "node_ids": [
            "node2"
          ],
          "name": "Internet",
          "tags": [
            "STRIDE:TrustBoundary"
          ],
          "attributes": {}
        }
      },
      "name": "",
      "tags": [
        "bsi_rules"
      ],
      "attributes": {}
    }
  }

.. _pyscaffold-notes:


Legal
=====

All files in this repository fall under the stated license in *LICENSE.txt*. The full licensing
terms of used dependencies can be found in *LICENSE-3RD-PARTY.txt*

Making Changes & Contributing
=============================

Please make sure to read *CONTRIBUTING.rst* and follow the preparations before making any
changes to the project.

Cite FlowStrider
================

The paper "FlowStrider: Low-friction Continuous Threat Modeling" was accepted at the Tool Track of ASE25.

Funding
=======

This work was done as part of the AVATAR competence cluster, funded by the Federal Ministry of Research, Technology and Space (funding code: 16KISA012).
