# Web Content Integrity Monitor
# Usage: make crawl [CSV=...] [OUT=...]   |  make diff [N=7] [OUT=...]

CSV ?= sample_input.csv
OUT ?= output
N    ?= 7

.PHONY: crawl diff test install

install:
	pip install -r requirements.txt

crawl:
	./html2md "$(CSV)" "$(OUT)"

diff:
	./diffcheck "$(N)" "$(OUT)"

test:
	pytest tests/ -v
