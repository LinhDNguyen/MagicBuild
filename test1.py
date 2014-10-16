import os
import sublime, sublime_plugin
import subprocess

from MagicBuild.MagicBuild.IARWorkspace import IARWorkspace
from MagicBuild.MagicBuild.ProcessUtil import ProcessUtil

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
		buildTimeOut = int(get_setting('build_timeout'))

		def on_batch_select(i):
			if(i < 0):
				return
			names = self.__currentSelectList
			iarWs = self.__currentWs
			result, messages = iarWs.buildBatch(names[i], buildTimeOut)

			# Create new view to display result
			nview = self.view.window().new_file()
			self.view.window().focus_view(nview)
			nview.set_name('MagicBuild result')
			msg = ""
			nview.run_command("insert", {"characters": "%s - %s\n" % (iarWs.path, names[i])})
			msg = "BUILD RESULT - "
			if result:
				msg += "PASS"
			else:
				msg += "FAIL"
			nview.run_command("insert", {"characters": msg + "\n"})
			nview.run_command("insert", {"characters": "%s\n" % messages})
			nview.set_read_only(True)
			nview.set_scratch(True)
			nview.show(sublime.Region(0, 0))

		def on_workspace_select(i):
			if (i < 0):
				return
			workspaces = self.__currentSelectList
			# Parse workspace name
			fullName = workspaces[i]
			arr = fullName.split('|')
			if(len(arr) != 2):
				return
			wsPath = arr[0].strip()
			batch = arr[1].strip()
			iarWs = IARWorkspace(wsPath, get_setting('compilers')['iar'])

			# Build batch and return result
			result, messages = iarWs.buildBatch(batch, buildTimeOut)

			# Create new view to display result
			nview = self.view.window().new_file()
			self.view.window().focus_view(nview)
			nview.set_name('MagicBuild result')
			nview.run_command("insert", {"characters": "%s - %s\n" % (iarWs.path, batch)})
			msg = "BUILD RESULT - "
			if result:
				msg += "PASS"
			else:
				msg += "FAIL"
			nview.run_command("insert", {"characters": msg + "\n"})
			nview.run_command("insert", {"characters": "%s\n" % messages})
			nview.set_read_only(True)
			nview.set_scratch(True)
			nview.show(sublime.Region(0, 0))

		# Check if run from workspace file
		if (runFrom == 'context') or (runFrom == 'key'):
			# Check if the current file is workspace file
			fileName = self.view.file_name()
			if not fileName:
				sublime.error_message("Please run on a workspace file!!!")
				return
			if not fileName.endswith('.eww'):
				#sublime.error_message("Please run on a workspace file!!!")
				#return
				# Create new view to display result
				
				sublime.set_timeout_async(self.test_command, 0)
				return

			# Is workspace file
			iarWs = IARWorkspace(fileName, get_setting('compilers')['iar'])
			self.__currentWs = iarWs
			# select what to build
			names = list(iarWs.batches.keys())
			self.__currentSelectList = names

			self.view.window().show_quick_panel(names, on_batch_select)

		elif (runFrom == 'sidebar'):
			# Run command from Side Bar, find all workspace file
			workspaces = []
			wsNames = []
			runDirs = args["dirs"]
			runFiles = args["files"]
			# find in all dirs
			for d in runDirs:
				# search all workspace file
				for root, dirnames, filenames in os.walk(d):
					for filename in filenames:
						if filename.endswith('.eww'):
							fullPath = os.path.join(root, filename)
							iarWs = IARWorkspace(fullPath)
							for batch in list(iarWs.batches.keys()):
								workspaces.append("%s|%s" % (fullPath, batch))
								# Add name of workspace into wsNames, used to display in input pannel
								wsNames.append("%s | %s" % (batch, filename))
			for f in runFiles:
				iarWs = IARWorkspace(f)
				for batch in list(iarWs.batches.keys()):
					workspaces.append("%s|%s" % (f, batch))
					# Add name of workspace into wsNames, used to display in input pannel
					wsNames.append("%s | %s" % (batch, os.path.basename(f)))
			# User select workspace from input pannel
			self.__currentSelectList = workspaces
			self.view.window().show_quick_panel(wsNames, on_workspace_select)
		else:
			sublime.message_dialog("Run from Unknow...%s" % str(runFrom))

	def test_command(self):
		nview = self.view.window().new_file()
		self.view.window().focus_view(nview)
		nview.set_name('MagicBuild result')
		msg = ""
		nview.run_command("insert", {"characters": "Just a test from Linh\n"})
		
		cmd = [
			'ping',
			'google.com.vn'
		]

		out_str = ''
		try:
			out_str = subprocess.check_output(cmd, shell=True, env=None, 
										stderr=subprocess.STDOUT)
		except Exception as ex:
			out_str += str(ex)
		# (ret_code, is_timed_out, out_str, err_str) = ProcessUtil.run_job(
		# 											cmd, 20)
		nview.run_command("insert", {"characters": "\n".join(out_str.decode('windows-1252').splitlines())})

		nview.set_read_only(True)
		nview.set_scratch(True)
		nview.show(sublime.Region(0, 0))

