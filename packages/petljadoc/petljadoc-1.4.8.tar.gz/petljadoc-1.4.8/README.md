# PetljaDoc - Petlja's tool for eLearning content

The tool is based on https://github.com/RunestoneInteractive/RunestoneComponents and https://github.com/sphinx-doc/sphinx and includes:

- additional Sphinx extensions
- partial Pygame implementation for Sculpt (https://github.com/Petlja/pygame4skulpt)
- additional ActiveCode features
- customized Sphinx theme
- customized project template
- exteded online course format
- ``petljadoc`` command line interface (CLI)

PetljaDoc currently depends on forked RunestoneComonents, but we are gradually closing the gap with the upstream repository through pull requests.

## Installation

Use `pip` to `install` PetljaDoc:

`pip3 install petljadoc`

If you use Windows and previous command does not work, try:

`py -3 -m pip install petljadoc`

## CLI usage

`petljadoc [OPTIONS] COMMAND [ARGS]...`

Options:

- `--help`&nbsp;&nbsp;&nbsp;&nbsp;Show help message

Commands:

- `init-course`&nbsp;&nbsp;&nbsp;&nbsp;Create a new online course project in your current directory
- `init-runestone`&nbsp;&nbsp;&nbsp;&nbsp;Create a new Runestone project in your current directory
- `preview`&nbsp;&nbsp;&nbsp;&nbsp;Build the project, open it in a web browser, watch for changes, rebuild changed files and refresh browser after rebuild (using [sphinx-autobuild](https://github.com/GaretJax/sphinx-autobuild))
- `publish`&nbsp;&nbsp;&nbsp;&nbsp;Build the project and copy produced content in `docs` subfolder (ready to be published using GitHub Pages)
- `export`&nbsp;&nbsp;&nbsp; &nbsp;Builds the project and exports its content as a SCORM package. You can select one of the 3 options with will deliver you diffrent type of packages:
  - `single`: A single SCO (Shareable Content Object) SCORM package, which contains all course content in a single file
  - `multi`: A multi SCO SCORM package, which breaks the course content into multiple modules or units
  - `proxy`: A proxy SCORM package, that can be used with a Learning Management System (LMS) and an additional Moodle backup file. This option requires you to upload your course files to a web server and provide a link to the packager via `package-conf.json`. We recommend to upload your course files to a web server like GitHub Pages, which allows you to host static web content for free. You can create a new repository for your course files and enable GitHub Pages to generate a website URL for your repository. Then, you can update `package-conf.json` to include the GitHub Pages URL as the `data_content_url` property.

By using `petljadoc preview`, an author may keep opened a browser window for preview. Any saved changes will be updated in browser in about 5-10 seconds.

`petljadoc publish` command helps an author to share a public preview of his work via GitHub Pages.
