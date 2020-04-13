# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?= "-W"
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	mkdir -p "$(SOURCEDIR)/scripts"
	mkdir -p "$(SOURCEDIR)/solutions"
	mkdir -p "$(SOURCEDIR)/static"
	mkdir -p "$(SOURCEDIR)/supervisor"
	cp "$(SOURCEDIR)/../../Hello Bluesky.ipynb" "$(SOURCEDIR)"
	cp "$(SOURCEDIR)/../../Hello Python and Jupyter.ipynb" "$(SOURCEDIR)"
	cp -r "$(SOURCEDIR)/../../scripts/." "$(SOURCEDIR)"/scripts
	cp -r "$(SOURCEDIR)/../../solutions/." "$(SOURCEDIR)"/solutions
	cp -r "$(SOURCEDIR)/../../static/." "$(SOURCEDIR)"/static
	cp -r "$(SOURCEDIR)/../../supervisor/." "$(SOURCEDIR)"/supervisor
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
