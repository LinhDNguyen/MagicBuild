import xml.etree.ElementTree as ET
import os

from test1.MagicBuild.Workspace import Workspace, BatchBuild
from test1.MagicBuild.Project import Project

class IARWorkspace(Workspace):
    """docstring for IARWorkspace"""
    def __init__(self, path):
        super(IARWorkspace, self).__init__(path)

        self.parse()

    def parse(self):
        # Parse IAR workspace to get informations
        tree = ET.parse(self.path)
        root = tree.getroot()
        curDir = os.path.dirname(self.path)

        # File project list
        for prj in root.findall("./project/path"):
            self.projects.append(os.path.join(curDir, prj.text))

        # Get batch list
        for batchEle in root.findall("./batchBuild/batchDefinition"):
            projects = []
            name = batchEle.find("./name").text

            for prjEle in batchEle.findall("./member"):
                path = prjEle.find("./project").text
                config = prjEle.find("./configuration").text
                configs = []
                configs.append(config)
                prj = Project(os.path.join(curDir, path), configs)
                projects.append(prj)
            self.batches[name] = projects

    def buildBatch(self, name):
        result = True
        messages = ""
        projects = self.batches[name]
        for prj in projects:
            msg = "=========BUILD PROJECT %s TARGET %s==========" % (prj.path, prj.configs[0])

            messages += msg + "\n"

        return (result, messages,)

    def buildProject(self, path, config):
        pass
