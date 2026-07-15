# 1. Containers and reproducibility

Before running a single command, it is worth understanding *why* containers exist and what problem Apptainer actually solves. This chapter builds the mental model that the rest of the workshop relies on.

## 1.1 Why this matters

Research software rarely runs in isolation. It depends on a specific interpreter version, a set of libraries, system-level packages, and a pile of implicit assumptions about the machine it runs on. That fragility creates three recurring problems:

- **Version sensitivity.** A pipeline that works with one version of a library can break, or worse, silently change its output, with another.
- **Machine drift.** The same code on two different machines can behave differently because the surrounding environment is different.
- **Shared-system constraints.** HPC clusters are multi-user environments with strict security and deployment rules. You usually cannot install whatever you like as root.

Containerization addresses all three by packaging the software, its dependencies, and its execution logic into a single portable runtime unit.

## 1.2 What is containerization?

Containerization is a method for packaging an application together with its runtime environment so that it runs the same way everywhere. A container typically bundles:

- the application code;
- the system libraries it needs;
- its dependencies;
- its configuration.

The goal is **portability**: run the same workload, in the same environment, across different systems. This is what directly attacks the classic "it worked on my machine" failure.

## 1.3 Why containers help reproducibility

Reproducing a computational experiment means much more than sharing the source code. To truly reproduce a result you also need to preserve:

- library versions;
- interpreter versions;
- system-level dependencies;
- the execution assumptions baked into the environment.

A container captures all of these together. Instead of writing a long, quickly-outdated document that explains how to recreate an environment, you ship the environment itself.

<Sidenote>
Reproducibility is not only about being able to rerun your own work months later. It is also about letting reviewers, collaborators, and future researchers obtain the same results from the same inputs.
</Sidenote>

## 1.4 Containers versus virtual machines

Containers are often compared to virtual machines (VMs), but the two work differently:

- **Virtual machines** emulate a full operating system, including their own kernel, on top of a hypervisor.
- **Containers** share the host kernel and isolate only the userspace around the application.

Because containers do not carry a whole guest operating system, they are usually:

- lighter in size;
- faster to start;
- easier to distribute.

For scientific workflows and software portability, this lightweight model is typically a much better fit than full virtualization.

## 1.5 Why not just install software manually?

Manual installation seems simpler at first, but it scales badly:

- it is hard to standardize across many machines;
- version conflicts are common;
- documentation drifts out of date quickly;
- recreating an old environment after several months can be painful or impossible.

Containers make the runtime environment **explicit and portable** instead of leaving it as an undocumented side effect of how a particular machine was set up.

## 1.6 What is Apptainer?

Apptainer is a container platform widely used in scientific computing. It is the continuation of the Singularity ecosystem and is designed specifically for shared compute infrastructure. It is especially relevant for:

- HPC clusters;
- academic environments;
- reproducible research.

The key images and concepts you will meet throughout this workshop are:

- **Image** – a packaged runtime environment.
- **SIF** – the Singularity Image Format, the common single-file Apptainer image format.
- **Definition file** – a text recipe describing how to build an image.
- **`exec`** – run a specific command inside a container.
- **`shell`** – open an interactive shell inside a container.
- **`run`** – execute the image's default runscript.

## 1.7 Why Apptainer instead of Docker on HPC?

Docker is the best-known container tool, but it is often a poor fit for HPC. The difference comes down to how each tool handles privilege and shared systems:

- HPC systems are shared by many users, with stricter security and isolation requirements than a personal machine.
- Docker commonly relies on a **privileged daemon** model, which administrators are reluctant to allow on shared clusters.
- Apptainer is aligned with typical HPC constraints: non-root-oriented workflows, user-space execution, and practical use on shared systems.

Importantly, Apptainer can still run images built from Docker sources, so you are not cut off from the broader container ecosystem.

## 1.8 Where Slurm fits in

On HPC systems you usually do not run long jobs interactively. Instead, work is submitted to a **workload manager and job scheduler**, most commonly **Slurm**. Slurm coordinates access to shared resources by:

- queueing jobs;
- allocating compute resources such as CPU cores, memory, and wall time;
- enforcing time and resource limits;
- collecting outputs and logs.

A typical HPC workflow therefore looks like this:

1. prepare code and input files;
2. prepare the runtime environment;
3. create a Slurm batch script;
4. submit the job;
5. monitor execution;
6. inspect output and error logs.

Apptainer is what makes step 2 portable: it lets you run the exact same environment inside these scheduled jobs that you tested on your own machine. The final chapter of this workshop puts Apptainer and Slurm together.

<Question
  id="apptainer-why-on-hpc"
  question="Why is Apptainer often preferred over Docker on HPC clusters?"
  options={["Because Docker cannot run scientific software at all", "* Because Apptainer supports non-root, user-space execution and does not rely on a privileged daemon, which fits shared multi-user systems", "Because Apptainer images are always smaller than Docker images", "Because Slurm only accepts Apptainer images"]}
  attempts={2}
>
HPC systems are shared and security-sensitive, so administrators avoid Docker's privileged daemon model. Apptainer is designed for non-root, user-space execution on shared infrastructure, while still being able to run images built from Docker sources.
</Question>

<Question
  id="containers-vs-vms"
  question="What is the key difference between a container and a virtual machine?"
  options={["A container emulates a full operating system including its own kernel", "* A container shares the host kernel and isolates userspace, while a VM emulates a full operating system", "A virtual machine is always faster to start than a container", "There is no technical difference; the terms are interchangeable"]}
  attempts={2}
>
Virtual machines emulate a complete operating system on a hypervisor, whereas containers share the host kernel and isolate only the userspace around the application. This is why containers are typically lighter and faster to start.
</Question>
