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
r""":mod:`pylibtemplate` (short for 'Python Library Template') is a Python
library that generates ``git`` repository templates for building Python
libraries that are suitable for publication on PyPI.

"""



#####################################
## Load libraries/packages/modules ##
#####################################

# For converting relative paths to absolute paths, and for making directories.
import pathlib

# For timing the execution of different segments of code.
import time

# For getting the current year.
import datetime

# For pattern matching.
import re

# For removing directories.
import shutil

# For removing files, renaming directories, and getting directory trees.
import os

# For wrapping text.
import textwrap

# For parsing command line arguments.
import argparse



# For validating and converting objects.
import czekitout.check
import czekitout.convert

# For cloning ``git`` repositories.
import git



# Get version of current package.
from pylibtemplate.version import __version__



##################################
## Define classes and functions ##
##################################

# List of public objects in package.
__all__ = ["generate_local_git_repo_template"]



_pylibtemplate_lib_name_for_imports = "pylibtemplate"
_pylibtemplate_abbreviated_lib_name_for_docs = "PyLibTemplate"
_pylibtemplate_non_abbreviated_lib_name_for_docs = "Python Library Template"
_pylibtemplate_author = "Matthew Fitzpatrick"
_pylibtemplate_email = "matthew.rc.fitzpatrick@gmail.com"
_pylibtemplate_gist_id = "7baba2a56d07b59cc49b8323f44416e5"
_pylibtemplate_copyright_year = "2025"



def _check_and_convert_lib_name_for_imports(params):
    obj_name = "lib_name_for_imports"
    kwargs = {"obj": params[obj_name], "obj_name": obj_name}
    lib_name_for_imports = czekitout.convert.to_str_from_str_like(**kwargs)

    current_func_name = "_check_and_convert_lib_name_for_imports"

    if not lib_name_for_imports.isidentifier():
        err_msg = globals()[current_func_name+"_err_msg_1"]
        raise ValueError(err_msg)
    
    return lib_name_for_imports



def _check_and_convert_abbreviated_lib_name_for_docs(params):
    obj_name = \
        "abbreviated_lib_name_for_docs"
    kwargs = \
        {"obj": params[obj_name], "obj_name": obj_name}
    abbreviated_lib_name_for_docs = \
        czekitout.convert.to_str_from_str_like(**kwargs)

    current_func_name = "_check_and_convert_abbreviated_lib_name_for_docs"

    if not abbreviated_lib_name_for_docs.isidentifier():
        err_msg = globals()[current_func_name+"_err_msg_1"]
        raise ValueError(err_msg)
    
    return abbreviated_lib_name_for_docs



def _check_and_convert_non_abbreviated_lib_name_for_docs(params):
    obj_name = \
        "non_abbreviated_lib_name_for_docs"
    kwargs = \
        {"obj": params[obj_name], "obj_name": obj_name}
    non_abbreviated_lib_name_for_docs = \
        czekitout.convert.to_str_from_str_like(**kwargs)
    
    return non_abbreviated_lib_name_for_docs



def _check_and_convert_author(params):
    obj_name = "author"
    kwargs = {"obj": params[obj_name], "obj_name": obj_name}
    author = czekitout.convert.to_str_from_str_like(**kwargs)
    
    return author



def _check_and_convert_email(params):
    obj_name = "email"
    kwargs = {"obj": params[obj_name], "obj_name": obj_name}
    email = czekitout.convert.to_str_from_str_like(**kwargs)
    
    return email



def _check_and_convert_gist_id(params):
    obj_name = "gist_id"
    kwargs = {"obj": params[obj_name], "obj_name": obj_name}
    gist_id = czekitout.convert.to_str_from_str_like(**kwargs)
    
    return gist_id



def _check_and_convert_path_to_directory_to_contain_new_repo(params):
    obj_name = \
        "path_to_directory_to_contain_new_repo"
    kwargs = \
        {"obj": params[obj_name], "obj_name": obj_name}
    path_to_directory_to_contain_new_repo = \
        czekitout.convert.to_str_from_str_like(**kwargs)
    path_to_directory_to_contain_new_repo = \
        str(pathlib.Path(path_to_directory_to_contain_new_repo).absolute())
    
    return path_to_directory_to_contain_new_repo



_default_lib_name_for_imports = \
    _pylibtemplate_lib_name_for_imports
