#! /usr/bin/env python

# Copyright (c) 2013 Freescale Semiconductor, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# o Redistributions of source code must retain the above copyright notice, this list
#   of conditions and the following disclaimer.
#
# o Redistributions in binary form must reproduce the above copyright notice, this
#   list of conditions and the following disclaimer in the documentation and/or
#   other materials provided with the distribution.
#
# o Neither the name of Freescale Semiconductor, Inc. nor the names of its
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os, sys, subprocess
import argparse

## Separator between the build output of each project.
SECTION_LINE = "*" * 79

## Name of the file containing the projects list.
PROJECTS_FILE = "iar_projects_to_build.txt"

class BuildProjects:
    ## Constructor.
    def __init__(self):
        ## List of projects to be built.
        #
        #  The items in the list are 3-tuples containing the project path, configuration to build,
        #  and the device the project builds for.
        self.projectList = []

        ## Path to the bin directory containing this script.
        self._binDir = os.path.dirname(os.path.realpath(__file__))

        ## The repository root directory.
        self.repositoryRoot = os.path.dirname(os.path.dirname(self._binDir))

        ## Path to the IAR build tool.
        self._iarPath = None

        ## Error project list
        self.errorList = []

        ## Whether to build only changed files.
        self._incremental = True

        ## Whether to clean instead of build.
        self._clean = False

        ## Whether to stop at the first faild project.
        self._stop = False

        ## List of devices to build. If empty, all devices will be built.
        self._devices = []

    ##
    # @brief Import list of projects to be built.
    def import_projects(self):
        # Import project list to a list of tuples
        with open(PROJECTS_FILE) as f:
            self.projectList = [l.split('||') for l in f.read().splitlines() if (not
                l.startswith("#") and len(l.strip('||')) > 0)]

        # Check if user specified a build config
        for i in self.projectList:
            if len(i) < 2:
                raise RuntimeError("Please specify build configuration for " + i[0] + " (i.e., Debug or Release)")

    ## Recursively find all IAR workspace file (.ewp)
    def search_projects(self):
        fileList = []
        # Search .ewp files in project root dirctory
        for root, dirs, files in os.walk(self.repositoryRoot):
            for file in files:
                if file.endswith(".ewp"):
                    fileList.append(os.path.abspath(os.path.join(root, file)))
        return fileList

    ## Find iarBuild.exe path in system
    def search_iar(self):
        try:
            workbenchPath = os.environ['IAR_WORKBENCH']
        except KeyError:
            raise RuntimeError("IAR_WORKBENCH environment variable is not set.")
        else:
            iarBuildPath = os.path.normpath(os.path.join(workbenchPath, "common", "bin", "IarBuild.exe"))

            if not os.path.isfile(iarBuildPath):
                raise RuntimeError("IarBuild.exe does not exist at: {}".format(iarBuildPath))

            return iarBuildPath

    ## Build project using iar
    def build(self, projectPath, buildConfig):
        # Add project root path to project path
        projectPath = os.path.join(self.repositoryRoot, projectPath)

        # Some build information to make it looks better
        startInfo = "    Build started " + projectPath
        endInfo = "    Build finished " + projectPath

        # Print build starting information in cmd
        print (SECTION_LINE + "\n" + startInfo + " --" + buildConfig + "\n")
        sys.stdout.flush()

        if self._clean:
            buildMode = "-clean"
        elif self._incremental:
            buildMode = "-make"
        else:
            buildMode = "-build"

        # Call IarBuild
        p = subprocess.Popen([self._iarPath, projectPath, buildMode, buildConfig, '-log', 'errors'],
            stdout=None, stderr=subprocess.STDOUT, bufsize=0)
        returncode = p.wait()

        if returncode != 0:
            self.errorList.append((projectPath, buildConfig))
            if self._stop:
                raise RuntimeError("** Build of {} failed.".format(projectPath))
            else:
                print "** Build of {} failed.".format(projectPath)

        # Print build ending information in cmd
        print ('\n' + endInfo + " --" + buildConfig + "\n")
        sys.stdout.flush()

    def _read_options(self):
        # Build arg parser.
        parser = argparse.ArgumentParser(
                    formatter_class=argparse.RawDescriptionHelpFormatter,
                    description="Build IAR projects")

        # Options
        parser.add_argument("-i", "--incremental", action="store_true", default=True, help="Incremental build (default).")
        parser.add_argument("-a", "--all", dest="incremental", action="store_false", help="Full build.")
        parser.add_argument("-c", "--clean", action="store_true", default=False, help="Clean instead of build.")
        parser.add_argument("-s", "--stop", action="store_true", default=False, help="Stop build at the first faild project.")
        parser.add_argument("-l", "--project_list", action="store_true", default=False, help="Print all IAR projects list found in parent path of this file location.")
        parser.add_argument("-d", "--device", action="append", metavar="DEVICES", help="Takes a comma separated list of devices to build. Projects are built if the project's device starts with the device argument(s). By default all devices are built.")

        return parser.parse_args()

    def run(self):
        # Read command line arguments.
        args = self._read_options()
        self._incremental = args.incremental
        self._clean = args.clean
        self._stop = args.stop

        if args.project_list:
            fileList = self.search_projects()
            for f in fileList:
                print f
            return 1

        if args.device:
            for d in args.device:
                self._devices.extend(d.lower().split(','))

        # Change current running path to bin dir in case of using Eclipse
        os.chdir(self._binDir)

        # Import the list of projects.
        self.import_projects()

        # Get iar path
        self._iarPath = self.search_iar()

        # build projects
        try:
            for projectInfo in self.projectList:
                # if no devices were specified to be built, or the project didn't specify
                # a device, then the project will be built.
                if not self._devices or len(projectInfo) < 3:
                    buildIt = True
                else:
                    # determine whether to build the project by looking at its device.
                    device = projectInfo[2].lower()
                    buildIt = any(device.startswith(d) for d in self._devices)

                if buildIt:
                    self.build(projectInfo[0], projectInfo[1])
        except RuntimeError as e:
            print
            print "**", e

        print SECTION_LINE
        print "          I A R   B U I L D   F I N I S H"
        print SECTION_LINE

        # print project with errors
        if len(self.errorList) > 0:
            print len(self.errorList), " builds failed:"
            for failedProjectInfo in self.errorList:
                print failedProjectInfo[0] + " --" + failedProjectInfo[1]

            print SECTION_LINE
            # Build failed, so return a non-zero status.
            return 1
        else:
            print "** all builds succeeded."
            print SECTION_LINE
            return 0

if __name__ == "__main__":
    exit(BuildProjects().run())

