import json
import os
import re
from doc.docdefaults import DocDefaults



includepattern=r'{%\s*include\s*(.*)\s*%}'

class TemplateUtils:

    @staticmethod
    def resolveIncludes(template,templates):
        matches=re.findall(includepattern,template)
        if len(matches)>0:
            for mat in matches:
                if mat.replace(".html","") in templates:
                    template=template.replace("{% include "+mat+" %}",templates[mat.replace(".html","")])
        return template

    @staticmethod
    def resolveTemplate(templatename,templatepath):
        templates=DocDefaults.templates
        print(templatepath+"/"+templatename+" "+str(os.path.exists(templatepath+"/"+templatename+"/templates/")))
        print(templatepath + "/" + templatename + " " + str(
            os.path.exists(templatepath + "/" + templatename)))
        print(os.listdir(templatepath + "/" + templatename))
        if os.path.exists(templatepath+"/"+templatename+"/templateconf.json"):
            with open(templatepath+"/"+templatename+"/templateconf.json", 'r') as f:
                templatefiles = json.load(f)
                for file in templatefiles:
                    if os.path.exists(templatepath +"/"+templatename+"/"+ file):
                        with open(templatepath +"/"+templatename+"/"+ file["path"], 'r') as f:
                            if "name" in file:
                                templates[file["name"]]= f.read()
                            else:
                                templates[file] = f.read()
        elif os.path.exists(templatepath+"/"+templatename+"/templates/"):
            if os.path.exists(templatepath+"/"+templatename+"/templates/layouts/") and os.path.exists(templatepath+"/"+templatename+"/templates/includes/"):
                templates["includes"]={}
                templates["layouts"] = {}
                for filename in os.listdir(templatepath+"/"+templatename+"/templates/includes/"):
                    print("FOUND INCLUDE: "+str(filename))
                    if filename.endswith(".html") or filename.endswith(".css"):
                        with open(templatepath+"/"+templatename+"/templates/includes/"+filename, 'r') as f:
                            content=f.read()
                            templates["includes"][filename.replace(".html","")] = content
                            templates[filename.replace(".html", "")] = content
                for filename in os.listdir(templatepath + "/" + templatename + "/templates/layouts/"):
                    print("FOUND LAYOUT: " + str(filename))
                    if filename.endswith(".html") or filename.endswith(".css"):
                        with open(templatepath + "/" + templatename + "/templates/layouts/" + filename, 'r') as f:
                            content=f.read()
                            templates["layouts"][filename.replace(".html", "")] = content
                            templates[filename.replace(".html", "")] = content
            else:
                for filename in os.listdir(templatepath+"/"+templatename+"/templates/"):
                    if filename.endswith(".html") or filename.endswith(".css"):
                        with open(templatepath+"/"+templatename+"/templates/"+filename, 'r') as f:
                            templates[filename.replace(".html","")] = f.read()
        print("Found templates.... "+str(len(templates)))
        for temp in templates:
            if temp!="includes" and temp!="layouts":
                templates[temp]=TemplateUtils.resolveIncludes(templates[temp],templates)
        return templates