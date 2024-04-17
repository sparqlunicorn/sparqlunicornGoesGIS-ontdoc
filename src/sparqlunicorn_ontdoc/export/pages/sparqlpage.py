from doc.docconfig import DocConfig

from doc.docutils import DocUtils


class SPARQLPage():

    def pageWidgetConstraint(self):
        print("PageWidgetConstraint")
        return []

    def collectionConstraint(self):
        return []

    def generatePageWidget(self, graph, subject, templates, f, onlybody=False):
        print("PageWidget")
        f.write(templates["sparqltemplate"])

    def generateCollectionWidget(self, graph, templates, subject, f):
        print("CollectionWidget")

    def generatePageView(self, templates,pubconfig,voidstatshtml, g, f):
        print("PageView")
        sparqlhtml = DocUtils.replaceStandardVariables(templates["htmltemplate"], "", "0", "false")
        sparqlhtml = sparqlhtml.replace("{{iconprefixx}}", ("icons/" if pubconfig["offlinecompat"] else "")).replace(
            "{{baseurl}}", pubconfig["prefixnamespace"]).replace("{{relativedepth}}", "0").replace("{{relativepath}}",
                                                                                      ".").replace("{{toptitle}}",
                                                                                                   "SPARQL Query Editor").replace(
            "{{title}}", "SPARQL Query Editor").replace("{{startscriptpath}}", "startscripts.js").replace(
            "{{stylepath}}", "style.css") \
            .replace("{{classtreefolderpath}}", pubconfig["corpusid"] + "_classtree.js").replace("{{baseurlhtml}}", "").replace(
            "{{nonnslink}}", "").replace("{{scriptfolderpath}}", pubconfig["corpusid"] + "_search.js").replace("{{exports}}",
                                                                                                  templates[
                                                                                                      "nongeoexports"]).replace(
            "{{versionurl}}", DocConfig.versionurl).replace("{{version}}", DocConfig.version).replace("{{bibtex}}",
                                                                                                      "").replace(
            "{{proprelationpath}}", "proprelations.js")
        sparqlhtml += templates["sparqltemplate"]
        tempfoot = DocUtils.replaceStandardVariables(templates["footer"], "", "0", "false").replace("{{license}}",
                                                                                                pubconfig["license"]).replace(
            "{{exports}}", templates["nongeoexports"]).replace("{{bibtex}}", "").replace("{{stats}}",
                                                                                         voidstatshtml)
        tempfoot = DocUtils.conditionalArrayReplace(tempfoot, [True, pubconfig["apis"]["ogcapifeatures"], pubconfig["apis"]["iiif"],
                                                               pubconfig["apis"]["ckan"]],
                                                    [
                                                        "APIs: <a href=\"" + str(
                                                            pubconfig["deploypath"]) + "/sparql.html?endpoint=" + str(
                                                            pubconfig["deploypath"]) + "\">[SPARQL]</a>&nbsp;",
                                                        "<a href=\"" + str(
                                                            pubconfig["deploypath"]) + "/api/api.html\">[OGC API Features]</a>&nbsp;",
                                                        "<a href=\"" + str(
                                                            pubconfig["deploypath"]) + "/iiif/\">[IIIF]</a>&nbsp;",
                                                        "<a href=\"" + str(pubconfig["deploypath"]) + "/api/3/\">[CKAN]</a>"
                                                    ], "{{apis}}")
        sparqlhtml += tempfoot
        f.write(sparqlhtml)
