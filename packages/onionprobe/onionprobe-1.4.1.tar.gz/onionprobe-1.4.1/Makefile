#
# Onionprobe Makefile.
#
# This Makefile is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or any later version.
#
# This Makefile is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place - Suite 330, Boston, MA 02111-1307, USA
#

.PHONY: configs docs

# Include the environment file so Makefile to include custom configs and
# overrides
#
# Not doing that anymore since the .env file might have quotes, and thus be
# incompatible with the Makefile format.
#
# Also, all procedures using settings from the .env file are now done through
# the onionprobe-monitor script.
#-include .env

#
# Configs
#

configs:
	@./packages/real-world-onion-sites.py
	@./packages/securedrop.py
	@./packages/tpo.py

#
# Documentation
#

ONION_MKDOCS_PATH = vendors/onion-mkdocs

# This is useful when developing locally and Onion MkDocs is not yet installed
vendoring:
	@test   -e $(ONION_MKDOCS_PATH) && git -C $(ONION_MKDOCS_PATH) pull || true
	@test ! -e $(ONION_MKDOCS_PATH) && git clone https://gitlab.torproject.org/tpo/web/onion-mkdocs.git $(ONION_MKDOCS_PATH) || true

docs: compile-docs

manpages:
	@./packages/manpages.py
	@sed -e '1i\\# Onionprobe manual page' -e 's|^#|##|g' -e '/^%/d' docs/man/onionprobe.1.txt > docs/man/README.md
	@pandoc -s -f markdown -w man docs/man/onionprobe.1.txt -o docs/man/onionprobe.1
	@# Pipe output to sed to avoid http://lintian.debian.org/tags/hyphen-used-as-minus-sign.html
	@# Fixed in http://johnmacfarlane.net/pandoc/releases.html#pandoc-1.10-2013-01-19
	@#sed -i -e 's/--/\\-\\-/g' docs/man/onionprobe.1

compile-docs: manpages
	@make onion-mkdocs-build

#
# Packaging
#

clean:
	@find -name __pycache__ -exec rm -rf {} \; &> /dev/null || true

build-python-package: clean
	@python3 -m build

upload-python-test-package:
	@twine upload --skip-existing --repository testpypi dist/*

upload-python-package:
	@twine upload --skip-existing dist/*

update_sbuild:
	@sudo sbuild-update -udcar u

mk-build-deps:
	@mk-build-deps --install --tool='apt-get -y' debian/control

build-debian-test-package: mk-build-deps
	@dpkg-buildpackage -rfakeroot --no-sign

sbuild: update_sbuild
	@#sbuild -c stable-amd64-sbuild
	@sbuild  -c unstable-amd64-sbuild

#
# Release
#

release: clean configs docs

#
# Other
#

# Include the Onion MkDocs Makefile
# See https://www.gnu.org/software/make/manual/html_node/Include.html
-include $(ONION_MKDOCS_PATH)/Makefile.onion-mkdocs
