# Best Practices

## Memory

If a job requests 16 GB and uses 17 GB, Slurm may kill it. The ARC `gmlog/failed` file often records this clearly. Request a realistic margin, commonly 10 to 20 percent above expected use.

## Walltime

Shorter walltime requests can schedule faster. If a job takes two hours, do not request 48 hours unless there is a real reason.

## Staging

Use ARC input-file renaming deliberately:

```xrsl
("local_name" "https://remote/source")
```

This lets compute scripts use stable local names even when the remote storage layout changes.

## Containers

Keep large data outside the SIF image. Store datasets and reusable model assets on dCache or shared storage, and keep the image focused on software dependencies.

Use labels in definition files to record image provenance:

```text
%labels
    Author Pavle Boskoski
    Version 2026-05
    Description CUDA, Ollama, BERTopic, and Python analysis environment
```

## Cleanup

Finished jobs consume space on gateway systems. After retrieving and checking results, clean them:

```bash
arcclean -j jobs.xml -s Finished
```
