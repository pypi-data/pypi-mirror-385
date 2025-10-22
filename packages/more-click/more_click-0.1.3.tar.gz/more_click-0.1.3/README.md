<!--
<p align="center">
  <img src="https://github.com/cthoyt/more-click/raw/main/docs/source/logo.png" height="150">
</p>
-->

<h1 align="center">
  More Click
</h1>

<p align="center">
    <a href="https://github.com/cthoyt/more-click/actions/workflows/tests.yml">
        <img alt="Tests" src="https://github.com/cthoyt/more-click/actions/workflows/tests.yml/badge.svg" /></a>
    <a href="https://pypi.org/project/more_click">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/more_click" /></a>
    <a href="https://pypi.org/project/more_click">
        <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/more_click" /></a>
    <a href="https://github.com/cthoyt/more-click/blob/main/LICENSE">
        <img alt="PyPI - License" src="https://img.shields.io/pypi/l/more_click" /></a>
    <a href='https://more_click.readthedocs.io/en/latest/?badge=latest'>
        <img src='https://readthedocs.org/projects/more_click/badge/?version=latest' alt='Documentation Status' /></a>
    <a href="https://codecov.io/gh/cthoyt/more-click/branch/main">
        <img src="https://codecov.io/gh/cthoyt/more-click/branch/main/graph/badge.svg" alt="Codecov status" /></a>  
    <a href="https://github.com/cthoyt/cookiecutter-python-package">
        <img alt="Cookiecutter template from @cthoyt" src="https://img.shields.io/badge/Cookiecutter-snekpack-blue" /></a>
    <a href="https://github.com/astral-sh/ruff">
        <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff" style="max-width:100%;"></a>
    <a href="https://github.com/cthoyt/more-click/blob/main/.github/CODE_OF_CONDUCT.md">
        <img src="https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg" alt="Contributor Covenant"/></a>
    <!-- uncomment if you archive on zenodo
    <a href="https://zenodo.org/badge/latestdoi/XXXXXX">
        <img src="https://zenodo.org/badge/XXXXXX.svg" alt="DOI"></a>
    -->
</p>

Implementations of common CLI patterns on top of Click.

## 💪 Getting Started

The module `more_click.options` has several options (pre-defined instances of
`click.option()`) that I use often. First, `verbose_option` makes it easy to
adjust the logger of your package using `-v`.

There are also several that are useful for web stuff, including

| Name                     | Type | Flag     |
| ------------------------ | ---- | -------- |
| `more_click.host_option` | str  | `--host` |
| `more_click.port_option` | str  | `--port` |

### Web Tools

In many packages, I've included a Flask web application in `wsgi.py`. I usually
use the following form inside `cli.py` file to import the web application and
keep it insulated from other package-related usages:

```python
# cli.py
import click
from more_click import host_option, port_option


@click.command()
@host_option
@port_option
def web(host: str, port: str):
    from .wsgi import app  # modify to point to your module-level `flask.Flask` instance
    app.run(host=host, port=port)


if __name__ == '__main__':
    web()
```

However, sometimes I want to make it possible to run via `gunicorn` from the
CLI, so I would use the following extensions to automatically determine if it
should be run with Flask's development server or gunicorn.

```python
# cli.py
import click
from more_click import host_option, port_option, with_gunicorn_option, workers_option, run_app


@click.command()
@host_option
@port_option
@with_gunicorn_option
@workers_option
def web(host: str, port: str, with_gunicorn: bool, workers: int):
    from .wsgi import app  # modify to point to your module-level `flask.Flask` instance
    run_app(app=app, with_gunicorn=with_gunicorn, host=host, port=port, workers=workers)


if __name__ == '__main__':
    web()
```

For ultimate lazy mode, I've written a wrapper around the second:

```python
# cli.py
from more_click import make_web_command

web = make_web_command('my_package_name.wsgi:app')

if __name__ == '__main__':
    web()
```

This uses a standard `wsgi`-style string to locate the app, since you don't want
to be eagerly importing the app in your CLI since it might rely on optional
dependencies like Flask. If your CLI has other stuff, you can include the web
command in a group like:

