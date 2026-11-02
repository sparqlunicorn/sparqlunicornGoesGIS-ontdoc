import json
import os
import re
from doc.docdefaults import DocDefaults


class TemplateUtils:

    includepattern = r'{%\s*include\s*(.*)\s*%}'

    @staticmethod
    def resolveIncludes(template,templates):
        for match in re.finditer(TemplateUtils.includepattern, template):
            template_name = match.group(1).strip().removesuffix(".html")
            if template_name in templates:
                template=template.replace(match.group(0),templates[template_name])
        return template

    @staticmethod
    def resolveTemplate(templatename,templatepath):
        templates=DocDefaults.templates
        templates["includes"] = {}
        templates["js"] = {}
        templates["layouts"] = {}
        print(f"{templatepath}/{templatename} {os.path.exists(f'{templatepath}/{templatename}/templates/')}")
        print(f"{templatepath}/{templatename} {os.path.exists(f'{templatepath}/{templatename}')}")
        #print(os.listdir(f"{templatepath}/{templatename}"))
        if os.path.exists(f"{templatepath}/{templatename}/templateconf.json"):
            with open(f"{templatepath}/{templatename}/templateconf.json", 'r',encoding="utf-8") as f:
                templatefiles = json.load(f)
                for file in templatefiles:
                    if os.path.exists(f"{templatepath}/{templatename}/{file}"):
                        with open(f"{templatepath}/{templatename}/{file['path']}", 'r',encoding="utf-8") as f2:
                            if "name" in file:
                                templates[file["name"]]= f2.read()
                            else:
                                templates[file] = f2.read()
        elif os.path.exists(f"{templatepath}/{templatename}/templates/"):
            if os.path.exists(f"{templatepath}/{templatename}/templates/layouts/") and os.path.exists(f"{templatepath}/{templatename}/templates/includes/"):
                for filename in os.listdir(f"{templatepath}/{templatename}/templates/includes/"):
                    print(f"FOUND INCLUDE: {filename}")
                    if filename.endswith(".html") or filename.endswith(".css"):
                        template_name = filename.removesuffix(".html")
                        with open(f"{templatepath}/{templatename}/templates/includes/{filename}", 'r',encoding="utf-8") as f:
                            content=f.read()
                            templates["includes"][template_name] = content
                            templates[template_name] = content
                for filename in os.listdir(f"{templatepath}/{templatename}/js/"):
                    print(f"FOUND INCLUDE: {filename}")
                    if filename.endswith(".js"):
                        template_name = filename.removesuffix(".js")
                        with open(f"{templatepath}/{templatename}/js/{filename}", 'r',encoding="utf-8") as f:
                            content=f.read()
                            templates["js"][template_name] = content
                            templates[template_name] = content
                for filename in os.listdir(f"{templatepath}/{templatename}/templates/layouts/"):
                    print(f"FOUND LAYOUT: {filename}")
                    if filename.endswith(".html") or filename.endswith(".css"):
                        template_name = filename.removesuffix(".html")
                        with open(f"{templatepath}/{templatename}/templates/layouts/{filename}", 'r',encoding="utf-8") as f:
                            content=f.read()
                            templates["layouts"][template_name] = content
                            templates[template_name] = content
            else:
                for filename in os.listdir(f"{templatepath}/{templatename}/templates/"):
                    if filename.endswith(".html") or filename.endswith(".css"):
                        template_name = filename.removesuffix(".html")
                        with open(f"{templatepath}/{templatename}/templates/{filename}", 'r',encoding="utf-8") as f:
                            templates[template_name] = f.read()
                if os.path.exists(f"{templatepath}/{templatename}/js/"):
                    for filename in os.listdir(f"{templatepath}/{templatename}/js/"):
                        print(f"FOUND INCLUDE: {filename}")
                        if filename.endswith(".js"):
                            template_name = filename.removesuffix(".js")
                            with open(f"{templatepath}/{templatename}/js/{filename}", 'r',encoding="utf-8") as f:
                                content=f.read()
                                templates["js"][template_name] = content
                                templates[template_name] = content
                if os.path.exists(f"{templatepath}/{templatename}/css/"):
                    for filename in os.listdir(f"{templatepath}/{templatename}/css/"):
                        print(f"FOUND LAYOUT: {filename}")
                        if filename.endswith(".css"):
                            template_name = filename.removesuffix(".css")
                            with open(f"{templatepath}/{templatename}/css/{filename}", 'r',encoding="utf-8") as f:
                                content=f.read()
                                templates[template_name] = content
        print(f"Found templates.... {len(templates)}")
        for temp in templates:
            if temp!="includes" and temp!="layouts" and temp!="js" and templates[temp] is not None:
                templates[temp]=TemplateUtils.resolveIncludes(templates[temp],templates)
        return templates