_default_abbreviated_lib_name_for_docs = \
    _pylibtemplate_abbreviated_lib_name_for_docs
_default_non_abbreviated_lib_name_for_docs = \
    _pylibtemplate_non_abbreviated_lib_name_for_docs
_default_author = \
    _pylibtemplate_author
_default_email = \
    _pylibtemplate_email
_default_gist_id = \
    _pylibtemplate_gist_id
_default_path_to_directory_to_contain_new_repo = \
    ""



def generate_local_git_repo_template(
        lib_name_for_imports=\
        _default_lib_name_for_imports,
        abbreviated_lib_name_for_docs=\
        _default_abbreviated_lib_name_for_docs,
        non_abbreviated_lib_name_for_docs=\
        _default_non_abbreviated_lib_name_for_docs,
        author=\
        _default_author,
        email=\
        _default_email,
        gist_id=\
        _default_gist_id,
        path_to_directory_to_contain_new_repo=\
        _default_path_to_directory_to_contain_new_repo):
    r"""Generate a local ``git`` repository template.

    The primary purpose of generating a local ``git`` repository template is to
    modify it subsequently to develop a new Python library.

    This Python function will perform several actions: First, it will clone the
    ``git`` commit of the ``pylibtemplate`` GitHub repository corresponding to
    the version of ``pylibtemplate`` being used currently, in the directory at
    the path ``path_to_directory_to_contain_new_repo``, i.e. the ``git clone``
    command is executed while the working directory is set temporarily to the
    path ``path_to_directory_to_contain_new_repo``; Next, it will rename the
    cloned repository to ``lib_name_for_imports`` such that the path to the
    cloned repository becomes
    ``path_to_directory_to_contain_new_repo+"/"+lib_name_for_imports``; Next,
    all instances of the string of characters "pylibtemplate" are replaced with
    ``lib_name_for_imports``, be it in file contents, directory basenames, or
    file basenames; Next, all instances of the string of characters
    "PyLibTemplate" are replaced with ``abbreviated_lib_name_for_docs``; Next,
    all instances of the string of characters "Python Library Template" are
    replaced with ``non_abbreviated_lib_name_for_docs``; Next, all email address
    placeholders (i.e. instances of the string of characters
    "matthew.rc.fitzpatrick@gmail.com") are replaced with ``email``; Next, all
    instances of the gist ID of ``pylibtemplate`` are replaced with ``gist_id``;
    Next, all author placeholders (i.e. instances of the string of characters
    "Matthew Fitzpatrick") are replaced with ``author``; Next, all copyright
    statements are updated according to the current year; And lastly, the
    following file is removed::

    * ``<local_repo_root>/docs/how_to_create_a_python_library_using_pylibtemplate.rst``

    where ``<local_repo_root>`` is the root of the local ``git`` repository, as
    well as the following directory::

    * ``<local_repo_root>/.git``

    On a unrelated note, for the purposes of demonstrating the citing of
    literature, we cite Ref. [RefLabel1]_ and [RefLabel2]_.

    Parameters
    ----------
    lib_name_for_imports : `str`, optional
        The name of the new Python library, as it would appear in Python import
        commands. This parameter needs to be a valid Python identifier.
    abbreviated_lib_name_for_docs : `str`, optional
        An abbreviated format of the name of the new Python library that appears
        in documentation pages. This parameter needs to be a valid Python 
        identifier. It can be set to the same value as ``lib_name_for_imports``.
    non_abbreviated_lib_name_for_docs : `str`, optional
        A non-abbreviated format of the name of the new Python library that
        appears in documentation pages.
    author : `str`, optional
        The name of the author of the new Python library.
    email : `str`, optional
        The email address of the author.
    gist_id : `str`, optional
        The ID of the GitHub gist to be used to record the code coverage from
        your unit tests. See the
        :ref:`how_to_create_a_python_library_using_pylibtemplate_sec` page for
        instructions on how to create a GitHub gist for your new Python library.
    path_to_directory_to_contain_new_repo : `str`, optional
        The path to the directory inside which the ``git`` commit --- of the
        ``pylibtemplate`` GitHub repository corresponding to the version of
        ``pylibtemplate`` being used currently --- is to be cloned, i.e. the
        ``git clone`` command is executed while the working directory is set
        temporarily to ``path_to_directory_to_contain_new_repo``.

    """
    params = locals()

    global_symbol_table = globals()
    for param_name in params:
        func_name = "_check_and_convert_" + param_name
        func_alias = global_symbol_table[func_name]
        params[param_name] = func_alias(params)

    kwargs = params
    result = _generate_local_git_repo_template(**kwargs)

    return None



