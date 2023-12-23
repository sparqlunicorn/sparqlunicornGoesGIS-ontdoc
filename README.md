# SPARQL Unicorn Ontology Documentation
This repository hosts a standalone version of the HTML documentation feature included in the SPARQLing Unicorn QGIS Plugin.

Rather than initiating the documentation generation within the SPARQLing Unicorn QGIS Plugin, this python script allows the generation of the documentation standalone or as a Github Action.

The standalone script does not rely on QGIS classes and does not provide the full functionality available in the SPARQLUnicorn QGIS Plugin.

Deviations from the SPARQLing Unicorn Plugin are listed as follows:

* Support for less geometry literals: Only WKT and GeoJSON literals are supported for rendering

### Usage Example as Github Action

For a usage example please refer to this repository:
https://github.com/sparqlunicorn/sparqlunicornGoesGIS_testdata

### Usage Example as Gitlab CI Workflow

For a usage example please refer to this repository:
[https://gitlab.com/sparqlunicorn/sparqlunicornGoesGIS_testdata](https://gitlab.com/sparqlunicorn/sparqlunicornGoesGIS_testdata)

### Installation as PIP package

You can install the ontology documentation script as a pip package using the following command:

`
pip install -U git+https://github.com/sparqlunicorn/sparqlunicornGoesGIS-ontdoc@v017dev
`

The execution parameters are the ones described in the next section.

### Usage as standalone script

You can use the standalone script by downloading a release or cloning this repository.

Before using the script, please ensure you have installed the requirements listed in the file requirements.txt.

```
pip install -r requirements.txt
```

The command docgeneration.py -h will print a help dialog with all available parameters and options.

At the minimum, this script expects an input RDF file and an output file path.

```
usage: docgeneration.py [-h] -i [INPUT ...] -o [OUTPUT ...] [-pxns PREFIXNS] [-px PREFIXNSSHORT]
                        [-ip CREATEINDEXPAGES] [-cc CREATECOLLECTIONS] [-ll LABELLANG] [-li LICENSE] -ex EXPORTS
                        [EXPORTS ...] [-lgu LOGOURL] [-dt DATASETTITLE] [-lo LOCALOPTIMIZED] [-mdt METADATATABLE]
                        [-nnsp NONNSPAGES] [-vowl CREATEVOWL] [-of OFFLINECOMPAT] [-ogc OGCAPIFEATURES]
                        [-iiif IIIFMANIFEST] [-sc STARTCONCEPT] [-dp DEPLOYPATH] [-tp TEMPLATEPATH] [-tn TEMPLATENAME]

optional arguments:
  -h, --help            show this help message and exit
  -i [INPUT ...], --input [INPUT ...]
                        the input TTL file(s) to parse
  -o [OUTPUT ...], --output [OUTPUT ...]
                        the output path(s)
  -pxns PREFIXNS, --prefixns PREFIXNS
                        the prefixnamespace
  -px PREFIXNSSHORT, --prefixnsshort PREFIXNSSHORT
                        the prefix
  -ip CREATEINDEXPAGES, --createIndexPages CREATEINDEXPAGES
                        create index pages?
  -cc CREATECOLLECTIONS, --createCollections CREATECOLLECTIONS
                        create collections?
  -ll LABELLANG, --labellang LABELLANG
                        preferred label language (default: en)
  -li LICENSE, --license LICENSE
                        license under which this data is published
  -ex EXPORTS [EXPORTS ...], --exports EXPORTS [EXPORTS ...]
                        choose script exports to be generated next to HTML ['graphml', 'json', 'tgf', 'ttl']
  -lgu LOGOURL, --logourl LOGOURL
                        URL of an optional page logo
  -dt DATASETTITLE, --datasettitle DATASETTITLE
                        The title of this dataset to use in HTML templates
  -lo LOCALOPTIMIZED, --localOptimized LOCALOPTIMIZED
                        build a version for local deployment
  -mdt METADATATABLE, --metadatatable METADATATABLE
                        create metadata table?
  -nnsp NONNSPAGES, --nonnspages NONNSPAGES
                        create nonns pages?
  -vowl CREATEVOWL, --createvowl CREATEVOWL
                        create vowl graph view?
  -of OFFLINECOMPAT, --offlinecompat OFFLINECOMPAT
                        built-result is offline compatible
  -ogc OGCAPIFEATURES, --ogcapifeatures OGCAPIFEATURES
                        create ogc api features collections?
  -iiif IIIFMANIFEST, --iiifmanifest IIIFMANIFEST
                        create iiif manifests?
  -sc STARTCONCEPT, --startconcept STARTCONCEPT
                        the concept suggested for browsing the HTML documentation
  -dp DEPLOYPATH, --deploypath DEPLOYPATH
                        the deploypath where the documentation will be hosted
  -tp TEMPLATEPATH, --templatepath TEMPLATEPATH
                        the path of the HTML template
  -tn TEMPLATENAME, --templatename TEMPLATENAME
                        the name of the HTML template
```

### Supported vocabularies

The following vocabularies are supported by the ontology documentation tool and may be rendered in a specific way in HTML:
 
* [BIBO Vocabulary](http://purl.org/ontology/bibo/)
* [Dublin Core DCTerms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/)
* [FOAF Vocabulary](http://xmlns.com/foaf/0.1/)
* [GeoSPARQL 1.0 and 1.1 vocabulary](https://github.com/opengeospatial/ogc-geosparql)
* [SKOS Vocabulary](https://www.w3.org/TR/swbp-skos-core-spec/)
* [SOSA Ontology](https://www.w3.org/TR/vocab-ssn/)
* [Unit of Measurements Ontology](https://github.com/HajoRijgersberg/OM)
* [W3C Web Annotation Data Model](https://www.w3.org/TR/annotation-model/)
* [W3C Geo Vocabulary](https://www.w3.org/2003/01/geo/)
