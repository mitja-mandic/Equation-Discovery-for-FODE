# Data Management With dCache

## Why Use dCache?

Large SIF files and datasets should not be uploaded from a laptop for every job. Upload them once to dCache, then let ARC stage them repeatedly to the execution site.

A typical SLING dCache URL has this shape:

```text
https://dcache.sling.si:2880/gen.vo.sling.si/user/<username>/<path>
```

Upload a large image with:

```bash
arccp my_local_image.sif https://dcache.sling.si:2880/gen.vo.sling.si/user/example/my_image.sif
```

List remote files with:

```bash
arcls -l https://dcache.sling.si:2880/gen.vo.sling.si/user/example/
```

In xRSL, stage the remote file by naming both its local job name and its remote URL:

```xrsl
("my_image.sif" "https://dcache.sling.si:2880/gen.vo.sling.si/user/example/my_image.sif")
```
