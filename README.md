# Equation Discovery for Fractional-Order Systems

Generate, fit, and rank equivalent-circuit models for electrochemical impedance
spectroscopy (EIS) data.

## Requirements

- Python 3.11 or newer
- The packages pinned in `requirements.txt`

Create and activate an isolated environment from the repository root on Linux
or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, use:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

Then install the dependencies:

```bash
python -m pip install -r requirements.txt
```

## Set up a new Ubuntu 26.04 experiment PC

After copying or cloning this repository onto the new PC's SSD, run this once
from a terminal in the repository root (and rerun it after a new installation if
needed). Do not copy an old `.venv` from another computer; the script creates
one for the new PC:

```bash
bash setup_ubuntu_26_04.sh
```

The script updates Ubuntu packages; installs Git, build tools, Tk support for
interactive plots, `rsync`, `tmux`, and `htop`; creates `.venv`; installs the
pinned Python packages; and checks that they import. It asks for your password
through `sudo` for the Ubuntu package steps. It does not format or mount drives.
Ubuntu 26.04 includes Python 3.14, which meets this project's Python 3.11+
requirement. Use `.venv/bin/python` for project commands so packages remain
separate from Ubuntu's system Python.

Finish these machine-specific steps:

1. Reboot if Ubuntu's updates request it. Check **Software & Updates → Additional
   Drivers** if the PC has an NVIDIA GPU or other hardware needing a driver.
   The fitting code itself uses SciPy on the CPU; it does not require CUDA.
2. In **Disks**, verify which drive is the 256 GB system SSD and which is the
   separate 4 TB data drive. Mount the data-drive partitions from **Files**.
   Check their contents and confirm you can create a test file before using
   them for experiments. Do not change their format or partitions without
   checking their contents first.
3. Copy measurement files to the new PC. Git does not include local files under
   `data/battery` and `data/spectrum`, the local campaign plan, or `Results`.
   Keep a backup of measurements and results on another device.
4. Check **Settings → Power** so the PC will not suspend during a long fit.
5. Verify a small run from the repository root:

   ```bash
   .venv/bin/python main.py --data-mode simulated --data-path data/simulation/generated/simulated_spectrum.npz --circuit-path data/circuits/no_G_relaxed_elements_4.json --number-starts 1 --no-show-plots --no-show-residual-plots
   ```

   For repeatable measurement campaigns, follow the
   [campaign workflow](experiments/README.md). Its default `Results` directory
   is inside this repository on the SSD, so choose storage for large outputs
   before running a large campaign.

## Quick start

The repository includes a small simulated EIS dataset and a collection of 92
circuits (all circuits with up to 4 elements), so a clean clone can run without external measurement files by selecting those inputs explicitly:

```bash
python main.py --data-mode simulated --data-path data/simulation/generated/simulated_spectrum.npz --circuit-path data/circuits/no_G_relaxed_elements_4.json
```

For a non-interactive or headless run:

```bash
python main.py --data-mode simulated --data-path data/simulation/generated/simulated_spectrum.npz --circuit-path data/circuits/no_G_relaxed_elements_4.json --no-show-plots --no-show-residual-plots
```

The bundled inputs are:

- `data/simulation/generated/simulated_spectrum.npz`
- `data/circuits/no_G_relaxed_elements_4.json`

This example fits every bundled circuit from six reproducible starting
points, refines the best candidates, and prints the highest-ranked results. It
does not save output files unless `--save-results` is supplied.

Run `python main.py --help` for the complete command-line interface. Settings in
`main.py` provide defaults; command-line arguments override them for one run.
Importing `main` does not start fitting.

## Input data

### Simulated or measured NPZ spectra

The `simulated` and `spectrum` modes use NPZ files containing frequency `F` in
Hz and complex impedance measurements `Z` in ohms. The loader reduces repeated
measurements to component-wise medians and estimates robust real and imaginary
scatter from their median absolute deviations.

Use `spectrum_direct` to fit one measured impedance column from each frequency
block without taking a median. By default it takes the middle column of each
block; `--spectrum-column-index 100` chooses column 100 in every block instead.
Columns are zero-indexed and the chosen index must exist in every block. Invalid
impedance points are removed. Scatter estimates still use all repeats if you
select `--residual-scale scatter`. Saved summaries record the chosen columns,
and direct result filenames include `spectrum_direct_` to keep them separate
from median results.

To fit a user-supplied measured spectrum with the bundled circuits:

