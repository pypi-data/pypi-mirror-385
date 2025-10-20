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
r"""An example of generating a local ``git`` repository template using
:mod:`pylibtemplate`.

It is recommended that you consult the documentation of the :mod:`pylibtemplate`
library as you explore this example script.

"""



#####################################
## Load libraries/packages/modules ##
#####################################

# For generating local ``git`` repository templates.
import pylibtemplate



##############################################
## Define classes, functions, and constants ##
##############################################



###########################
## Define error messages ##
###########################



#########################
## Main body of script ##
#########################

kwargs = {"lib_name_for_imports": "mypylib",
          "abbreviated_lib_name_for_docs": "MyPyLib",
          "non_abbreviated_lib_name_for_docs": "My Python Library",
          "author": "Randy Lahey",
          "email": "randy.lahey@bobandy.com",
          "gist_id": "5klmds090sdm2jansdu92nrlkjnmsa9r",
          "path_to_directory_to_contain_new_repo": "./examples_data"}
pylibtemplate.generate_local_git_repo_template(**kwargs)
