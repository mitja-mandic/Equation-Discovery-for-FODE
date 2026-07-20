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
