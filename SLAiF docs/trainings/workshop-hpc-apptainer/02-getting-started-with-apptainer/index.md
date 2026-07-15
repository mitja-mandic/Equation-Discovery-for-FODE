# 2. Getting started with Apptainer

This is your first hands-on session. You will pull an existing container, run commands inside it, explore its environment, and see reproducibility in action. By the end you should be comfortable with the three core ways of interacting with a container: `exec`, `shell`, and `run`.

## 2.1 What you need

To follow along you need either:

- a Linux system (Ubuntu is recommended), or
- access to an HPC cluster,

with Apptainer already installed. Confirm that Apptainer is available before you start:

```bash
apptainer --version
```

If this prints a version number, you are ready. Apptainer's main advantages, which you will rely on throughout, are that it needs **no root access** (safe on shared systems), it produces **portable** environments, and it makes it **easy to run pre-built containers**.

## 2.2 Your first container

### Pull an image from Docker Hub

Apptainer can build a SIF image directly from a Docker source. Pull a standard Ubuntu image:

```bash
apptainer pull docker://ubuntu:22.04
```

This downloads the Docker layers and converts them into a single Apptainer image file, `ubuntu_22.04.sif`, in your current directory.

<Sidenote>
The `docker://` prefix tells Apptainer to fetch from a Docker registry and convert the result into the Singularity Image Format (SIF). The output is one self-contained `.sif` file you can copy around like any other file.
</Sidenote>

### Run a command inside the container

Use `exec` to run a single command inside the image. Here we read the container's OS information:

```bash
apptainer exec ubuntu_22.04.sif cat /etc/os-release
```

Notice that the reported distribution is Ubuntu 22.04 from inside the container, regardless of what your host system actually is.

### Open an interactive shell

To explore interactively, use `shell`:

```bash
apptainer shell ubuntu_22.04.sif
```

Once inside, try a few commands to get oriented:

```bash
whoami
pwd
ls /
```

When you are done, leave the container shell:

```bash
exit
```

## 2.3 Working with files

Containers do not live in complete isolation from your filesystem. Apptainer automatically makes parts of your host environment, including your current working directory, available inside the container by default.

Create a file on the host:

```bash
echo "Hello from host system" > test.txt
```

Now read it from inside the container:

```bash
apptainer exec ubuntu_22.04.sif cat test.txt
```

The container can see the file even though the file was never copied into the image. This is a key idea: the image holds the *environment*, while your *data* typically stays on the host and is made visible to the container at run time. You will revisit this explicitly with directory binding in the HPC chapter.

## 2.4 Inspecting containers

You can give a pulled image a name of your choice and then inspect its metadata.

Pull the image under a custom filename:

```bash
apptainer pull ubuntu.sif docker://ubuntu:22.04
```

Inspect the image's metadata:

```bash
apptainer inspect ubuntu.sif
```

Run a command using your locally named image:

```bash
apptainer exec ubuntu.sif hostname
```

## 2.5 Reproducibility in action

The real payoff is being able to run an exact, named environment anywhere. For example, run a specific Python version straight from a Docker source without installing Python on the host:

```bash
apptainer exec docker://python:3.10 python --version
```

Because the version is pinned in the image reference, anyone who runs this command gets the same Python version, on any machine with Apptainer. That is reproducibility in a single line.

### Bonus challenge

Run a short program inside the same Python container:

```bash
apptainer exec docker://python:3.10 python -c "print('Hello SLAIF')"
```

## 2.6 Run, exec, and shell

You have now used the three main verbs. It is worth distinguishing them clearly, because choosing the right one is half of using Apptainer well:

- **`exec`** runs a *specific command* you provide inside the container. Use it when you know exactly what you want to run, including in scripts and batch jobs.
- **`shell`** opens an *interactive shell* inside the container. Use it to explore, debug, or experiment.
- **`run`** executes the image's *default runscript*, the command the image author defined as its standard behavior. You will define such a runscript yourself in the next chapter.

## 2.7 What you should be able to do now

After this chapter you should be able to run containers, execute commands inside them, and explain why pinning an environment makes your work reproducible.

<Question
  id="apptainer-run-exec-shell"
  question="What is the difference between apptainer run, exec, and shell?"
  options={["They are aliases for the same operation", "* exec runs a specific command you provide, shell opens an interactive shell, and run executes the image's default runscript", "run opens an interactive shell, while exec and shell both build images", "exec is only for Docker images and shell is only for SIF images"]}
  attempts={2}
>
`exec` runs a command you specify, `shell` drops you into an interactive shell inside the container, and `run` executes the default runscript defined by the image author.
</Question>

<Question
  id="apptainer-pinned-reproducibility"
  question="Why does running 'apptainer exec docker://python:3.10 python --version' support reproducibility?"
  options={["Because it installs Python permanently on the host", "* Because the image reference pins an exact environment, so anyone running it on any machine with Apptainer gets the same version and behavior", "Because it disables all access to host files", "Because it guarantees the program runs faster"]}
  attempts={2}
>
The pinned image reference (`python:3.10`) defines an exact environment. Running the same reference reproduces the same interpreter and dependencies on any Apptainer-capable machine, independent of the host setup.
</Question>
