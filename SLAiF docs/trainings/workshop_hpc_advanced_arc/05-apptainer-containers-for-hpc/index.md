# Apptainer Containers For HPC

## Why Containers Matter

AI and scientific Python workflows often depend on exact versions of Python, CUDA, PyTorch, TensorFlow, Pyro, scikit-learn, or other libraries. Installing the same software stack on every cluster is fragile. Containers provide a portable execution environment that can move across NSC, Vega, Arnes, and other sites.

Apptainer, formerly Singularity, is designed for HPC. Its main artifact is a Singularity Image File, or SIF: a compressed, usually read-only image that can be copied, archived, and submitted with a job.

## Apptainer Versus Docker And Podman

| Feature | Docker | Podman | Apptainer |
|:---|:---|:---|:---|
| Daemon | Root daemon required | Daemonless | Daemonless |
| Rootless use | Possible, but more complex | Native | Native/default in HPC use |
| HPC integration | Limited | Partial | Strong MPI, GPU, and shared filesystem support |
| Image model | Layered registry image | Layered registry image | Single-file SIF |
| Security model | Container root can be risky on shared systems | Rootless by default | User remains the same user inside and outside |

The key HPC advantage is the privilege model: Apptainer does not give users a practical path to become root on shared infrastructure. Your UID and GID remain your UID and GID inside the container.

## Definition Files

An Apptainer definition file is the build recipe for an image:

```text
Bootstrap: docker
From: ubuntu:22.04

%post
    apt-get update
    apt-get install -y python3 python3-pip
    pip3 install torch

%environment
    export PROJECT_ROOT=/opt/project

%runscript
    python3 /opt/project/main.py "$@"
```

Common sections are:

- `%setup`: commands run on the host during build; use rarely and carefully;
- `%files`: copy files from the host into the image;
- `%post`: install software during image build;
- `%environment`: define runtime environment variables;
- `%runscript`: default command used by `apptainer run`;
- `%test`: validate the image after build.

## Default Bind Mounts

Apptainer integrates with the host more than Docker does. By default, it often makes these paths available:

- `$HOME`;
- `/tmp`;
- `/proc`;
- `/sys`;
- `/dev`;
- the current working directory.

This is convenient on HPC systems because code inside the container can read and write data in the user home directory or shared storage without many explicit `-v` flags.

## GPU Access With `--nv`

Do not bake cluster-specific NVIDIA drivers into an image. Drivers change across hosts and should come from the execution node.

Use `--nv` to bind host NVIDIA devices and libraries into the container:

```bash
apptainer exec --nv my_image.sif nvidia-smi
```

This is essential for PyTorch, TensorFlow, Pyro, and similar GPU workloads.

## Writable Temporary Filesystems

SIF images are read-only by default. If a program tries to write into system paths such as `/var/tmp`, use an ephemeral writable layer:

```bash
apptainer exec --writable-tmpfs --nv my_image.sif python3 script.py
```

Changes in the writable temporary layer disappear after the process exits. This is useful for software that expects write access to system-like paths but does not need those changes preserved.

## Core Commands

```bash
apptainer run my_image.sif
apptainer exec my_image.sif python3 script.py
apptainer shell --nv my_image.sif
```

Use `shell` for interactive debugging:

```bash
apptainer shell --nv my_env.sif
Apptainer> python3
>>> import torch
>>> print(torch.cuda.is_available())
```
