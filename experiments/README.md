# Comparable PCL, spectrum, and simulated experiments

This folder prepares a new set of fits using one settings file and the same
output layout for every measurement. Existing files under `Results` are left in
place. Raw recordings are outside this campaign.

## Prepare the dataset list

From the repository root, run:

```bash
.venv/bin/python experiments/run_experiments.py prepare
```

This creates `experiments/local_plan.csv` from `data/battery/EIS_mitja/*.pcl`,
`data/spectrum/*.npz`, and `data/simulation/generated/*.npz`. The plan is local and ignored by Git because the
measurements are local. The script never opens a measurement during discovery.
It refuses to replace an existing plan, so edits are preserved.

The plan has one row per dataset:

| Column | Meaning |
| --- | --- |
| `dataset_id` | Unique folder name for this measurement and channel. |
| `format` | `pcl`, `spectrum` or `simulated` (median), or `spectrum_direct` (one column per block). |
| `path` | Path to the input file, relative to the repository root. |
| `channel` | Battery channel for PCL, blank for spectrum. |
| `enabled` | Change `0` to `1` for datasets to fit. |
| `notes` | Your free-text description; saved in the campaign plan. |

PCL rows start with `batt_1`. Edit the channel if another channel is intended.
To fit several channels from one PCL file, duplicate its row and give each row
a unique `dataset_id`. Only use PCL files you trust; fitting them uses Python's
pickle loader.

## Fix common settings

Edit [settings.json](settings.json) before the campaign. It records the circuit
collection, grammar, maximum element count, residual scale, scatter floor,
`f_scale`, loss function, number of starts, random seed, refinement margin, and
both ranking metrics. `spectrum_column_index` is optional: `null` uses the
middle column of each block in `spectrum_direct` mode; a nonnegative integer
chooses that column in every block. To use direct data, change a spectrum row's
`format` to `spectrum_direct` in the plan. Saved summaries record the selected
columns. All enabled rows receive the applicable CLI options. Use a new campaign ID
when any of these choices changes. The current settings select the
`no_G_relaxed` five-element circuit collection with relative residual scaling
and soft-L1 loss; each campaign saves its own settings snapshot for comparison
with earlier runs.

The completed five-element soft-L1 sweep uses the same enabled PCL and spectrum
datasets in three campaigns:

| `f_scale` | Campaign folder under `Results/campaigns` |
| --- | --- |
| `0.001` | `unified_no_G_relaxed_5_elements_relative_soft_l1_fscale_0p001` |
| `0.01` | `unified_no_G_relaxed_5_elements_relative_soft_l1_fscale_0p01` |
| `0.1` | `unified_no_G_relaxed_5_elements_relative_soft_l1_fscale_0p1` |

The deterministic one-start control for both datasets is saved under
`unified_no_G_relaxed_5_elements_relative_soft_l1_fscale_0p001_deterministic_1start`.
The working `settings.json` currently selects `f_scale = 0.001` and one start;
each campaign contains the settings used for its own fits.

The same four soft-L1 configurations were rerun with `lp_error` ranking in the
first round and `lp_bic` ranking in the second round. Their campaign folder
names are the corresponding names above (including the one-start control) with
`_lp_error_lp_bic` appended. The working `settings.json` now selects
`optimizer_value` in the first round and `lp_bic` for final circuit ranking.
Each future summary exports `optimizer_value` for every circuit.

Simulated spectra `simulated_spectrum_006.npz` and
`simulated_spectrum_007.npz` were fitted together in
`Results/campaigns/simulated_006_007_no_G_relaxed_5_relative_soft_l1_fscale_0p001_optimizer_value_lp_bic_1start`.
This campaign uses the working settings above and saves its two-row plan,
settings snapshot, logs, summaries, and plots in that folder.

## Run and compare

```bash
.venv/bin/python experiments/run_experiments.py run baseline_01
```

The command fits all enabled rows sequentially, continues after a failed fit,
and returns a nonzero exit code if any fit failed. It creates a new folder and
refuses to reuse an existing campaign ID:

```text
Results/campaigns/baseline_01/
  plan.csv
  settings.json
  runs/
    spectrum_eis_20200224_190006/
      fit.log
      run.json
      Results/
        fit_results/       # first_round and refined JSON summaries
        Plots/Nyquists/   # first_round and refined plots
        Plots/Residuals/  # first_round and refined residual plots
    pcl_eis_bank1_20251112-103715_batt_1/
      ...
```

Each `run.json` records the exact command, input, channel, times, and exit code.
The two fit summary JSON files record optimizer settings and ranked circuits.
For a failed row, inspect its `fit.log`. The campaign plan snapshot includes
disabled rows too, so you can see the selection made for that campaign.

The script does not start fits during `prepare`; the `run` action is required.
Fitting every local measurement can take a long time. Select a small first set
in the plan to check the intended data and settings.
