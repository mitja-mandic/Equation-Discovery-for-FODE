# xRSL Essentials

xRSL, the eXtended Resource Specification Language, describes what the job should run, what resources it needs, what files it should stage, and which outputs should be preserved.

The official xRSL reference is:

```text
https://www.nordugrid.org/documents/xrsl.pdf
```

## Basic Structure

An ARC job description begins with `&`, which combines all following attributes:

```xrsl
& (executable = "main_fis.sh")
  (arguments = "--N 10")
  (jobname = "MyJob_01")
```

Attributes are enclosed in parentheses. Values may be strings, numbers, or lists.

## Execution And Identity Attributes

Use these fields to define what runs:

- `executable`: the script or binary to run;
- `arguments`: arguments passed to the executable;
- `jobname`: a human-readable name shown in `arcstat`;
- `runtimeenvironment`: a requested software environment on the cluster, such as `APPS/BASE/GPU`.

If the executable is a local file, include it in `inputfiles`; otherwise ARC will not stage it to the execution site.

## Hardware Requests

Use resource requests carefully. Over-requesting can make jobs wait longer; under-requesting can make jobs fail.

- `memory`: requested memory in megabytes. ARC commonly treats this as total job memory, while Slurm is often configured per core.
- `walltime`: maximum runtime. The job is killed when the limit is reached.
- `count`: number of slots or cores.
- `countpernode`: useful when cores must be placed on the same physical node.
- `queue`: target queue or partition, such as `gpu`, `long`, or `short`.

## Data And I/O

The most important I/O fields are:

- `stdout`: standard output file;
- `stderr`: standard error file;
- `join = yes`: merge standard output and standard error;
- `gmlog`: ARC Grid Manager diagnostic log directory;
- `inputfiles`: files staged before execution;
- `outputfiles`: files retrieved or staged out after execution.

Input files use this form:

```xrsl
(inputfiles =
  ("main_fis.sh" "")
  ("data.npz" "https://dcache.sling.si:2880/gen.vo.sling.si/user/example/data.npz")
)
```

An empty source string means ARC looks for the file locally at submission time. A URL means ARC stages the file from remote storage.