def _generate_local_git_repo_template(lib_name_for_imports,
                                      abbreviated_lib_name_for_docs,
                                      non_abbreviated_lib_name_for_docs,
                                      author,
                                      email,
                                      gist_id,
                                      path_to_directory_to_contain_new_repo):
    kwargs = locals()
    _print_generate_local_git_repo_template_starting_msg(**kwargs)

    start_time = time.time()

    kwargs = {"path_to_directory_to_contain_new_repo": \
              path_to_directory_to_contain_new_repo,
              "lib_name_for_imports": \
              lib_name_for_imports}
    _clone_pylibtemplate_repo(**kwargs)
    _rm_file_subset_of_local_git_repo(**kwargs)
    _mv_directory_subset_of_local_git_repo(**kwargs)
    filenames = _get_paths_to_files_in_local_git_repo(**kwargs)

    text_replacement_map = {_pylibtemplate_lib_name_for_imports: \
                            lib_name_for_imports,
                            _pylibtemplate_abbreviated_lib_name_for_docs: \
                            abbreviated_lib_name_for_docs,
                            _pylibtemplate_non_abbreviated_lib_name_for_docs: \
                            non_abbreviated_lib_name_for_docs,
                            _pylibtemplate_author: \
                            author,
                            _pylibtemplate_email: \
                            email,
                            _pylibtemplate_gist_id: \
                            gist_id,
                            _pylibtemplate_copyright_year: \
                            str(datetime.datetime.now().year)}

    kwargs = {"paths_to_files_in_local_git_repo": filenames,
              "text_replacement_map": text_replacement_map}
    _replace_and_wrap_text(**kwargs)

    kwargs = {"start_time": \
              start_time,
              "path_to_directory_to_contain_new_repo": \
              path_to_directory_to_contain_new_repo,
              "lib_name_for_imports": \
              lib_name_for_imports}
    _print_generate_local_git_repo_template_end_msg(**kwargs)

    return None



def _print_generate_local_git_repo_template_starting_msg(
        lib_name_for_imports,
        abbreviated_lib_name_for_docs,
        non_abbreviated_lib_name_for_docs,
        author,
        email,
        gist_id,
        path_to_directory_to_contain_new_repo):
    unformatted_msg = ("Generating a local ``git`` repository with the "
                       "following parameters:\n"
                       "\n"
                       "``lib_name_for_imports`` = ``'{}'``\n"
                       "``abbreviated_lib_name_for_docs`` = ``'{}'``\n"
                       "``non_abbreviated_lib_name_for_docs`` = ``'{}'``\n"
                       "``author`` = ``'{}'``\n"
                       "``email`` = ``'{}'``\n"
                       "``gist_id`` = ``'{}'``\n"
                       "``path_to_directory_to_contain_new_repo`` = ``'{}'``\n"
                       "\n"
                       "..."
                       "\n")
    msg = unformatted_msg.format(lib_name_for_imports,
                                 abbreviated_lib_name_for_docs,
                                 non_abbreviated_lib_name_for_docs,
                                 author,
                                 email,
                                 gist_id,
                                 path_to_directory_to_contain_new_repo)
    print(msg)

    return None



def _clone_pylibtemplate_repo(path_to_directory_to_contain_new_repo,
                              lib_name_for_imports):
    current_func_name = "_clone_pylibtemplate_repo"

    try:
        kwargs = {"output_dirname": path_to_directory_to_contain_new_repo}
        _make_output_dir(**kwargs)

        github_url = "https://github.com/mrfitzpa/pylibtemplate.git"

        kwargs = {"path_to_directory_to_contain_new_repo": \
                  path_to_directory_to_contain_new_repo,
                  "lib_name_for_imports": \
                  lib_name_for_imports}
        path_to_new_repo = _generate_path_to_new_repo(**kwargs)

        tag = _get_pylibtemplate_tag()

        cloning_options = (tuple()
                           if (tag is None)
                           else ("--depth 1", "--branch {}".format(tag)))

        kwargs = {"url": github_url,
                  "to_path": path_to_new_repo,
                  "multi_options": cloning_options}
        git.Repo.clone_from(**kwargs)
    except:
        err_msg = globals()[current_func_name+"_err_msg_1"]
        IOError(err_msg)

    return None



