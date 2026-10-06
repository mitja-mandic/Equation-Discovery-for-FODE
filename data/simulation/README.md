# Circuit data simulator

Open `run_simulation.py` in your IDE, select the project's Python environment,
edit its **CONFIGURATION** sections, and run the file. It works independently
of the IDE's working directory and uses the existing NumPy/Matplotlib dependencies.

Define `CIRCUIT` with the same component classes used by the fitter, nesting
`Series(children=(...))` and `Parallel(children=(...))`. Enter numeric values in
`PARAMETERS` under the names passed to the components. Supported elements are
`Resistor`, `SeriesResistance`, `CPE`, `Inductor`, `Warburg`, and `Gerischer`.
An ideal capacitor is a CPE with exponent 1 (its Q value is capacitance in F).
No impedance equation needs to be entered. Only series/parallel networks are
supported; the simulator reuses the project's element conventions.

For example, replace the example circuit and parameters with:

```python
CIRCUIT = Series(children=(
    SeriesResistance("Rs"),
    Parallel(children=(Resistor("R1"), CPE("C1", "alpha1"))),
))
PARAMETERS = {"Rs": 0.1, "R1": 1.0, "C1": 0.01, "alpha1": 1.0}
```

Values use SI units: resistance in ohms, inductance in H, CPE Q in
S·s^alpha, Gerischer time constant in seconds. Warburg follows the project's
`sigma / sqrt(j*omega)` convention (sigma in ohm·s^-1/2).
Values must be positive, and CPE exponents must lie in [0, 1].

The default sweep spans **0.001–1,000,000 Hz** with 30 intervals per decade
(271 points including endpoints). Adjust both bounds and the sampling density
for the time scales of your circuit; a fixed range cannot capture every possible
parameter choice. Frequency is converted internally from Hz to rad/s.

Set `ADD_NOISE = False` for exact data. When enabled, independent Gaussian noise
is added to the real and imaginary parts of every repeat, each with standard
deviation `hypot(RELATIVE_NOISE * abs(Z_clean), ABSOLUTE_NOISE_OHM)`.
`RELATIVE_NOISE = 0.01` means 1% per component per measurement. With multiple
repeats the fitter's median will be less noisy. `RANDOM_SEED` makes runs repeatable;
set it to `None` for new noise each run. This is synthetic frequency-domain EIS,
not a time-domain voltage/current or instrument-error simulation.

Output defaults to `generated/simulated_spectrum.npz` and a matching PNG with
Nyquist and Bode plots. Re-running replaces these outputs; change `OUTPUT_PATH`
to keep multiple datasets. `SHOW_PLOT` controls the interactive plot window,
and `SAVE_PLOT` controls the PNG.

The NPZ stores `F` in Hz and complex `Z` in ohms with shape
`(1, number_frequencies, repeats)`, plus `Z_clean`, `noise_std_ohm`, and
`metadata_json` recording the circuit, parameters, and noise settings. It needs
no pickle loading. To fit it using the existing `main.py`, set:

```python
DATA_MODE = "simulated"
SIMULATED_DATA_PATH = PROJECT_DIR / "data" / "simulation" / "generated" / "simulated_spectrum.npz"
```

Generate the dataset with `run_simulation.py` before running the fitter. If you
change the simulator's `OUTPUT_PATH`, update `SIMULATED_DATA_PATH` to match.

The existing loader computes measurement medians and robust scatter. Noiseless
data or a single repeat yields zero scatter; use the fitter's uncertainty floor
when weighting those data.
