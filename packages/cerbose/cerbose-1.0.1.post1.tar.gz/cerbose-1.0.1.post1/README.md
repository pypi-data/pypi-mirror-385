![Cerbose Logo](.readme/logo.png)
<p align="center">
  <img alt="Language: Python" src="https://img.shields.io/badge/Language-Python-purple?style=flat-square">
  <img alt="Version: 1.0.1" src="https://img.shields.io/badge/Version-1.0.1-green?style=flat-square">
  <img alt="Devlopment Stage: Early Beta" src="https://img.shields.io/badge/Development_Stage-Early_Beta-orange?style=flat-square">
  <img alt="License: LGPLv3" src="https://img.shields.io/badge/License-LGPLv3-blue?style=flat-square">
  <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square"><br>
  Cerbose is a simple, cross-platform Python library, mainly for making tagged, colourful console output along with additional features.<br>
  <a href="https://jasperredis.github.io/cerbose">Website</a> |
  <a href="https://pypi.org/project/cerbose">PyPI</a> |
  <a href="https://jris.straw.page">jasperredis</a><br>
  Made by jasperredis [o]:
  <br><br>
  It is highly reccomended to check <a href="https://jasperredis.github.io/cerbose">the website.</a>
</p>

---
![Test Preview Image](.readme/test.png)
> This wasn't done in a codeblock because they can't display colours.

- For contributing, see CONTRIBUTING.md on the GitHub repo.
- For the changelog, see CHANGELOG.md on the GitHub repo.

# Functions
## cprint
This is the highlight function of Cerbose. It outputs highly configurable tagged text to the console, and you can configure the following:
- Tag (obviously)
- Text (obviously)
- Logging (enabled, file, and optional feedback)
- Text colour
- Dual tags
- Timestamp (enabled?)
- And more through configuration files.  

It also has a "valonly" mode where it returns the suppposed output instead of printing it.  
More info in [the documentation](docs/DOCS.md).

## mprint
The same as cprint, except it has multiline support.

## cerbar
Returns an ASCII progress bar. You can configure the following:
- Length in characters
- Value being represented (obviously) in regular integers, not percentages.
- Optionally add the percentage represented be before/after the progress bar.
- Optionally add the amount represented (fill/total) before/after the progress bar.
- And more through configuration files.  

More info in [the documentation](docs/DOCS.md).

## cin
Takes user input and returns the input. You can configure the following:
- Prompt (obviously)
- All options for `cprint` in the prompt.
- 'i' and 'o' mode. 'i' allows any text input (remember to set options to 'any'!), and 'o' has a strict set of options.
- Recieving user input as lowercase (enabled?)

More info in [the documentation](docs/DOCS.md).

# Configuration
Cerbose can be more highly configured via config files. As always, [the documentation](docs/DOCS.md) has the best information on this, but here is roughly what you can configure with these:
- Tag colours
- Tag text
- Symbols (brackets, cerbar contents, etc.)
- Timestamp format
- Space repeat tolerance (check [documentation](docs/DOCS.md))

Cerbose config files are in JSON format.

# Licensing
Always, for more information related to licenses in Cerbose, check the [LICENSE](LICENSE) file in the project root and the files it refers to.

- Cerbose, the Python script itself, is licensed under the GNU Lesser General Public License v3.0 or later. What constitutes as the script itself is any file in the src/ directory of this repository.
  + See the [LICENSE-LGPL](LICENSE-LGPL) file for more info.
  + The LGPLv3 is an extension of the GNU General Public License v3. See the [LICENSE-GPL](LICENSE-GPL) file for more info.
- All other files, with reasonable exception of license-related files (e.g., docs, examples) are under the MIT License.
  + See the [LICENSE-MIT](LICENSE-MIT) file for more info.

**REMINDER**: The best source of information in Cerbose (and most other projects you will encounter) is the [LICENSE](LICENSE) file at the project root.

<h2 align="center">
  Primarily made by:<br><br>
  <img alt="jasperredis" src=".readme/jrisbanner.png">
</h2>