def _make_output_dir(output_dirname):
    current_func_name = "_make_output_dir"

    try:
        pathlib.Path(output_dirname).mkdir(parents=True, exist_ok=True)
    except:
        unformatted_err_msg = globals()[current_func_name+"_err_msg_1"]
        err_msg = unformatted_err_msg.format(output_dirname)
        raise IOError(err_msg)

    return None



def _generate_path_to_new_repo(path_to_directory_to_contain_new_repo,
                               lib_name_for_imports):
    path_to_new_repo = "{}/{}".format(path_to_directory_to_contain_new_repo,
                                      lib_name_for_imports)

    return path_to_new_repo



def _get_pylibtemplate_tag():
    pattern = r"[0-9]\.[0-9]\.[0-9]"
    pylibtemplate_version = __version__    
    pylibtemplate_tag = ("v{}".format(pylibtemplate_version)
                         if re.fullmatch(pattern, pylibtemplate_version)
                         else None)

    return pylibtemplate_tag



def _rm_file_subset_of_local_git_repo(path_to_directory_to_contain_new_repo,
                                      lib_name_for_imports):
    kwargs = {"path_to_directory_to_contain_new_repo": \
              path_to_directory_to_contain_new_repo,
              "lib_name_for_imports": \
              lib_name_for_imports}
    path_to_new_repo = _generate_path_to_new_repo(**kwargs)

    path_to_dir_to_rm = path_to_new_repo + "/.git"
    shutil.rmtree(path_to_dir_to_rm, ignore_errors=True)

    basename = "how_to_create_a_python_library_using_pylibtemplate.rst"
    path_to_file_to_rm = path_to_new_repo + "/docs/" + basename
    os.remove(path_to_file_to_rm)

    return None



def _mv_directory_subset_of_local_git_repo(
        path_to_directory_to_contain_new_repo,
        lib_name_for_imports):
    kwargs = locals()
    path_to_new_repo = _generate_path_to_new_repo(**kwargs)

    os.rename(path_to_new_repo + "/pylibtemplate",
              path_to_new_repo + "/" + lib_name_for_imports)

    return None



def _get_paths_to_files_in_local_git_repo(path_to_directory_to_contain_new_repo,
                                          lib_name_for_imports):
    kwargs = locals()
    path_to_new_repo = _generate_path_to_new_repo(**kwargs)
    
    dir_tree = list(os.walk(path_to_new_repo))

    dirname = os.path.abspath(dir_tree[0][0])
    basename = os.path.basename(dirname)

    filenames = []
    subdirnames = []

    for x in dir_tree:
        subdirname = x[0]
        subdirnames += [subdirname]

        file_basenames = x[2]
        for file_basename in file_basenames:
            filename = subdirname + '/' + file_basename
            filenames += [filename]

        subdirnames.pop(0)

    paths_to_files_in_local_git_repo = filenames

    return paths_to_files_in_local_git_repo



def _replace_and_wrap_text(paths_to_files_in_local_git_repo,
                           text_replacement_map):
    filenames = paths_to_files_in_local_git_repo

    for filename in filenames:
        basename = os.path.basename(filename)

        kwargs = {"filename": filename,
                  "text_replacement_map": text_replacement_map}
        new_file_contents = _generate_new_file_contents(**kwargs)
                            
        with open(filename, "w") as file_obj:
            line_set = new_file_contents
            file_obj.write("\n".join(line_set))

    return None



def _generate_new_file_contents(filename, text_replacement_map):
    with open(filename, "r") as file_obj:
        line_set = file_obj.read().splitlines()
        original_file_contents = line_set

    kwargs = {"line_set_to_modify": original_file_contents,
              "text_replacement_map": text_replacement_map}
    modified_line_set = _apply_text_replacements_to_line_set(**kwargs)
    modified_file_contents = modified_line_set

    kwargs = {"line_set_to_modify": modified_file_contents,
              "filename": filename}
    modified_line_set = _apply_text_wrapping_to_line_set(**kwargs)
    modified_file_contents = modified_line_set

    new_file_contents = modified_file_contents

    return new_file_contents