```bash
python main.py --data-mode spectrum --data-path path/to/measurement.npz --circuit-path data/circuits/no_G_relaxed_elements_4.json --no-show-plots

# Fit a direct (unaggregated) spectrum from the same file:
python main.py --data-mode spectrum_direct --data-path path/to/measurement.npz --circuit-path data/circuits/no_G_relaxed_elements_4.json --no-show-plots
```

Measurement files under `data/spectrum` are intentionally not included in Git;
provide your own path when using `spectrum` mode.

### Processed battery pickles

Use `pcl` mode for a trusted pickle containing a dictionary of battery channels:

```bash
python main.py --data-mode pcl --data-path path/to/measurement.pcl --channel batt_1 --no-show-plots
```

For the selected channel, array 0 is interpreted as frequency in Hz and array 1
as complex impedance. All points are retained; remaining arrays are unused.
Because no measurement uncertainty is inferred from this format, unit real and
imaginary scales are returned. Invalid shapes, nonpositive or nonfinite
frequencies, and nonfinite impedances raise an error.


### Raw recordings

The legacy `raw` mode remains present in the source, but its command-line
downsampling argument is currently incomplete.

## Simulate circuit data

Edit the configuration sections in `data/simulation/run_simulation.py`, then run:

```bash
python data/simulation/run_simulation.py
```

The current default sweep covers 0.01 Hz to 100 kHz with 30 intervals per
decade. The script saves a loader-compatible NPZ and a Nyquist/Bode plot under
`data/simulation/generated`. Existing files are preserved by adding `_001`,
`_002`, and later suffixes. See the
[simulator guide](data/simulation/README.md) for circuit definitions, units,
noise settings, and output details.

Fit a newly generated file without editing `main.py`:

```bash
python main.py --data-mode simulated --data-path data/simulation/generated/simulated_spectrum_001.npz --no-show-plots
```

Use the actual filename printed by the simulator.

## Generate circuit collections

The bundled `no_G_relaxed` collection can be used directly. To generate a new
cumulative collection with one of the exporter-supported grammars (`relaxed`,
`compact_hybrid`, or `compact_only_blocks`), run:

```bash
python -m Circuit_generation.circuit_export --grammar relaxed --element-range 3 5 --output-directory data/circuits
```

Each `*_elements_N.json` file contains all valid circuits with up to `N`
physical elements, including the mandatory series resistance `Rs`. For example,
`relaxed_elements_5.json` contains models with one through five elements.
Collection sizes grow combinatorially, so inspect smaller exports before fitting
larger element limits.

To fit a generated collection, either match its name and maximum element count:

```bash
python main.py --grammar relaxed --elements 5 --no-show-plots
```

or pass its path explicitly with `--circuit-path`.

## Fitting options

This example uses the bundled data and circuits while overriding common fitting
and reporting settings:

```bash
python main.py --data-mode simulated --data-path data/simulation/generated/simulated_spectrum.npz --circuit-path data/circuits/no_G_relaxed_elements_4.json --residual-scale relative --f-scale 0.01 --number-starts 6 --random-seed 42 --save-results --no-show-plots
```

Useful options include:

- `--data-mode` and `--data-path` to select the input format and file;
- `--circuit-path`, or `--grammar` with `--elements`, to select circuits;
- `--channel` to select a raw/PCL battery channel;
- `--number-starts` and `--random-seed` to control initial values;
- `--residual-scale`, `--scatter-floor`, `--loss`, and `--f-scale` to control fitting;
- `--sort-first-round` and `--sort-second-round` to control ranking;
- `--save-results` and `--output-root` to control saved artifacts;
- `--show-plots` and `--show-residual-plots` to control interactive figures.

Relative paths are resolved from the terminal's working directory. The other
least-squares settings are defined in `fitting_parameters/train_refactored.py`.
Changing residual scaling does not automatically recalibrate `f_scale`; specify
it in the selected scaled-residual units when using `soft_l1`. With `linear`
loss, `f_scale` has no effect on the optimization.

### Residual scaling

`--residual-scale` accepts four modes:

- `unscaled` leaves real and imaginary residuals in ohms;
- `scatter` divides them by separate robust real and imaginary scatter estimates
  from repeated measurements;
- `relative` divides each component by its measured component magnitude, floored
  at 10% of that component's median absolute magnitude;
- `magnitude` divides both components by the same measured `|Z|`, floored at 10%
  of the median positive magnitude.

An entirely zero component or spectrum uses unit divisors where a relative scale
cannot be inferred. `--scatter-floor` applies an additional floor, expressed as
a fraction of the median scatter, before scatter scaling.

