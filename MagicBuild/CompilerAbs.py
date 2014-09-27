class CompilerAbs(object):
	"""docstring for CompilerAbs"""
	def __init__(self, id, path, target, options, **args):
		super(CompilerAbs, self).__init__()
		self.id = id
		self.path = path
		self.target = target
		self.options = options

	def build(self):
		output = ""
		result = True

		return (result, output)
