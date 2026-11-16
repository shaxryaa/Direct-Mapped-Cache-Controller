.PHONY: all test traces synthesis
all:
	python3 scripts/run.py
test:
	python3 scripts/run.py --skip-synthesis
traces:
	python3 scripts/generate_traces.py
synthesis:
	yosys -Q -T -s scripts/synthesize.ys > results/synthesis.log
