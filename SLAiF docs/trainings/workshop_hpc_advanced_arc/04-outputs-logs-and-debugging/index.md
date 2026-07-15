# Outputs, Logs, And Debugging

## Session Directories

ARC jobs run inside a temporary session directory on the remote cluster. Files that are not listed as outputs may disappear when the session expires, so always retrieve important results explicitly.

## Standard Output And Standard Error

Use `stdout` for normal program output and `stderr` for errors, tracebacks, and shell failures. During early development, `join=yes` is convenient because it puts both streams in one file.

## The `gmlog` Directory

The Grid Manager log directory is one of the most useful debugging tools in ARC. Enable it in xRSL:

```xrsl
(gmlog="log")
```

The directory can contain:

- `failed`: a concise explanation when the job fails, for example because walltime or memory was exceeded;
- `errors`: staging or system-level errors;
- `local`: details about the Slurm script created by ARC.

## Retrieving Results

By default, `arcget` creates a directory based on the job ID. Use `-d` to choose a cleaner destination:

```bash
arcget -d my_results_folder https://situla.fis.unm.si:2811/jobs/ABC123XYZ
```

When using a job list, retrieve only jobs in the right state:

```bash
arcget -j jobs.xml -s Finished -d ./finished_jobs
arcget -j jobs.xml -s Failed -d ./failed_jobs
```

After retrieving and validating outputs, clean finished jobs from the gateway:

```bash
arcclean https://situla.fis.unm.si:2811/jobs/ABC123XYZ
```

## Automated Retrieval

For repeated retrieval, use a small script rather than running `arcget` manually for every job:

```bash
#!/bin/bash
# Usage: ./get_jobs.sh [job_list] [target_dir] [status]

JOB_LIST=$1
TARGET=$2
STATUS=$3

mkdir -p "$TARGET"

for JOB_URL in $(arcstat -j "$JOB_LIST" -s "$STATUS" | grep "https" | awk '{print $NF}')
do
    echo "Processing job: $JOB_URL"
    timeout 30 arcget -f -j "$JOB_LIST" -D "$TARGET" "$JOB_URL"
done
```
