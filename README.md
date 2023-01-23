# SPARQLUnicorn Ontology Documentation
This repository hosts a standalone version of the HTML documentation feature included in the SPARQLing Unicorn QGIS Plugin.

Rather than initiating the documentation generation within the SPARQLing Unicorn QGIS Plugin, this python script allows the generation of the documentation standalone or as a Github Action.

The standalone script does not rely on QGIS classes and does not provide the full functionality available in the SPARQLUnicorn QGIS Plugin.

Deviations from the SPARQLing Unicorn Plugin are listed as follows:

* Support for less geometry literals: Only WKT and GeoJSON literals are supported for rendering
