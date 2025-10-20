## [v1.0.3] - 2025-10-19

Release Type: minor

### 📋 Summary 
- New documentation site [Bayescalc2 Documentation](https://johan162.github.io/bayescalc2/) together with generic documentation updates. 

### ✨ Additions
- New documentation site built with MkDocs (https://www.mkdocs.org/)

### 🛠 Internal
- Fix GitHub Release Creation Script o handle naming of pre-releases
- Added `mkdocs.sh` documentation build and deploy script
- Added all necessary MkDocs dependencies to `pyproject.toml`
- New GitHub workflow to deploy documentation to GitHub Pages via `gh_pages` branch
- Harmonize all build and release scripts to have the same structure

## [v1.0.2] - 2025-10-11

Release Type: patch

### 🚀 Improvements
- Updated documentation across the tree

### 🛠 Internal
- Optimize build and release scripts
- Added GitHub release script to automate creation of GitHub releases.

## [v1.0.1] - 2025-10-11

Release Focus: patch

### 🚀 Improvements
- Updated documentation across the tree

### 🛠 Internal
- Added GitHub release script to automate creation of GitHub releases.

## [v1.0.0] - 2025-10-10

Release Focus: major

### 📋 Summary 

This is the first release of the second generations of Bayescalc which uses a new 
inference algorithm (based on variable elimination) to better handle larger networks.
It also has a better CLI interface with pop-up auto-completion and command history.
The network specification grammar has also been improved to better handle boolean variables
and the specification of the JPT for the nodes to use a more compact methematical syntax.
Finally the documentation have been improved with both a user guide and a developer guide.


### ✨ Additions
- Added `load()` command to load a network while in interactive mode
- Added graphic visualization of network graph (PNG, PDF, SVG) format
- Command line history
- Updated network syntax with `boolean` keyword for boolean variables
- Developer guide documentation improvements
- User guide documentation improvements

### 🐛 Bug Fixes
- All lint and type checking warnings 

### 🛠 Internal
- Added unit tests to pass >= 80% code coverage
- Updated and build and release scripts
- Updated CI/CD Github actions and pipelines
- Added PyPi upload
- Added build script for automatic code coverage badge updated

## [0.1.0] - 2025-09-30

Relase type: alpha

### ✨ Additions
- Complete rewrite of Bayescalc with new inference engine based on a variable elimination algorithm
- Use prompt_toolkit which gives both Tab-completion (with pop-up window) and command history


