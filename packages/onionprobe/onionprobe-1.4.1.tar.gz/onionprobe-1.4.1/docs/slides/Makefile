#
# Makefile for Onion Tex Slim slides
# Adapted to Onionprobe
#
# See https://gitlab.torproject.org/rhatto/onion-tex-slim
# Inspired by https://gitlab.torproject.org/anarcat/presentations/-/blob/main/soto-2022/Makefile
#

TEMPLATE      = beamer-ahf-slim.tex
TEMPLATE_PATH = ../../vendors/onion-tex-slim/src/pandoc/templates/$(TEMPLATE)
COMPILE_CMD   = pandoc -t beamer --pdf-engine=pdflatex --slide-level 2 --template="$(TEMPLATE_PATH)"
ALL						= $(shell find -name '*.md' | sed -e 's/.md$$/.pdf/g')

export TEXINPUTS:=$(shell pwd)/../../vendors/onion-tex-slim/src/tex:${TEXINPUTS}

.PHONY: all clean

all: $(ALL)

%.pdf: %.md
	@echo Building $@...
	@$(COMPILE_CMD) $< -o $@

clean:
	@rm -r $(ALL) || true
