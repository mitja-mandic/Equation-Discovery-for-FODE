# 4. Apptainer on HPC with Slurm

This final chapter brings everything together. You will take a container, package a small workload, and run it on a cluster as a scheduled **Slurm** job. You will also learn how to give the container access to your working files and how to avoid the most common mistakes on shared systems.

## 4.1 Why Apptainer on HPC

On HPC systems you usually do **not** have root access, and software must run safely on shared infrastructure. Apptainer is the standard choice in this setting because:

- it does not require a privileged Docker daemon;
- it works well on shared clusters;
- it supports portable, reproducible research environments;
- it can run images built from Docker sources.

Slurm then schedules your work onto cluster resources such as CPUs, memory, and time. Together, Apptainer provides the portable environment and Slurm provides controlled access to the hardware.

## 4.2 Prerequisites

Before starting, make sure you have:

- access to an HPC cluster running Slurm;
- Apptainer available on the cluster;
- basic command-line knowledge;
- a working `.sif` image (for example the `python.sif` from the previous chapter) or access to Docker-based images.

Check that the key tools are available:

```bash
apptainer --version
sbatch --version
```

You may also want to see the partitions your cluster offers:

```bash
sinfo
```

## 4.3 The basic HPC workflow

A typical containerized HPC job follows the same six steps every time:

1. connect to the cluster;
2. prepare your files;
3. create a Slurm job script;
4. submit the job with `sbatch`;
5. monitor the job;
6. inspect the output files.

The rest of this chapter walks through these steps with concrete examples.

## 4.4 Prepare a workload

Create a small Python script to run inside the container:

```bash
nano hello.py
```

Add a single line:

```python
print("Hello from Apptainer on HPC")
```

Save and exit. You can also create it directly from the shell:

```bash
echo 'print("Hello from Apptainer on HPC")' > hello.py
```

## 4.5 Write a Slurm job script

Create a job script named `job_hello.slurm`:

```bash
nano job_hello.slurm
```

Add the following:

```bash
#!/bin/bash
#SBATCH --job-name=apptainer-hello
#SBATCH --output=output_%j.txt
#SBATCH --error=error_%j.txt
#SBATCH --time=00:05:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G

apptainer exec python.sif python hello.py
```

We use `python.sif`, the image built in the previous chapter. Running from a prebuilt local image is often the better choice on HPC because:

- the image does not need to be pulled on every run;
- startup may be faster;
- it avoids unnecessary external downloads during jobs.

The `#SBATCH` lines tell Slurm how to handle the job:

- `--job-name` gives the job a readable name;
- `--output` stores standard output (`%j` is replaced by the job ID);
- `--error` stores error output;
- `--time` sets the maximum runtime;
- `--cpus-per-task` requests CPU cores;
- `--mem` requests memory.

The final line runs your Python script inside the Python container.

<Sidenote>
Always request realistic resources. Too little time or memory will cause the job to be killed; too much may make it wait longer in the queue. Start small and adjust based on the logs.
</Sidenote>

## 4.6 Submit the job

Submit the script to Slurm:

```bash
sbatch job_hello.slurm
```

Slurm responds with a job ID:

```text
Submitted batch job 12345
```

## 4.7 Monitor the job

Check your queued and running jobs:

```bash
squeue -u $USER
```

After the job finishes, inspect its accounting details:

```bash
sacct -j 12345
```

Replace `12345` with your real job ID.

## 4.8 Inspect the output

Once the job completes, read the output file:

```bash
cat output_12345.txt
```

The expected content is:

```text
Hello from Apptainer on HPC
```

If the job failed, check the error file:

```bash
cat error_12345.txt
```

## 4.9 Binding a working directory

Many HPC workflows read inputs and write outputs in the current working directory. Create an input file:

```bash
echo "SLAIF HPC test" > input.txt
```

Create a script that reads it:

```bash
nano read_input.py
```

Add:

```python
with open("input.txt", "r") as f:
    print(f.read())
```

Run it through the container:

```bash
apptainer exec python.sif python read_input.py
```

In many cases the current directory is already visible inside the container. When it is not, bind it explicitly:

```bash
apptainer exec --bind $PWD:$PWD --pwd $PWD python.sif python read_input.py
```

