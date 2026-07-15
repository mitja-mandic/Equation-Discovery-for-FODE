---
title: "Apptainer (Singularity)"
subTitle: "Portable, reproducible research environments for AI and HPC, a hands-on workshop"
language: "en"
tocInHeader: true
chapters:
  - ./01-containers-and-reproducibility
  - ./02-getting-started-with-apptainer
  - ./03-building-your-own-container
  - ./04-apptainer-on-hpc-with-slurm
---

**Author:** Robi Pritržnik, MSc CS  
**Email:** robi.pritrznik@fis.unm.si  
**Affiliation:** Faculty of Information Studies in Novo mesto (FIS)

# About this workshop

Research software is fragile in a very specific way. It usually depends on exact versions of interpreters, libraries, and system tools, and it tends to behave differently the moment it leaves the machine it was written on. On shared High Performance Computing (HPC) systems the problem is worse: you rarely have root access, the software stack is not yours to change, and the same code can silently produce different results. The recurring complaint, "but it worked on my machine," is not a joke in research, it is a reproducibility failure.

This workshop teaches **Apptainer** (formerly **Singularity**), a container platform built for exactly these constraints. Apptainer lets you package an application together with its full runtime environment into a single portable image, then run that image without privileged daemons, safely, on a laptop or on a shared cluster. It is the de facto standard for containers in scientific computing precisely because it was designed around the realities of multi-user HPC.

# Who this is for

This is a hands-on, practical course aimed at researchers, students, and engineers who already work on the Linux command line and want to make their computational environments portable and reproducible. No prior container experience is assumed. Some familiarity with HPC and job schedulers is helpful for the final chapter but is explained as needed.

# What you will be able to do

By the end of the workshop you will be able to:

- explain what containerization is and why it matters for reproducible research;
- pull and run existing containers with `apptainer`;
- inspect container environments and run commands inside them;
- write an Apptainer definition file and build your own custom image;
- run containerized workloads on an HPC cluster through Slurm batch jobs;
- avoid the most common mistakes when moving container work onto shared infrastructure.

# How the workshop is structured

The book moves from concepts to practice and then from a single machine to a cluster:

1. **Containers and reproducibility** establishes the mental model: what a container is, how it differs from a virtual machine, and why Apptainer fits HPC.
2. **Getting started with Apptainer** is your first hands-on session: pulling, running, and inspecting containers.
3. **Building your own container** introduces definition files so you can produce custom, reproducible images.
4. **Apptainer on HPC with Slurm** brings everything together, running your containers as scheduled cluster jobs.

Each practical chapter ends with short comprehension questions so you can check your understanding before moving on.

<Sidenote>
**Use of AI.** AI tools were used as an aid while preparing this material, for generating ideas, refining examples, and drafting text. All final commands and explanations were reviewed and verified by the author.
</Sidenote>
