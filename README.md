# Equation-Discovery-for-FODE
Repository for working on equation discovery for fractional order systems

## Export generated circuits to Modelica

`alt_parse.py` generates normalized circuit trees. `modelica_export.py` turns
those trees into connected, frequency-domain Modelica circuits with real and
imaginary phasor pins.

Generate Modelica models from the relaxed grammar:

```powershell
python modelica_export.py --grammar relaxed --depth 5
```

Limit the first run while checking the workflow:

```powershell
python modelica_export.py `
  --grammar relaxed `
  --depth 5 `
  --max-candidates 10
```

The command writes:

- `generated_modelica/GeneratedEISCircuits.mo`: connected candidate circuits;
- `generated_modelica/check_candidates.mos`: OpenModelica flattening commands;
- `generated_modelica/candidates.txt`: mapping from model names to circuits.

Run the OpenModelica compiler from the generated directory:

```powershell
Set-Location generated_modelica
omc check_candidates.mos
```

This creates `Candidate001_flat.mo`, `Candidate002_flat.mo`, and so on. Each
flattened model contains the component and Kirchhoff equations assembled by
OpenModelica.

Each generated `CandidateNNN` is a two-pin circuit. Its corresponding
`CandidateNNNImpedance` model connects a unit phasor-current source and ground.
Consequently, its outputs `Z_re` and `Z_im` are the real and imaginary parts of
the candidate impedance at angular frequency `omega`.

The current element conventions are:

- `CPE`: `Y = Q*(j*omega)^alpha`;
- `W`: infinite Warburg, `Z = sigma/sqrt(j*omega)`;
- `G`: `Z = Rg/sqrt(1 + j*omega*tauG)`;
- `zarc`: expanded as `R || CPE`;
- `randles`: expanded as `R || (CPE + W)`.

## Fit generated circuits to an NPZ recording

Generate cumulative circuit collections before fitting:

```powershell
python circuit_export.py --grammar relaxed --element-range 3 5
```

Each `*_elements_N.json` file contains all valid circuits with **up to** `N`
physical elements, including the mandatory series resistance `Rs`. Loading
`relaxed_elements_5.json` therefore compares the 1-, 2-, 3-, 4-, and 5-element
models in one BIC ranking.

Each completed run of `main.py` writes two matching, dataset-specific outputs:

- `Results/Plots/Nyquists/<dataset>_<grammar>_<N>_best_5.png`, containing the five
  highest-ranked fits;
- `Results/fit_results/<dataset>_<grammar>_<N>_fit_summary.json`, containing the fit
  settings, circuit counts, plot reference, and ten highest-ranked circuits.

The fitter reduces one raw recording to a robust median impedance at each
frequency, generates candidate circuits, tunes their parameters with bounded
multi-start least squares, and ranks the fitted models using BIC. To avoid
over-interpreting tiny score improvements, it prefers the simplest topology
within six BIC units of the minimum by default.

Install the dependencies and run the learning example from the repository root:

```powershell
python -m pip install -r requirements.txt
python "fitting parameters/fit_example.py" `
  --plot fit_diagnostic.png `
  --output-json fit_results.json
```

The default example uses `data/eis_20200224_190006.npz` and the constrained
`redone` grammar. Use `--help` to change the file, grammar depth, number of
candidates, multi-start count, or residual weighting.
