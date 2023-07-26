# SPARQLUnicorn Ontology Documentation
This repository hosts a standalone version of the HTML documentation feature included in the SPARQLing Unicorn QGIS Plugin.

Rather than initiating the documentation generation within the SPARQLing Unicorn QGIS Plugin, this python script allows the generation of the documentation standalone or as a Github Action.

The standalone script does not rely on QGIS classes and does not provide the full functionality available in the SPARQLUnicorn QGIS Plugin.

Deviations from the SPARQLing Unicorn Plugin are listed as follows:

* Support for less geometry literals: Only WKT and GeoJSON literals are supported for rendering

### Usage Example as Github Action

For a usage example please refer to this repository:
https://github.com/sparqlunicorn/sparqlunicornGoesGIS_testdata

### Usage as standalone script

Before using the script, please ensure you have installed the requirements listed in the file requirements.txt.

The command docgeneration.py -h will print you a help dialog with all available parameters and options.

### Supported vocabularies

The following vocabularies are supported by the ontology documentation tool and may be rendered in a specific way in HTML:
 
* [BIBO Vocabulary](http://purl.org/ontology/bibo/)
* [Dublin Core DCTerms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/)
* [FOAF Vocabulary](http://xmlns.com/foaf/0.1/)
* [GeoSPARQL 1.0 and 1.1 vocabulary](https://github.com/opengeospatial/ogc-geosparql)
* [SKOS Vocabulary](https://www.w3.org/TR/swbp-skos-core-spec/)
* [Unit of Measurements Ontology](https://github.com/HajoRijgersberg/OM)
* [W3C Web Annotation Data Model](https://www.w3.org/TR/annotation-model/)
* [W3C Geo Vocabulary](https://www.w3.org/2003/01/geo/)
