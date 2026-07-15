# 3. Building your own container

Pulling existing images is useful, but real research environments usually need specific packages and configuration. In this chapter you will write an Apptainer **definition file**, build it into a custom image, and run reproducible workloads from it.

## 3.1 What is a definition file?

A definition file, conventionally named with a `.def` extension, is a text recipe that describes how your container is built. It makes the build process explicit and repeatable. A definition file typically specifies:

- the **base image** to start from;
- the **installation steps** to run;
- the **environment variables** to set;
- the **run commands** that define the image's default behavior.

Because the recipe is plain text, you can version it alongside your code, review it, and rebuild an identical image later.

<Sidenote>
Think of the definition file as the documented, executable version of "how I set up my environment." Instead of a README that drifts out of date, the recipe *is* the build.
</Sidenote>

## 3.2 Prerequisites

You need Apptainer installed on a Linux environment. Confirm it is available:

```bash
apptainer --version
```

## 3.3 Create a definition file

Create a file named `python.def`:

```bash
nano python.def
```

Add the following content:

```singularity
Bootstrap: docker
From: python:3.10

%post
    apt-get update
    apt-get install -y git
    pip install numpy pandas

%environment
    export MY_VAR="SLAIF_ENV"

%runscript
    echo "Running container..."
    python --version
```

Save the file. Each section has a distinct role:

- **`Bootstrap` / `From`** define the starting point. Here we bootstrap from the Docker `python:3.10` image.
- **`%post`** runs *while the image is being built*. This is where you install system packages and Python libraries so they become a permanent part of the image.
- **`%environment`** sets environment variables that apply *every time the container runs*.
- **`%runscript`** defines the default command executed by `apptainer run`.

## 3.4 Build the container

Build a SIF image from the definition file:

```bash
apptainer build python.sif python.def
```

Apptainer reads the recipe, fetches the base image, executes the `%post` steps, and produces a single `python.sif` file containing your customized environment.

## 3.5 Run the container

Because the definition file declares a `%runscript`, you can now use `run` to execute that default behavior:

```bash
apptainer run python.sif
```

You should see the "Running container..." message followed by the Python version, exactly as defined in `%runscript`.

## 3.6 Execute specific commands

You are not limited to the runscript. Use `exec` to run any command and confirm that your installed packages are present:

```bash
apptainer exec python.sif python -c "import numpy; print(numpy.__version__)"
```

This prints the NumPy version, proving that the `pip install` step in `%post` was baked into the image.

## 3.7 Test the environment variable

Check that the variable defined in `%environment` is available at run time:

```bash
apptainer exec python.sif bash -c 'echo $MY_VAR'
```

This should print `SLAIF_ENV`.

## 3.8 Modify and rebuild

Containers are meant to evolve with your needs. To add a package, edit the `%post` section of `python.def` and add another install line, for example:

```bash
pip install matplotlib
```

Then rebuild the image with the same `apptainer build` command. The rebuild is fully determined by the recipe, so the new image is reproducible too.

### Bonus challenge

Run a script that lives on the host inside your custom container:

```bash
echo "print('Hello from container')" > test.py
apptainer exec python.sif python test.py
```

The script stays on the host; the environment to run it comes from the image.

## 3.9 What you should be able to do now

After this chapter you should be able to write a definition file, build a custom reproducible image, install dependencies into it, and run code against it.

<Question
  id="apptainer-post-section"
  question="What is the purpose of the %post section in an Apptainer definition file?"
  options={["It sets environment variables for every run of the container", "* It runs commands while the image is being built, for example installing packages so they become part of the image", "It defines the command executed by 'apptainer run'", "It deletes the base image after building"]}
  attempts={2}
>
`%post` runs during the build. It is where you install system packages and libraries so they are permanently included in the resulting image. By contrast, `%environment` sets variables at run time and `%runscript` defines the default run behavior.
</Question>

<Question
  id="apptainer-build-vs-run"
  question="What is the difference between 'apptainer build' and 'apptainer run'?"
  options={["They are the same command with different names", "* build creates a SIF image from a definition file, while run executes the image's default runscript", "build executes the runscript, while run compiles the definition file", "run is only used for Docker images and build only for SIF images"]}
  attempts={2}
>
`build` turns a definition file into a SIF image (executing the `%post` steps along the way), while `run` executes the already-built image's `%runscript`.
</Question>
