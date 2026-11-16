# Diagram and waveform sources

`architecture.dot` is the editable Graphviz architecture source. `fsm.dot` is
an alternative Graphviz FSM description; the final FSM SVG/PNG uses the fixed
Matplotlib layout in scripts/build_figures.py to avoid crossing state labels. `waveform.png` plots the actual
`results/directed.vcd`; `results/waveform_verification.json` records a comparison
of all CPU response handshakes against the checked CSV.

Regenerate using `python scripts/build_figures.py` in an environment with
Matplotlib and Graphviz. An isolated environment is provided in `build/analysis-env`
on the authoring machine; it is not required for RTL verification.
