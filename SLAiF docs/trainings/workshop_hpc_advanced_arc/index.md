---
title: "Running Containerized AI Workloads on SLING"
subTitle: "ARC, dCache, Apptainer, and reproducible HPC jobs for AI research"
language: "en"
tocInHeader: true
chapters:
  - ./01-installation-and-setup
  - ./02-first-arc-job
  - ./03-xrsl-essentials
  - ./04-outputs-logs-and-debugging
  - ./05-apptainer-containers-for-hpc
  - ./06-running-containers-through-arc
  - ./07-data-management-with-dcache
  - ./08-scaling-up-with-python
  - ./09-bert-topic-ollama-and-apptainer
  - ./10-best-practices
  - ./11-troubleshooting
  - ./12-final-workflow-checklist
---

**Author:** Pavle Boskoski  
**Email:** pavle.boskoski@fis.unm.si  
**Affiliation:** Faculty of Information Studies in Novo mesto (FIS)

# Overview

This workshop explains how to prepare, submit, monitor, retrieve, and debug AI-oriented workloads on SLING and related HPC resources. The central idea is simple: package the software environment in an Apptainer image, stage large assets through dCache, describe the computation with xRSL, and submit the job through ARC.

By the end, participants should be able to:

- create and validate an ARC proxy;
- write a minimal xRSL job description;
- submit jobs to a selected Computing Element (CE);
- retrieve outputs and diagnostic logs;
- use Apptainer containers safely on shared HPC systems;
- stage large images and data through dCache;
- scale from one job to many parameterized jobs;
- debug common ARC, xRSL, Apptainer, and resource-allocation failures.

The material assumes basic command-line familiarity and some experience with Python-based research workflows. It does not assume prior ARC or Apptainer experience.

# Resources
- SLING documentation: `https://doc.sling.si`
- NorduGrid ARC documentation: `https://www.nordugrid.org`
- Apptainer documentation: `https://apptainer.org`