Binding lets the container access your project files **without copying them into the image**. This keeps images small and data on the host where it belongs.

### A Slurm job with a bound directory

Create `job_bind.slurm`:

```bash
nano job_bind.slurm
```

Add:

```bash
#!/bin/bash
#SBATCH --job-name=apptainer-bind
#SBATCH --output=output_%j.txt
#SBATCH --error=error_%j.txt
#SBATCH --time=00:05:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G

apptainer exec --bind $PWD:$PWD --pwd $PWD python.sif python read_input.py
```

Submit it:

```bash
sbatch job_bind.slurm
```

## 4.10 Checking the container's view of the environment

It is often useful to confirm what the container actually sees. Create a script:

```bash
nano env_check.py
```

Add:

```python
import os
print("Current working directory:", os.getcwd())
print("Files:", os.listdir("."))
```

Run it:

```bash
apptainer exec python.sif python env_check.py
```

## 4.11 Bonus challenges

### Run a NumPy computation

Create `compute.py`:

```bash
nano compute.py
```

Add:

```python
import numpy as np

a = np.array([1, 2, 3, 4, 5])
print("Mean:", a.mean())
```

Run it with an image that contains NumPy, such as the custom image from the previous chapter. An example Slurm script:

```bash
#!/bin/bash
#SBATCH --job-name=apptainer-numpy
#SBATCH --output=output_%j.txt
#SBATCH --error=error_%j.txt
#SBATCH --time=00:05:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G

apptainer exec python.sif python compute.py
```

### Cancel a job

If you need to stop a running or queued job:

```bash
scancel 12345
```

## 4.12 Common mistakes

A few mistakes account for most failures when moving container work onto a cluster:

1. **Using Docker on HPC directly.** Many clusters forbid Docker for security reasons. Use Apptainer instead.
2. **Pulling large images on every job.** This is slow and wasteful. Prefer a prebuilt local `.sif` image.
3. **File not found inside the container.** The container may not see your path as expected. Use `--bind` and `--pwd` when needed.
4. **Assuming internet access on compute nodes.** Some clusters restrict external network access. Build or pull images ahead of time.
5. **Wrong resource requests.** Too little memory or time causes job failure. Check the logs and adjust your `#SBATCH` settings.

## 4.13 What you should be able to do now

After this chapter you should be able to:

- submit a Slurm job that runs a container;
- execute scripts inside Apptainer on a cluster;
- inspect output and error logs;
- explain the basic HPC container workflow;
- use bound directories for file-based tasks.

<Question
  id="hpc-local-sif-vs-docker-pull"
  question="Why is a prebuilt local .sif image often better than pulling docker:// images inside every HPC job?"
  options={["Because docker:// images cannot run on HPC at all", "* Because a local .sif avoids repeated downloads, starts faster, and does not depend on external network access during the job", "Because local .sif files use no disk space", "Because Slurm refuses to run docker:// references"]}
  attempts={2}
>
Pulling on every job is slow and assumes network access on compute nodes, which is often restricted. A prebuilt local `.sif` image is downloaded once, starts faster, and keeps jobs self-contained.
</Question>

<Question
  id="hpc-bind-purpose"
  question="When would you use the --bind option with Apptainer?"
  options={["To permanently add files to the image at build time", "* To make host directories and their files available inside the container at run time without copying them into the image", "To disable Slurm resource limits", "To convert a Docker image into a SIF file"]}
  attempts={2}
>
`--bind` (often together with `--pwd`) exposes host directories inside the container at run time, so the container can read inputs and write outputs without those files being baked into the image.
</Question>

<Question
  id="hpc-role-of-slurm"
  question="What is the role of Slurm in a containerized HPC workflow?"
  options={["It builds container images from definition files", "* It is a workload manager and scheduler that queues jobs and allocates shared resources such as CPU, memory, and time", "It replaces Apptainer for running containers", "It provides internet access to compute nodes"]}
  attempts={2}
>
Slurm schedules work on the cluster: it queues jobs, allocates CPU/memory/time, enforces limits, and collects logs. Apptainer provides the portable environment; Slurm provides controlled access to the hardware.
</Question>