`optimizer_value = 2 * scipy_cost / number_of_frequencies` is the optimizer's
loss per complex frequency point. It uses the selected residual scaling, loss,
and `f_scale`; for linear loss with unscaled residuals it equals MSE. Saved
summaries include it for every circuit alongside MSE, relative MSE, BIC, and EBIC.
Compare optimizer values across rounds only when scaling, loss, and `f_scale`
are the same.

### Refinement and ranking

By default, the first round is sorted by `optimizer_value`. Every candidate with

```text
optimizer_value <= best optimizer_value * (1 + reoptimization error margin)
```

is refined from its own best first-round parameters. The best starting point
for each circuit is also selected by `optimizer_value`. The default margin is
0.20 (20%); a margin of zero includes only candidates tied for the lowest score. Should you
choose to sort by BIC-related metric in the first round, a hard coded delta of 10 is
implemented in the model_selection.py file.

The refined results are sorted by BIC by default to account for circuit complexity.
Pass `--sort-second-round optimizer_value` to rank them by fit loss alone.
Console previews and plots show at
most the top five circuits.

Use `--reoptimization-error-margin`, `--sort-first-round`, and
`--sort-second-round` to override these defaults.

`combinatorial_score` is also available for either ranking stage. It uses
`n * log(MSE) + alpha * element_count + beta * log(arrangement_count)`, where
`n` is twice the number of frequencies. `arrangement_count` is the number of
distinct ways to place the same element types in the circuit's normalized
series/parallel topology. `Rs` stays fixed; swapping series or parallel
children, or swapping identical elements, does not create another arrangement.
Placements that simplify to a different topology are excluded. The count is
computed from each circuit, without looking up other generated circuits.
The weights `COMBINATORIAL_ELEMENT_WEIGHT` (`alpha`) and
`COMBINATORIAL_ARRANGEMENT_WEIGHT` (`beta`) are set in
`fitting_parameters/train_refactored.py`; both default to 1. This is a custom
ranking score, not BIC. Saved summaries include the score and arrangement count.

## Inserting a manual circuit

You can insert a circuit manually in main.py by defining it (two examples already pre-defined)
and changing the value on line 310 to the name of the variable under which you stored the circuit.
This circuit will then be inserted on top of the grammar-selected circuits, its parameters will be
estimated with the same algorithm as the refinement part.


## Results and residual diagnostics

For a repeatable series of PCL and measured spectrum runs, see the
[campaign workflow](experiments/README.md). It keeps one settings file and a
separate output folder for each selected measurement and PCL channel.

Use `--save-results` to write artifacts under `Results`. A saved run produces
first-round and reoptimized versions of:

- Nyquist plots under `Results/Plots/Nyquists`;
- residual plots under `Results/Plots/Residuals`;
- JSON summaries under `Results/fit_results`.

Current fits save directly in these folders; campaign runs keep separate
folders for each dataset. The Nyquist plots contain the five highest-ranked fits. PCL output names include the selected
battery channel, so channels from one file remain separate. Each version 3 JSON summary records the
input mode and channel, source file hash, exact processed frequency and complex
impedance arrays, loader scales, fitting divisors, optimizer settings, run
settings, circuit counts, and associated plots. `circuit_metrics` contains the
best fit for every circuit, including its parameters, optimizer value, MSE, relative MSE, AIC,
BIC, EBIC, LP metrics, bounds, optimizer status, and evaluation costs. The top
ten also include predicted impedance arrays for frequency-domain comparisons.
First-round and refined summaries include `scaled_lp_bic` for every circuit. It applies the
existing LP-BIC formula to the real and imaginary residuals after division by
the saved `fitting_residual_divisors`, using LP exponent 0.5. The score changes
with the residual scaling mode, so compare it only among fits on the same data
with the same scaling.
It is also available to `--sort-first-round` and `--sort-second-round`.
Aggregate evaluation counts and fit time include all starts without storing
each start separately. `delta_bic` is measured from the lowest BIC in that
stage, regardless of the ranking metric. Older saved summaries retain their
original metadata.
Filename suffixes default to `first_round` and `reoptimized` and can be changed
with `--filename-suffix` and `--final-filename-suffix`.

Display residual plots interactively with:

```bash
python main.py --show-residual-plots
```

Each residual figure shows raw real and imaginary errors in ohms beside the
matching normalized residuals. Residuals are model minus measurement. Dotted
lines mark `+/- f_scale` in the normalized panels when using `soft_l1` loss;
linear-loss plots omit these lines. Residual figures are saved
whenever `--save-results` is enabled, even if interactive residual plots are not
shown.