```python
# cli.py
import click
from more_click import make_web_command


@click.group()
def main():
    """My awesome CLI."""


make_web_command('my_package_name.wsgi:app', group=main)

if __name__ == '__main__':
    main()
```

## 🚀 Installation

The most recent release can be installed from
[PyPI](https://pypi.org/project/more_click/) with uv:

```console
$ uv pip install more_click
```

or with pip:

```console
$ python3 -m pip install more_click
```

The most recent code and data can be installed directly from GitHub with uv:

```console
$ uv pip install git+https://github.com/cthoyt/more-click.git
```

or with pip:

```console
$ python3 -m pip install git+https://github.com/cthoyt/more-click.git
```

## 👐 Contributing

Contributions, whether filing an issue, making a pull request, or forking, are
appreciated. See
[CONTRIBUTING.md](https://github.com/cthoyt/more-click/blob/master/.github/CONTRIBUTING.md)
for more information on getting involved.

## 👋 Attribution

### ⚖️ License

The code in this package is licensed under the MIT License.

<!--
### 📖 Citation

Citation goes here!
-->

<!--
### 🎁 Support

This project has been supported by the following organizations (in alphabetical order):

- [Biopragmatics Lab](https://biopragmatics.github.io)

-->

<!--
### 💰 Funding

This project has been supported by the following grants:

| Funding Body  | Program                                                      | Grant Number |
|---------------|--------------------------------------------------------------|--------------|
| Funder        | [Grant Name (GRANT-ACRONYM)](https://example.com/grant-link) | ABCXYZ       |
-->

### 🍪 Cookiecutter

This package was created with
[@audreyfeldroy](https://github.com/audreyfeldroy)'s
[cookiecutter](https://github.com/cookiecutter/cookiecutter) package using
[@cthoyt](https://github.com/cthoyt)'s
[cookiecutter-snekpack](https://github.com/cthoyt/cookiecutter-snekpack)
template.

## 🛠️ For Developers

<details>
  <summary>See developer instructions</summary>

The final section of the README is for if you want to get involved by making a
code contribution.

### Development Installation

To install in development mode, use the following:

```console
$ git clone git+https://github.com/cthoyt/more-click.git
$ cd more-click
$ uv pip install -e .
```

Alternatively, install using pip:

```console
$ python3 -m pip install -e .
```

### 🥼 Testing

After cloning the repository and installing `tox` with
`uv tool install tox --with tox-uv` or `python3 -m pip install tox tox-uv`, the
unit tests in the `tests/` folder can be run reproducibly with:

```console
$ tox -e py
```

Additionally, these tests are automatically re-run with each commit in a
[GitHub Action](https://github.com/cthoyt/more-click/actions?query=workflow%3ATests).

### 📖 Building the Documentation

The documentation can be built locally using the following:

```console
$ git clone git+https://github.com/cthoyt/more-click.git
$ cd more-click
$ tox -e docs
$ open docs/build/html/index.html
```

The documentation automatically installs the package as well as the `docs` extra
specified in the [`pyproject.toml`](pyproject.toml). `sphinx` plugins like
`texext` can be added there. Additionally, they need to be added to the
`extensions` list in [`docs/source/conf.py`](docs/source/conf.py).

The documentation can be deployed to [ReadTheDocs](https://readthedocs.io) using
[this guide](https://docs.readthedocs.io/en/stable/intro/import-guide.html). The
[`.readthedocs.yml`](.readthedocs.yml) YAML file contains all the configuration
you'll need. You can also set up continuous integration on GitHub to check not
only that Sphinx can build the documentation in an isolated environment (i.e.,
with `tox -e docs-test`) but also that
[ReadTheDocs can build it too](https://docs.readthedocs.io/en/stable/pull-requests.html).

</details>

## 🧑‍💻 For Maintainers

<details>
  <summary>See maintainer instructions</summary>

### Initial Configuration

#### Configuring ReadTheDocs

[ReadTheDocs](https://readthedocs.org) is an external documentation hosting
service that integrates with GitHub's CI/CD. Do the following for each
repository:

1. Log in to ReadTheDocs with your GitHub account to install the integration at
   https://readthedocs.org/accounts/login/?next=/dashboard/
2. Import your project by navigating to https://readthedocs.org/dashboard/import
   then clicking the plus icon next to your repository
3. You can rename the repository on the next screen using a more stylized name
   (i.e., with spaces and capital letters)
4. Click next, and you're good to go!

#### Configuring Archival on Zenodo

[Zenodo](https://zenodo.org) is a long-term archival system that assigns a DOI
to each release of your package. Do the following for each repository:

1. Log in to Zenodo via GitHub with this link:
   https://zenodo.org/oauth/login/github/?next=%2F. This brings you to a page
   that lists all of your organizations and asks you to approve installing the
   Zenodo app on GitHub. Click "grant" next to any organizations you want to
   enable the integration for, then click the big green "approve" button. This
   step only needs to be done once.
2. Navigate to https://zenodo.org/account/settings/github/, which lists all of
   your GitHub repositories (both in your username and any organizations you
   enabled). Click the on/off toggle for any relevant repositories. When you
   make a new repository, you'll have to come back to this

After these steps, you're ready to go! After you make "release" on GitHub (steps
for this are below), you can navigate to
https://zenodo.org/account/settings/github/repository/cthoyt/more-click to see
the DOI for the release and link to the Zenodo record for it.

#### Registering with the Python Package Index (PyPI)

The [Python Package Index (PyPI)](https://pypi.org) hosts packages so they can
be easily installed with `pip`, `uv`, and equivalent tools.

1. Register for an account [here](https://pypi.org/account/register)
2. Navigate to https://pypi.org/manage/account and make sure you have verified
   your email address. A verification email might not have been sent by default,
   so you might have to click the "options" dropdown next to your address to get
   to the "re-send verification email" button
3. 2-Factor authentication is required for PyPI since the end of 2023 (see this
   [blog post from PyPI](https://blog.pypi.org/posts/2023-05-25-securing-pypi-with-2fa/)).
   This means you have to first issue account recovery codes, then set up
   2-factor authentication
4. Issue an API token from https://pypi.org/manage/account/token

This only needs to be done once per developer.

#### Configuring your machine's connection to PyPI

This needs to be done once per machine.

```console
$ uv tool install keyring
$ keyring set https://upload.pypi.org/legacy/ __token__
$ keyring set https://test.pypi.org/legacy/ __token__
```

Note that this deprecates previous workflows using `.pypirc`.

### 📦 Making a Release

#### Uploading to PyPI

After installing the package in development mode and installing `tox` with
`uv tool install tox --with tox-uv` or `python3 -m pip install tox tox-uv`, run
the following from the console:

```console
$ tox -e finish
```

This script does the following:

1. Uses [bump-my-version](https://github.com/callowayproject/bump-my-version) to
   switch the version number in the `pyproject.toml`, `CITATION.cff`,
   `src/more_click/version.py`, and [`docs/source/conf.py`](docs/source/conf.py)
   to not have the `-dev` suffix
2. Packages the code in both a tar archive and a wheel using
   [`uv build`](https://docs.astral.sh/uv/guides/publish/#building-your-package)
3. Uploads to PyPI using
   [`uv publish`](https://docs.astral.sh/uv/guides/publish/#publishing-your-package).
4. Push to GitHub. You'll need to make a release going with the commit where the
   version was bumped.
5. Bump the version to the next patch. If you made big changes and want to bump
   the version by minor, you can use `tox -e bumpversion -- minor` after.

#### Releasing on GitHub

1. Navigate to https://github.com/cthoyt/more-click/releases/new to draft a new
   release
2. Click the "Choose a Tag" dropdown and select the tag corresponding to the
   release you just made
3. Click the "Generate Release Notes" button to get a quick outline of recent
   changes. Modify the title and description as you see fit
4. Click the big green "Publish Release" button

This will trigger Zenodo to assign a DOI to your release as well.

### Updating Package Boilerplate

This project uses `cruft` to keep boilerplate (i.e., configuration, contribution
guidelines, documentation configuration) up-to-date with the upstream
cookiecutter package. Install cruft with either `uv tool install cruft` or
`python3 -m pip install cruft` then run:

```console
$ cruft update
```

More info on Cruft's update command is available
[here](https://github.com/cruft/cruft?tab=readme-ov-file#updating-a-project).

</details>