def _apply_text_replacements_to_line_set(line_set_to_modify,
                                         text_replacement_map):
    modified_line_set = line_set_to_modify.copy()
    for line_idx, line_to_modify in enumerate(line_set_to_modify):
        modified_line = line_to_modify.rstrip()
        for old_substring, new_substring in text_replacement_map.items():
            modified_line = modified_line.replace(old_substring, new_substring)
        modified_line_set[line_idx] = modified_line
        if ((re.fullmatch("=+", modified_line)
             or re.fullmatch("-+", modified_line)
             or re.fullmatch("~+", modified_line))
            and (len(modified_line) > 3)):
            modified_line_set[line_idx] = (modified_line[0]
                                           * len(modified_line_set[line_idx-1]))

    return modified_line_set



def _apply_text_wrapping_to_line_set(line_set_to_modify, filename):
    file_extension = os.path.splitext(filename)[1]

    if file_extension == ".py":
        func_alias = _apply_text_wrapping_to_line_set_of_py_file
    elif file_extension in (".md", ".rst"):
        func_alias = _apply_text_wrapping_to_line_set_of_md_or_rst_file
    elif file_extension == ".sh":
        func_alias = _apply_text_wrapping_to_line_set_of_sh_file

    kwargs = {"line_set_to_modify": line_set_to_modify}
    modified_line_set = (func_alias(**kwargs)
                         if (file_extension in (".py", ".md", ".sh", ".rst"))
                         else line_set_to_modify.copy())

    return modified_line_set



def _apply_text_wrapping_to_line_set_of_py_file(line_set_to_modify):
    modified_line_set = line_set_to_modify.copy()

    pattern_1 = r"#\ ((Copyright)|(For\ setting\ up))\ .*"
    pattern_2 = r"\s*((lib_name)|(project)|(author))\ =\ \".+"
    pattern_3 = r"\s*r\"\"\".+\ ``.+``.+"

    end_of_file_has_not_been_reached = True
    line_idx = 0
    
    while end_of_file_has_not_been_reached:
        modified_line = modified_line_set[line_idx].rstrip()

        if re.fullmatch(pattern_1, modified_line):
            func_alias = _apply_text_wrapping_to_single_line_python_comment
        elif re.fullmatch(pattern_2, modified_line):
            func_alias = _apply_text_wrapping_to_single_line_variable_assignment
        elif re.fullmatch(pattern_3, modified_line):
            func_alias = _apply_text_wrapping_to_single_line_partial_doc_str
        else:
            func_alias = None

        kwargs = {"line_to_modify": modified_line}
        modified_line_subset = ([modified_line]
                                if (func_alias is None)
                                else func_alias(**kwargs))

        modified_line_set = (modified_line_set[:line_idx]
                             + modified_line_subset
                             + modified_line_set[line_idx+1:])
        
        line_idx += len(modified_line_subset)
        if line_idx >= len(modified_line_set):
            end_of_file_has_not_been_reached = False

    return modified_line_set



_char_limit_per_line = 80



def _apply_text_wrapping_to_single_line_python_comment(line_to_modify):
    modified_line = line_to_modify.rstrip()
    
    char_idx = len(modified_line) - len(modified_line.lstrip())
    indent = " "*char_idx
    
    modified_line = modified_line.lstrip()[2:]

    kwargs = {"text": modified_line,
              "width": _char_limit_per_line-char_idx-2,
              "break_long_words": False}
    lines_resulting_from_text_wrapping = textwrap.wrap(**kwargs)
    
    for line_idx, line in enumerate(lines_resulting_from_text_wrapping):
        lines_resulting_from_text_wrapping[line_idx] = indent + "# " + line

    return lines_resulting_from_text_wrapping



def _apply_text_wrapping_to_single_line_variable_assignment(line_to_modify):
    modified_line = line_to_modify.rstrip()

    if len(modified_line) <= _char_limit_per_line:
        lines_resulting_from_text_wrapping = [modified_line]
    else:
        char_idx_1 = modified_line.find("=")
        char_idx_2 = _char_limit_per_line - (char_idx_1+4)
        
        indent = " "*(char_idx_1+3)
        
        modified_line = modified_line[char_idx_1+2:]

        line_resulting_from_text_wrapping = (line_to_modify[:char_idx_1+2]
                                             + "(\""
                                             + modified_line[1:char_idx_2]
                                             + "\"")
        lines_resulting_from_text_wrapping = [line_resulting_from_text_wrapping]

        modified_line = modified_line[char_idx_2:]

        while len(indent+modified_line)+2 > _char_limit_per_line:
            line_resulting_from_text_wrapping = \
                indent + "\"" + modified_line[:char_idx_2-1] + "\""
            lines_resulting_from_text_wrapping += \
                [line_resulting_from_text_wrapping]

            modified_line = modified_line[char_idx_2-1:]

        line_resulting_from_text_wrapping = \
            indent + "\"" + modified_line + ")"
        lines_resulting_from_text_wrapping += \
            [line_resulting_from_text_wrapping]

    return lines_resulting_from_text_wrapping



