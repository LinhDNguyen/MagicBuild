import os
import xml.etree.ElementTree as ET
import subprocess

from MagicBuild.MagicBuild.Workspace import Workspace, BatchBuild
from MagicBuild.MagicBuild.Project import Project
from MagicBuild.MagicBuild.ProcessUtil import ProcessUtil

class IARWorkspace(Workspace):
    """docstring for IARWorkspace"""
    def __init__(self, path, toolchainPath = ''):
        super(IARWorkspace, self).__init__(path, toolchainPath)

        self.parse()

    def parse(self):
        # Parse IAR workspace to get informations
        tree = ET.parse(self.path)
        root = tree.getroot()
        curDir = os.path.dirname(self.path)

        # File project list
        for prj in root.findall("./project/path"):
            path = prj.text
            path = path.replace('$WS_DIR$', curDir)
            self.projects.append(os.path.normpath(os.path.join(curDir, path)))

        # Get batch list
        for batchEle in root.findall("./batchBuild/batchDefinition"):
            projects = []
            name = batchEle.find("./name").text

            for prjEle in batchEle.findall("./member"):
                pname = prjEle.find("./project").text + ".ewp"
                config = prjEle.find("./configuration").text
                configs = []
                configs.append(config)
                path = pname
                for prj in self.projects:
                    if prj.endswith(pname):
                        path = prj
                prj = Project(os.path.normpath(path), configs)
                projects.append(prj)
            self.batches[name] = projects

    def buildBatch(self, name, timeout=100):
        result = True
        messages = ""
        projects = self.batches[name]
        for prj in projects:
            messages += "\n\n=========BUILD PROJECT %s TARGET %s==========\n" % (prj.path, prj.configs[0])

            prjResult, outStr = self.buildProject(prj.path, prj.configs[0], timeout)
            if prjResult != 0:
                result = False
            messages += str(outStr.decode("windows-1252"))

        return (result, messages, )

    def buildProject(self, path, config, timeout=100):
        iarBuildPath = os.path.normpath(os.path.join(self.toolchainPath, "common", "bin", "IarBuild.exe"))

        # Call IarBuild
        # build_cmd = [
        #     iarBuildPath,
        #     path,
        #     '-make', config,
        #     '-log', 'all'
        # ]
        build_cmd = [
            'TIMEOUT',
            '10',
        ]
        (ret_code, is_timed_out, out_str, err_str) = ProcessUtil.run_job(
            build_cmd, timeout)

        return (ret_code, out_str, )
