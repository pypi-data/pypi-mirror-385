# Python Library Template (PyLibTemplate)

[![Test library](https://github.com/mrfitzpa/pylibtemplate/actions/workflows/test_library.yml/badge.svg)](https://github.com/mrfitzpa/pylibtemplate/actions/workflows/test_library.yml)
[![Code Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/mrfitzpa/7baba2a56d07b59cc49b8323f44416e5/raw/pylibtemplate_coverage_badge.json)](https://github.com/mrfitzpa/pylibtemplate/actions/workflows/measure_code_coverage.yml)
[![Documentation](https://img.shields.io/badge/docs-read-brightgreen)](https://mrfitzpa.github.io/pylibtemplate)
[![PyPi Version](https://img.shields.io/pypi/v/pylibtemplate.svg)](https://pypi.org/project/pylibtemplate)
[![Conda-Forge Version](https://img.shields.io/conda/vn/conda-forge/pylibtemplate.svg)](https://anaconda.org/conda-forge/pylibtemplate)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

`pylibtemplate` (short for 'Python Library Template') is a Python library that
generates `git` repository templates for building Python libraries that are
suitable for publication on PyPI.

Visit the `pylibtemplate` [website](https://mrfitzpa.github.io/pylibtemplate)
for a web version of the installation instructions, the reference guide, and the
examples archive.



## Table of contents

- [Instructions for installing and uninstalling
  `pylibtemplate`](#instructions-for-installing-and-uninstalling-pylibtemplate)
  - [Installing `pylibtemplate`](#installing-pylibtemplate)
    - [Installing `pylibtemplate` using
      `pip`](#installing-pylibtemplate-using-pip)
    - [Installing `pylibtemplate` using
      `conda`](#installing-pylibtemplate-using-conda)
  - [Uninstalling `pylibtemplate`](#uninstalling-pylibtemplate)
- [How to create a Python library using `pylibtemplate`](#how-to-create-a-python-library-using-pylibtemplate)
  - [Create a new empty GitHub repository for your new Python library](#create-a-new-empty-github-repository-for-your-new-python-library)
  - [Create a new GitHub gist for your new Python library](#create-a-new-github-gist-for-your-new-python-library)
  - [Create a new GitHub token for your new Python library](#create-a-new-github-token-for-your-new-python-library)
  - [Create a new GitHub environment for your new Python library](#create-a-new-github-environment-for-your-new-python-library)
  - [Configure GitHub Pages for your new Python library](#configure-github-pages-for-your-new-python-library)
  - [Create local `git` repository template using `pylibtemplate`](#create-local-git-repository-template-using-pylibtemplate)
  - [Add GitHub remote repository to local `git` repository](#add-github-remote-repository-to-local-git-repository)
  - [Modify local repository files](#modify-local-repository-files)



## Instructions for installing and uninstalling `pylibtemplate`



### Installing `pylibtemplate`

For all installation scenarios, first open up the appropriate command line
interface. On Unix-based systems, you could open e.g. a terminal. On Windows
systems you could open e.g. an Anaconda Prompt as an administrator.



#### Installing `pylibtemplate` using `pip`

Before installing `pylibtemplate`, make sure that you have activated the
(virtual) environment in which you intend to install said package. After which,
simply change into the root of the repository, and run the following command:

    pip install pylibtemplate

The above command will install the latest stable version of `pylibtemplate`.

To install the latest development version from the main branch of the
[pylibtemplate GitHub repository](https://github.com/mrfitzpa/pylibtemplate),
one must first clone the repository by running the following command:

    git clone https://github.com/mrfitzpa/pylibtemplate.git

Next, change into the root of the cloned repository, and then run the following
command:

    pip install .

Note that you must include the period as well. The above command executes a
standard installation of `pylibtemplate`.

Optionally, for additional features in `pylibtemplate`, one can install
additional dependencies upon installing `pylibtemplate`. To install a subset of
additional dependencies (along with the standard installation), run the
following command from the root of the repository:

    pip install .[<selector>]

where `<selector>` can be one of the following:

* `tests`: to install the dependencies necessary for running unit tests;
* `examples`: to install the dependencies necessary for executing files stored
  in `<root>/examples`, where `<root>` is the root of the repository;
* `docs`: to install the dependencies necessary for documentation generation;
* `all`: to install all of the above optional dependencies.

Alternatively, one can run:

    pip install pylibtemplate[<selector>]

elsewhere in order to install the latest stable version of `pylibtemplate`,
along with the subset of additional dependencies specified by `<selector>`.



#### Installing `pylibtemplate` using `conda`

To install `pylibtemplate` using the `conda` package manager, run the following
command:

    conda install -c conda-forge pylibtemplate

The above command will install the latest stable version of `pylibtemplate`.



### Uninstalling `pylibtemplate`

If `pylibtemplate` was installed using `pip`, then to uninstall, run the
following command from the root of the repository:

    pip uninstall pylibtemplate

If `pylibtemplate` was installed using `conda`, then to uninstall, run the
following command from the root of the repository:

    conda remove pylibtemplate



## How to create a Python library using `pylibtemplate`

The following instructions assume that the reader understands completely the
purpose of each file in the [`pylibtemplate` GitHub
repository](https://github.com/mrfitzpa/pylibtemplate), in relation to the
corresponding Python library `pylibtemplate`.



### Create a new empty GitHub repository for your new Python library

Before generating your `git` repository template for building your new Python
library, several other actions need to be performed, the first of which is to
create a new empty public GitHub repository, which will serve as the remote
repository for your new Python library. The GitHub repository should share the
same name as your new Python library, as it would appear in a `pip install`
command. We will refer to the name of your new Python library as
`<your_lib_name>`.



### Create a new GitHub gist for your new Python library

We need to create a new GitHub gist that will be used to record the code
coverage from your unit tests. To create a new gist, first go to
[https://gist.github.com](https://gist.github.com). Next, in the field
containing the placeholder text "Gist description" write:

    To store the code coverage of the `<your_lib_name>` library.

Next, in the field containing the placeholder text "Filename including
extension...", write:

    <your_lib_name>_coverage_badge.json

Next, in the field directly below --- where the gist contents are suppose to be
written --- write:

    {}

Next, click on the green down arrow button in the bottom right corner, select
the "Create public gist" option, and then click the "Create public gist" button.

Upon creating the new gist, you will be redirected to a new page that presents
the gist. Copy or save somewhere the string of characters following the last `/`
in the URL of said page. This string of characters is the ID of the gist that
you just created. We will refer to the gist ID as `<your_gist_id>`.



### Create a new GitHub token for your new Python library

Next, we need to create a new GitHub token with gist scope. To do this, first go
to
[https://github.com/settings/tokens](https://github.com/settings/tokens). Next,
click on the button "Generate new token" and select the "Generate new token
(classic)" option. Next, in the field directly below "Note", write:

    To access the `<your_lib_name>` code coverage file.

Next, in the field directly below "Expiration", select whatever expiration date
that you prefer. Next, select the "gist" box amongst the options of scope. Next,
click on the "Generate token" button. Next, copy or save somewhere the personal
access token that appears on the current page. We will refer to the personal
access token as `<your_access_token>`. Next, go to the main page of the
`<your_lib_name>` GitHub repository. Next, click on "Settings", then "Secrets
and variables" in the side menu that appears, followed by "Actions" in the
sub-menu. Next, click on the "New repository secret" button. In the field
containing the placeholder text "YOUR_SECRET_NAME", write:

    CODE_COVERAGE_SECRET

In the field directly below "Secret *", copy and paste `<your_access_token>`.



### Create a new GitHub environment for your new Python library

In order to add your GitHub repository as a pending publisher on PyPI, you need
to create a specific GitHub environment for said repository. To do this, first
go to the main page of the `<your_lib_name>` GitHub repository. Next, click on
"Settings", then "Environments" in the side menu that appears. Next, click on
the "New environment" button. In the field directly below "Name *", write:

    release

and then click on the "Configure environment" button.



### Configure GitHub Pages for your new Python library

Next, we need to configure the GitHub Pages for you new Python library. To do
this, first go to the main page of the `<your_lib_name>` GitHub
repository. Next, click on "Settings", then "Pages" in the side menu that
appears. In the field directly below "Source", select "GitHub Actions".



### Create local `git` repository template using `pylibtemplate`

Next, we need to create a local `git` repository template using
`pylibtemplate`. To do this, activate an environment in which `pylibtemplate` is
installed, and then execute the following Python code block:

    import pylibtemplate

    kwargs = {"lib_name_for_imports": \
              <your_lib_name>,
              "abbreviated_lib_name_for_docs": \
              <your_abbreviated_lib_name_for_docs>,
              "non_abbreviated_lib_name_for_docs": \
              <your_non_abbreviated_lib_name_for_docs>,
              "author": \
              <author>,
              "email": \
              <email>,
              "gist_id": \
              <your_gist_id>,
              "path_to_directory_to_contain_new_repo": \
              <path_to_directory_to_contain_new_repo>}
    pylibtemplate.generate_local_git_repo_template(**kwargs)

This code block will perform several actions: First, it will clone the `git`
commit of the `pylibtemplate` GitHub repository corresponding to the version of
`pylibtemplate` being used currently, in the directory at the patth
`<path_to_directory_to_contain_new_repo>`, i.e. the `git clone` command is
executed while the working directory is set temporarily to the path
`path_to_directory_to_contain_new_repo`; Next, it will rename the cloned
repository to `<your_lib_name>` such that the path to the cloned repository
becomes `<path_to_directory_to_contain_new_repo>/<your_lib_name>`; Next, all
instances of the string of characters "pylibtemplate" are replaced with
`<your_lib_name>`, be it in file contents, directory basenames, or file
basenames; Next, all instances of the string of characters "PyLibTemplate" are
replaced with `<your_abbreviated_lib_name_for_docs>`; Next, all instances of the
string of characters "Python Library Template" are replaced with
`<your_non_abbreviated_lib_name_for_docs>`; Next, all email address placeholders
(i.e. instances of the string of characters "matthew.rc.fitzpatrick@gmail.com")
are replaced with `<email>`; Next, all instances of the gist ID of
`pylibtemplate` are replaced with `<your_gist_id>`; Next, all author
placeholders (i.e. instances of the string of characters "Matthew Fitzpatrick")
are replaced with `<author>`; Next, all copyright statements are updated
according to the current year; And lastly, the following file is removed:

- `<local_repo_root>/docs/how_to_create_a_python_library_using_pylibtemplate.rst`

where `<local_repo_root>` is the root of the local ``git`` repository, as well
as the following directory:

- `<local_repo_root>/.git`

Instead of executing the above Python code block, one can achieve the same
result by running `pylibtemplate` as a command line too. To do this, activate an
environment in which `pylibtemplate` is installed, and then execute the
following command in the terminal:

    pylibtemplate --lib_name_for_imports=<your_lib_name> --abbreviated_lib_name_for_docs=<your_abbreviated_lib_name_for_docs> --non_abbreviated_lib_name_for_docs=<your_non_abbreviated_lib_name_for_docs> --author=<author> --email=<email> --gist_id=<your_gist_id> --path_to_directory_to_contain_new_repo=<path_to_directory_to_contain_new_repo>



### Add GitHub remote repository to local `git` repository

Once you have created your local `git` repository template, you should add to it
the GitHub repository that you created in the very first step above. To do this,
run the following commands in a terminal:

    git init
    git remote add origin https://github.com/<your_username>/<your_lib_name>.git
    git branch -M main
    git push -u origin main

where `<your_username>` is the name of the GitHub user that created the GitHub
repository.



### Modify local repository files

Of course, now you must modify the local `git` repository files in order to
develop your new Python library.

The following files do not need to be modified under any circumstances:

* `<local_repo_root>/.coveragerc`
* `<local_repo_root>/tox.ini`
* `<local_repo_root>/docs/Makefile`
* `<local_repo_root>/docs/make.bat`
* `<local_repo_root>/docs/api.rst`
* `<local_repo_root>/docs/private_members_to_publish_to_docs.rst`

The following files may need to be modified to reflect the appropriate license
should it differ from that of `pylibtemplate`:

* `<local_repo_root>/run_tests.sh`
* `<local_repo_root>/setup.py`
* `<local_repo_root>/LICENSE`
* `<local_repo_root>/docs/license.rst`
* `<local_repo_root>/docs/build_docs.py`

The following files may need to be modified if a custom installation procecdure
is required to run your new Python library's unit tests, that differs from the
default installation procedure:

* `<local_repo_root>/.github/workflows/measure_code_coverage.yml`
* `<local_repo_root>/.github/workflows/test_library.yml`
* `<local_repo_root>/.github/workflows/publish_documentation_website.yml`
* `<local_repo_root>/.github/workflows/publish_release_to_pypi.yml`

The following files need to be modified according to the specifics of your new
Python library:

* `<local_repo_root>/README.md`
* `<local_repo_root>/pyproject.toml`
* `<local_repo_root>/.gitignore`
* `<local_repo_root>/docs/INSTALL.rst`
* `<local_repo_root>/docs/conf.py`
* `<local_repo_root>/docs/index.rst`
* `<local_repo_root>/docs/literature.rst`
* `<local_repo_root>/docs/examples.rst`

as well as the files stored in the directories:

* `<local_repo_root>/<your_lib_name>`
* `<local_repo_root>/tests`
* `<local_repo_root>/examples`
* `<local_repo_root>/docs/examples`

After making the necessary modifications, you can proceed to test and debug your
new Python library.