def _apply_text_wrapping_to_single_line_partial_doc_str(line_to_modify):
    modified_line = line_to_modify.rstrip()
    
    char_idx = len(modified_line) - len(modified_line.lstrip())
    indent = " "*char_idx

    modified_line = line_to_modify.lstrip()

    kwargs = {"text": modified_line,
              "width": _char_limit_per_line - char_idx,
              "break_long_words": False}
    lines_resulting_from_text_wrapping = textwrap.wrap(**kwargs)

    for line_idx, line in enumerate(lines_resulting_from_text_wrapping):
        lines_resulting_from_text_wrapping[line_idx] = indent + line

    return lines_resulting_from_text_wrapping



def _apply_text_wrapping_to_line_set_of_md_or_rst_file(line_set_to_modify):
    modified_line_set = line_set_to_modify.copy()

    pattern_1 = (r"((\[!\[)|(\s+)|(\*\ )|(\-\ \`)|(\.\.\ )|(\{\%)"
                 r"|(\{\{)|(##)|(#\ \-)|(----+)|(====+)|(~~~~+)).*")
    pattern_2 = r"((----+)|(====+)|(~~~~+))"

    end_of_file_has_not_been_reached = True
    line_idx = 1
    
    while end_of_file_has_not_been_reached:
        modified_line_1 = modified_line_set[line_idx].rstrip()

        if (re.fullmatch(pattern_1, modified_line_1)
            or (modified_line_1 in ("", "#"))):
            modified_line_subset = [modified_line_1]
        else:
            end_of_paragraph_has_not_been_reached = True
            
            while end_of_paragraph_has_not_been_reached:
                if line_idx+1 < len(modified_line_set):
                    modified_line_2 = modified_line_set[line_idx+1].rstrip()
                    if (re.fullmatch(pattern_1, modified_line_2)
                        or (modified_line_2 in ("", "#"))):
                        end_of_paragraph_has_not_been_reached = False
                    else:
                        modified_line_1 += " " + modified_line_2.lstrip()
                        modified_line_set.pop(line_idx+1)
                else:
                    end_of_paragraph_has_not_been_reached = False

            if re.fullmatch(pattern_2, modified_line_2):
                modified_line_subset = [modified_line_1]
            else:
                kwargs = {"text": modified_line_1,
                          "width": _char_limit_per_line,
                          "break_long_words": False}
                modified_line_subset = textwrap.wrap(**kwargs)

        modified_line_set = (modified_line_set[:line_idx]
                             + modified_line_subset
                             + modified_line_set[line_idx+1:])

        line_idx += len(modified_line_subset)
        if line_idx >= len(modified_line_set):
            end_of_file_has_not_been_reached = False

    lines_resulting_from_text_wrapping = modified_line_set

    return lines_resulting_from_text_wrapping



def _apply_text_wrapping_to_line_set_of_sh_file(line_set_to_modify):
    modified_line_set = line_set_to_modify.copy()

    pattern = r"#\ .+"

    end_of_file_has_not_been_reached = True
    line_idx = 2
    
    while end_of_file_has_not_been_reached:
        modified_line_1 = modified_line_set[line_idx].rstrip()

        if re.fullmatch(pattern, modified_line_1):
            prefix = "# "
            end_of_paragraph_has_not_been_reached = True
            
            while end_of_paragraph_has_not_been_reached:
                modified_line_2 = modified_line_set[line_idx+1].rstrip()
                if re.fullmatch(pattern, modified_line_2):
                    modified_line_1 += " " + modified_line_2.lstrip(prefix)
                    modified_line_set.pop(line_idx+1)
                else:
                    end_of_paragraph_has_not_been_reached = False

            kwargs = {"text": modified_line_1,
                      "width": _char_limit_per_line,
                      "subsequent_indent": prefix,
                      "break_long_words": False}
            modified_line_subset = textwrap.wrap(**kwargs)
        else:
            modified_line_subset = [modified_line_1]

        modified_line_set = (modified_line_set[:line_idx]
                             + modified_line_subset
                             + modified_line_set[line_idx+1:])

        line_idx += len(modified_line_subset)
        if line_idx >= len(modified_line_set):
            end_of_file_has_not_been_reached = False

    lines_resulting_from_text_wrapping = modified_line_set

    return lines_resulting_from_text_wrapping



