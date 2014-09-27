class Project(object):
    """docstring for Project"""
    def __init__(self, path, configs=[]):
        super(Project, self).__init__()
        self.path = path
        self.configs = configs

    def parse(self):
        pass
