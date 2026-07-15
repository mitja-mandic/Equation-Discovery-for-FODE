# First ARC Job

## Why Start Small?

ARC workflows involve authentication, job description parsing, queueing, execution, data staging, and output retrieval. A minimal job helps verify the complete path before adding containers, GPUs, or large input files.

The first job should require no input files. A useful starting point is to print the environment of the compute node.

## Minimal `hello.xrsl`

```xrsl
&(executable="/usr/bin/env")
(jobname="hello_env")
(stdout="environment.txt")
(join=yes)
(walltime="5 minutes")
(memory=1000)
```

Submit the job to a specific Computing Element:

```bash
arcsub -c situla.fis.unm.si hello.xrsl
```

ARC returns a job URL. Save it; you will use it for monitoring and retrieval.

## Monitoring The Job

```bash
arcstat https://situla.fis.unm.si:2811/jobs/ABC123XYZ
```

Common states include:

```text
Submitted -> DataStagingIn -> Queuing -> Running -> DataStagingOut -> Finished
```

If the job never leaves an early state, check your proxy, CE availability, and input-file staging rules.
