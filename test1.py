import sublime, sublime_plugin

from test1.MagicBuild.IARWorkspace import IARWorkspace

def get_settings():
	"""Load settings.

	:returns: dictionary containing settings
	"""
	return sublime.load_settings("test1.sublime-settings")


def get_setting(key, default=None):
	"""Load individual setting.

	:param key: setting key to get value for
	:param default: default value to return if no value found

	:returns: value for ``key`` if ``key`` exists, else ``default``
	"""
	return get_settings().get(key, default)

class Test1Command(sublime_plugin.TextCommand):

	def run(self, edit, **args):
		self.__currentWs = None
		self.__currentSelectList = None
		self.__currentEdit = edit
		runFrom = args["mode"]

		def on_batch_select(i):
			if(i < 0):
				return
			names = self.__currentSelectList
			iarWs = self.__currentWs
			result, messages = iarWs.buildBatch(names[i])

			# Create new view to display result
			nview = self.view.window().new_file()
			self.view.window().focus_view(nview)
			nview.set_name('MagicBuild result')
			nview.run_command('insertCharacters "RESULT - %d\n"' % result)
			#nview.run_command('insertCharacters', {'text': messages})
			nview.set_read_only(True)
			nview.set_scratch(True)
		# Check if run from workspace file
		if (runFrom == 'context') or (runFrom == 'key'):
			# Check if the current file is workspace file
			fileName = self.view.file_name()
			if not fileName:
				sublime.error_message("Please run on a workspace file!!!")
				return
			if not fileName.endswith('.eww'):
				sublime.error_message("Please run on a workspace file!!!")
				return

			# Is workspace file
			iarWs = IARWorkspace(fileName)
			self.__currentWs = iarWs
			# select what to build
			names = list(iarWs.batches.keys())
			self.__currentSelectList = names
			self.view.window().show_quick_panel(names, on_batch_select)

		elif (runFrom == 'sidebar'):
			sublime.message_dialog("Run from side bar!!!")

		self.view.insert(edit, 0, "Your are editing: " + str(self.view.file_name()) + "\n")
