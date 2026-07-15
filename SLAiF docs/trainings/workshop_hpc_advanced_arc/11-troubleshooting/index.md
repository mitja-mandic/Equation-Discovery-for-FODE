# Troubleshooting

## Proxy Expired

Symptom:

```text
Authentication failed
```

Fix:

```bash
arcproxy -s gen.vo.sling.si
```

Then confirm the new proxy:

```bash
arcproxy -I
```

## Computing Element Not Found

Symptoms include connection refusal, unreachable host errors, or a job that cannot be submitted to the selected CE.

Check:

- whether the CE alias is correct;
- whether the cluster is under maintenance;
- whether your ARC configuration file contains the expected endpoint;
- whether your network can reach the CE.

## Input File Not Found

ARC stages files either from the local submission directory or from a URL. If a job cannot find an input:

- verify local file names at submission time;
- verify dCache URLs;
- check spelling and case in `inputfiles`;
- inspect `gmlog/errors`.

## Container Execution Failure

If Apptainer reports an execution-format or image error:

- confirm the file is a SIF or valid Apptainer image;
- check that the image was fully uploaded to dCache;
- test the image locally with `apptainer exec`;
- use `--nv` only on nodes where GPU support is expected;
- add `--writable-tmpfs` if software tries to write into read-only system paths.

## Out Of Memory

Look in:

```text
gmlog/failed
```

If the failure is memory-related, raise the `memory` request and check whether the workload can be split into smaller jobs.
