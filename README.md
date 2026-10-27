# Equation-Discovery-for-FODE
Repository for working on equation discovery for fractional order systems

## Load processed battery EIS pickles

In `main.py`, set `DATA_MODE = "pcl"`, choose `PCL_DATA_PATH`, and set
`PCL_BATTERY_CHANNEL` (for example, `"batt_1"`). The example path points to
`data/battery/EIS_mitja/eis_bank1_20250703-161359.pcl`.

Each file is a dictionary of battery channels. For the selected channel, array
0 is interpreted as frequency in Hz and array 1 as complex impedance. All
points are retained without averaging or coherence filtering; the other arrays
are unused. Equal real and imaginary residual weights are used because no
measurement uncertainty is inferred from those arrays. Invalid shapes,
nonpositive/nonfinite frequencies, and nonfinite impedances raise an error.
Only load trusted pickle files, since unpickling can execute code.

The existing `raw`, `spectrum`, and `simulated` modes remain available, and the
default mode remains `spectrum`.

## Simulate circuit data from the IDE

Open `data/simulation/run_simulation.py`, edit its circuit, component values,
frequency sweep and noise settings, and run the file. The default sweep covers
1 mHz to 1 MHz. It saves an NPZ compatible with the existing spectrum loader and
Nyquist/Bode plots. See [the simulator guide](data/simulation/README.md).

## Fit generated circuits to an NPZ recording

From the repository directory, run:

```powershell
python main.py
```

Run `python main.py --help` for all options. Source settings remain the defaults;
command-line arguments override them for one run. Importing `main` does not start
fitting. Example (PowerShell):

```powershell
python main.py --data-mode spectrum --data-path data/spectrum/eis_20200226_190006.npz `
  --grammar no_G_relaxed --elements 5 --residual-scale relative --f-scale 0.01 `
  --number-starts 6 --random-seed 42 `
  --save-results --no-show-plots
```

Use `--circuit-path` to supply a circuit JSON directly, `--channel` for raw/PCL
battery data, and `--raw-points` to control raw-data downsampling. Relative paths
are resolved from the terminal's working directory. `--output-root` selects the
parent of the `Results` directory; filename prefixes/suffixes and plot titles
are also configurable. `--filename-prefix` replaces the old environment override.

There are four different options for residual scaling in the optimization algorithm:
`unscaled, scatter, relative. magnitude`. Unscaled leaves the residuals unchanged,
scatter scaling takes median across repeated measurements of the same battery pack/SOFC
in the dataset. Relative scaling divides the real (imaginary) part of the error with maximum
absolute value of the real (imaginary) part of the impedance measurement. Magnitude scaling does
the same as relative scaling, but it divides the errors with largest absolute value of the impedance
measurement (not separated into real and imaginary parts).

`--f-scale` is the only least-squares setting exposed on the command line and
applies to both fitting stages. The other least-squares settings remain defined
in `fitting_parameters/train_refactored.py`. `--reoptimization-error-margin` is
a fraction (0.2 means 20%). `--residual-scale` and `--scatter-floor` control
residual preparation. Changing scaling does not automatically recalibrate
`f_scale`: specify a threshold in the chosen scaled-residual units.

Second-round fitting uses `REOPTIMIZATION_ERROR_MARGIN` in `main.py` (default
`0.20`). Every candidate with first-round MSE at or below
`best_mse * (1 + REOPTIMIZATION_ERROR_MARGIN)` is refined, starting from its own
best first-round parameters. This replaces the fixed candidate-count cutoff in
both fitting implementations. A margin of zero includes only candidates tied
for the lowest MSE. The returned refined list includes all selected candidates;
console previews and plots show only the top five. The margin controls selection
only; optimizer settings and ranking metrics are unchanged.

Generate cumulative circuit collections before fitting:

```powershell
python circuit_export.py --grammar relaxed --element-range 3 5
```

Each `*_elements_N.json` file contains all valid circuits with **up to** `N`
physical elements, including the mandatory series resistance `Rs`. Loading
`relaxed_elements_5.json` therefore compares the 1-, 2-, 3-, 4-, and 5-element
models in one BIC ranking.

Note that the 7 element collection already contains nearly 140.000 circuits. Adding an additional 8th element would bring the circuit
count well over 1 million, making fitting very expensive.


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
# Residual diagnostics

Set `RESIDUAL_SCALE = "magnitude"` in `fitting_parameters/train_refactored.py`
to divide both real and imaginary errors by the same measured impedance
magnitude. The divisor is floored at 10% of the median positive magnitude;
an entirely zero spectrum uses unit divisors. This option applies to every
fitting stage and the normalized residual plots. The existing `"relative"`
option continues to use separate component magnitudes. Ranking metrics are unchanged.

Running `main.py` also displays real and imaginary residuals against log frequency
for the top five circuits, separately for the initial and reoptimized fits.
Each figure includes raw real and imaginary errors in ohms in the left column,
with matching vertical scales, and normalized residuals in the right column.
Residuals are model minus measured impedance, divided by the exact scales used
by the optimizer (`RESIDUAL_SCALE`). Dotted lines mark ±`f_scale` for that stage
only in the normalized panels.
With `SAVE_RESULTS = True`, these figures are saved under `Results/Plots/Residuals`.
Relative scaling gives relative errors, not measurement-standard-deviation units.
