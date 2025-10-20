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
r"""Contains tests for the root of the package :mod:`pylibtemplate`.

"""



#####################################
## Load libraries/packages/modules ##
#####################################

# For operations related to unit tests.
import pytest

# For removing directories.
import shutil

# For setting file permissions and executing Python scripts.
import os

# For making directories.
import pathlib



# For generating local ``git`` repository templates.
import pylibtemplate



##################################
## Define classes and functions ##
##################################

def test_1_of_generate_local_git_repo_template():
    path_to_test_data = "./pylibtemplate"

    pylibtemplate.generate_local_git_repo_template()
    
    shutil.rmtree(path_to_test_data)

    return None



def test_2_of_generate_local_git_repo_template():
    path_to_test_data = "./test_data"

    kwargs = {"lib_name_for_imports": "mypylib",
              "abbreviated_lib_name_for_docs": "MyPyLib",
              "non_abbreviated_lib_name_for_docs": "My Python Library",
              "author": "Randy Lahey",
              "email": "randy.lahey@bobandy.com",
              "gist_id": "5klmds090sdm2jansdu92nrlkjnmsa9r",
              "path_to_directory_to_contain_new_repo": path_to_test_data}
    pylibtemplate.generate_local_git_repo_template(**kwargs)

    shutil.rmtree(path_to_test_data)

    return None



def test_3_of_generate_local_git_repo_template():
    path_to_test_data = "./test_data"
    pathlib.Path(path_to_test_data).mkdir(parents=True, exist_ok=True)
    os.chmod(path_to_test_data, 0o111)

    with pytest.raises(IOError) as err_info:
        kwargs = {"path_to_directory_to_contain_new_repo": \
                  path_to_test_data + "/mypylib"}
        pylibtemplate.generate_local_git_repo_template(**kwargs)

    os.chmod(path_to_test_data, 0o711)

    shutil.rmtree(path_to_test_data)

    return None



def test_4_of_generate_local_git_repo_template():
    with pytest.raises(ValueError) as err_info:
        kwargs = {"lib_name_for_imports": "123abc"}
        pylibtemplate.generate_local_git_repo_template(**kwargs)

    with pytest.raises(ValueError) as err_info:
        kwargs = {"abbreviated_lib_name_for_docs": "123abc"}
        pylibtemplate.generate_local_git_repo_template(**kwargs)

    param_name_subset = ("author",
                         "email",
                         "gist_id",
                         "path_to_directory_to_contain_new_repo")

    for param_name in param_name_subset:
        with pytest.raises(TypeError) as err_info:
            kwargs = {param_name: slice(None)}
            pylibtemplate.generate_local_git_repo_template(**kwargs)

    return None



def test_5_of_generate_local_git_repo_template():
    path_to_test_data = "./test_data"

    kwargs = {"lib_name_for_imports": "mypylib",
              "abbreviated_lib_name_for_docs": "MyPyLib",
              "non_abbreviated_lib_name_for_docs": "My Python Library",
              "author": "F"+ "o"*170 +" Bar",
              "email": "randy.lahey@bobandy.com",
              "gist_id": "5klmds090sdm2jansdu92nrlkjnmsa9r",
              "path_to_directory_to_contain_new_repo": path_to_test_data}
    pylibtemplate.generate_local_git_repo_template(**kwargs)

    shutil.rmtree(path_to_test_data)

    return None



def test_1_of_run_pylibtemplate_as_an_app():
    path_to_test_data = "./test_data"

    params = {"lib_name_for_imports": "mypylib",
              "abbreviated_lib_name_for_docs": "MyPyLib",
              "non_abbreviated_lib_name_for_docs": "My Python Library",
              "author": "Randy Lahey",
              "email": "randy.lahey@bobandy.com",
              "gist_id": "5klmds090sdm2jansdu92nrlkjnmsa9r",
              "path_to_directory_to_contain_new_repo": path_to_test_data}

    cmd_line_args = []
    for param_name in params:
        cmd_line_arg = "--"+param_name+"="+str(params[param_name])
        cmd_line_args.append(cmd_line_arg)

    pylibtemplate._run_pylibtemplate_as_an_app(cmd_line_args)

    with pytest.raises(BaseException) as err_info:
        cmd_line_arg = "--foo=bar"
        cmd_line_args.append(cmd_line_arg)
        pylibtemplate._run_pylibtemplate_as_an_app(cmd_line_args)

    shutil.rmtree(path_to_test_data)

    return None



###########################
## Define error messages ##
###########################
