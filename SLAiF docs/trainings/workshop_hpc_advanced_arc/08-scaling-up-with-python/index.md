# Scaling Up With Python

## The Scaling Problem

Grid computing becomes valuable when the same workflow can run across tens or hundreds of parameter combinations. Writing xRSL files by hand does not scale and is easy to get wrong.

Use Python to generate job descriptions programmatically:

```python
def generate_xrsl(index):
    return f"""&
(executable=main.sh)
(arguments=--batch {index})
(jobname=job_{index})
(stdout=out_{index}.txt)
(join=yes)
(walltime=60)
(memory=4000)
"""
```

You can submit a generated description directly:

```python
import subprocess

description = generate_xrsl(1)
subprocess.run(
    ["arcsub", "-c", "ce01.si", "--jobdescrstring", description],
    check=True,
)
```

Prefer `subprocess.run` over `os.system` when writing production scripts, because it handles argument boundaries and failures more reliably.

## Selecting Hosts And Queues

A submission script can choose between known targets:

```python
def queue_fragment(host):
    if host == "arnes":
        return '(queue = "gpu")'
    return ""
```

It can also skip completed parameter values by inspecting existing output files:

```python
import re
from pathlib import Path

def first_number(path):
    matches = re.findall(r"\d+", path.name)
    return int(matches[0]) if matches else 0

root = Path("./enum_model_7_mask_seq")
processed = {
    first_number(path)
    for path in root.rglob("*_model_pyro.pt")
}

target = sorted(set(range(0, 603)) - processed)
```

## Throttling Submissions

A Computing Element is a gateway, not an unlimited API endpoint. Add a short delay when submitting many jobs:

```python
import time

for index in range(100):
    submit_job(index)
    time.sleep(1)
```

This reduces load on the CE and makes failures easier to diagnose.
