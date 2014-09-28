
class BatchBuild(object):
    """docstring for BatchBuild"""
    def __init__(self, name, projects=[]):
        super(BatchBuild, self).__init__()
        self.name = name
        self.projects = projects

class Workspace(object):
    """docstring for Workspace"""
    def __init__(self, path, toolchainPath = ''):
        super(Workspace, self).__init__()
        self.path = path
        self.toolchainPath = toolchainPath
        self.batches = {}
        self.projects = []

    def getBatchNames(self):
        return self.batches.keys()

    def parse(self):
        pass

    def buildBatch(self, name):
        pass

    def buildProject(self, path, config):
        pass
