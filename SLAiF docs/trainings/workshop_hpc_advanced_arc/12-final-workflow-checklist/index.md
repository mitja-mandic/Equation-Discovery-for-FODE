# Final Workflow Checklist

Before submitting a production batch, verify:

1. A valid proxy exists: `arcproxy -I`.
2. Large images and datasets are uploaded to dCache.
3. The Apptainer image was tested locally.
4. Wrapper scripts run outside ARC.
5. xRSL includes all local scripts in `inputfiles`.
6. Outputs and logs are listed in `outputfiles`.
7. `gmlog` is enabled.
8. The job list file, such as `jobs.xml`, is being maintained.
9. Submissions are throttled when launching many jobs.
10. Retrieved jobs are cleaned after validation.
