# Running Containers Through ARC

In xRSL, do not usually call `apptainer` directly as a long inline command. Stage a wrapper script and make that script the executable:

```bash
#!/bin/bash
apptainer exec --nv my_image.sif python3 my_code.py
```

Then reference the wrapper and image in xRSL:

```xrsl
&
(executable = "wrapper.sh")
(jobname = "container_test")
(stdout = "test.log")
(join = yes)
(walltime = 60)
(count = 1)
(memory = 16000)
(runtimeenvironment = "APPS/BASE/GPU")
(inputfiles =
  ("wrapper.sh" "")
  ("my_code.py" "")
  ("my_image.sif" "https://dcache.sling.si:2880/gen.vo.sling.si/user/example/my_image.sif")
)
(outputfiles =
  ("test.log" "")
)
```

This pattern keeps xRSL readable and makes local testing easier, because the wrapper can be run outside ARC before submission.