def _print_generate_local_git_repo_template_end_msg(
        start_time,
        path_to_directory_to_contain_new_repo,
        lib_name_for_imports):
    elapsed_time = time.time() - start_time
    path_to_local_git_repo_template = (path_to_directory_to_contain_new_repo
                                       + "/"
                                       + lib_name_for_imports)

    unformatted_msg = ("Finished generating the local ``git`` repository, "
                       "which is located at the path ``'{}'``. Time taken to "
                       "generate the local ``git`` repository: {} "
                       "s.\n\n\n")
    msg = unformatted_msg.format(path_to_local_git_repo_template,
                                 elapsed_time)
    print(msg)

    return None



def _run_pylibtemplate_as_an_app(cmd_line_args=None):
    converted_cmd_line_args = _parse_and_convert_cmd_line_args(cmd_line_args)

    kwargs = converted_cmd_line_args
    generate_local_git_repo_template(**kwargs)

    return None



def _parse_and_convert_cmd_line_args(cmd_line_args):
    arg_names = ("lib_name_for_imports",
                 "abbreviated_lib_name_for_docs",
                 "non_abbreviated_lib_name_for_docs",
                 "author",
                 "email",
                 "gist_id",
                 "path_to_directory_to_contain_new_repo")

    parser = argparse.ArgumentParser()

    global_symbol_table = globals()
    for arg_name in arg_names:
        obj_name = "_default_" + arg_name
        default_arg_val = global_symbol_table[obj_name]
            
        arg_type = type(default_arg_val)

        parser.add_argument("--"+arg_name,
                            default=default_arg_val,
                            type=arg_type)

    current_func_name = "_parse_and_convert_cmd_line_args"

    try:    
        args = parser.parse_args(args=cmd_line_args)
    except:
        err_msg = globals()[current_func_name+"_err_msg_1"]
        raise SystemExit(err_msg)

    converted_cmd_line_args = dict()
    for arg_name in arg_names:
        converted_cmd_line_args[arg_name] = getattr(args, arg_name)
    
    return converted_cmd_line_args



###########################
## Define error messages ##
###########################

_check_and_convert_lib_name_for_imports_err_msg_1 = \
    ("The object ``lib_name_for_imports`` must be a string that is a valid "
     "identifier.")

_check_and_convert_abbreviated_lib_name_for_docs_err_msg_1 = \
    _check_and_convert_lib_name_for_imports_err_msg_1

_make_output_dir_err_msg_1 = \
    ("An error occurred in trying to make the directory ``'{}'``: see "
     "traceback for details.")

_clone_pylibtemplate_repo_err_msg_1 = \
    ("An error occurred while trying to clone the ``pylibtemplate`` "
     "repository: see the traceback for details.")

_parse_and_convert_cmd_line_args_err_msg_1 = \
    ("The correct form of the command is:\n"
     "\n"
     "    pylibtemplate "
     "--lib_name_for_imports="
     "<lib_name_for_imports> "
     "--abbreviated_lib_name_for_docs="
     "<abbreviated_lib_name_for_docs> "
     "--non_abbreviated_lib_name_for_docs="
     "<non_abbreviated_lib_name_for_docs> "
     "--author="
     "<author> "
     "--email="
     "<email> "
     "--gist_id="
     "<gist_id> "
     "--path_to_directory_to_contain_new_repo="
     "<path_to_directory_to_contain_new_repo>\n"
     "\n"
     "where the command line arguments are the same as the parameters of the "
     "function ``pylibtemplate.generate_local_git_repo_template``. For "
     "details, see the documentation for the libary ``pylibtemplate`` via the "
     "link https://mrfitzpa.github.io/pylibtemplate, and navigate the "
     "reference guide for the version of the library that is installed.")



#########################
## Main body of script ##
#########################

_ = (_run_pylibtemplate_as_an_app()
     if (__name__ == "__main__")
     else None)
