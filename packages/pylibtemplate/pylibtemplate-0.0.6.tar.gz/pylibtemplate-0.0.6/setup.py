# -*- coding: utf-8 -*-
# Copyright 2025 Matthew Fitzpatrick.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.
r"""The setup script for the ``pylibtemplate`` library.

"""



#####################################
## Load libraries/packages/modules ##
#####################################

# For determining the machine architecture.
import sys

# For running terminal commands.
import os



# For setting up ``pylibtemplate`` package.
import setuptools



####################################
## Define functions and constants ##
####################################

def clean():
    lib_name = "pylibtemplate"

    if sys.platform.startswith("win"):
        os.system("rmdir /s /q ./build")
        os.system("rmdir /s /q ./{}.egg-info".format(lib_name))
        os.system("del /q ./*.pyc")
        os.system("del /q ./*.tgz")
    else:
        os.system("rm -vrf ./build ./*.pyc ./*.tgz ./*.egg-info")

    return None



class CleanCommand(setuptools.Command):
    r"""Custom clean command to tidy up the project root.

    """
    user_options = []
    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass
    
    def run(self):
        clean()

        return None



def setup_package():
    r"""Setup the ``pylibtemplate`` package.

    """
    setuptools.setup(cmdclass={"clean": CleanCommand})

    return None


    
if __name__ == "__main__":
    setup_package()
    clean()
