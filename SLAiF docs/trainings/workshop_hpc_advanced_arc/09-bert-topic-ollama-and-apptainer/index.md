# Case Study: BERT Topic, Ollama, And Apptainer

This case study combines several moving parts:

- NLTK stop words;
- an Ollama-hosted Llama 3 model for topic aggregation;
- a multilingual embedding model such as `paraphrase-multilingual-mpnet-base-v2`;
- a CUDA-enabled Apptainer image;
- ARC staging through dCache.

## Apptainer Cache And Temporary Directories

Large builds can exceed default temporary storage. Set explicit Apptainer cache and temporary directories:

```bash
export APPTAINER_CACHEDIR=/home/example/slaif_workshop/app_cache
mkdir -p "$APPTAINER_CACHEDIR/app_tmp"
export APPTAINER_TMPDIR="$APPTAINER_CACHEDIR/app_tmp"
```

## Example Bootstrap File

```text
Bootstrap: docker
From: nvidia/cuda:12.0.0-runtime-ubuntu22.04

%files
   /usr/share/ollama /opt/ollama

%environment
    export OLLAMA_MODELS=/opt/ollama/.ollama/models
    export PATH=/usr/local/bin:$PATH
    export NLTK_DATA=/usr/share/nltk_data

%post
    apt-get update -y
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        curl \
        zstd

    curl -fsSL https://ollama.com/install.sh | sh

    pip3 install --upgrade pip
    pip3 install pandas scikit-learn nltk bertopic ollama
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

    python3 -m nltk.downloader -d /usr/share/nltk_data all
    rm -rf /var/lib/apt/lists/*
```

Build the image:

```bash
export APPTAINER_CACHEDIR=/home/example/slaif_workshop/app_cache
mkdir -p "$APPTAINER_CACHEDIR/app_tmp"
export APPTAINER_TMPDIR="$APPTAINER_CACHEDIR/app_tmp"

apptainer build ollama.app ollama_apptainer.bootstrap
```

Upload the image once:

```bash
arccp ollama.app https://dcache.sling.si:2880/gen.vo.sling.si/user/example/ollama.app
```

## Local Test Before ARC Submission

Test the server and model locally before submitting through ARC:

```bash
apptainer exec --nv --contain --bind /tmp:/tmp \
  --env OLLAMA_HOST=127.0.0.1:11436 \
  ollama.app ollama serve
```

In another shell, verify that the client can talk to the server:

```bash
apptainer exec --contain \
  --env OLLAMA_HOST=127.0.0.1:11436 \
  ollama.app ollama list
```

## ARC Job Description

```xrsl
&
(executable = master_run.sh)
(jobname = "bert_ollama_test")
(stdout = test.log)
(join = yes)
(walltime = 2880)
(count = 1)
(countpernode = 1)
(gmlog = log)
(memory = 16000)
(runtimeenvironment = "APPS/BASE/GPU")
(inputfiles =
  ("master_run.sh" "")
  ("run_analysis.sh" "")
  ("bert_script-ollama.py" "")
  ("ollama.app" "https://dcache.sling.si:2880/gen.vo.sling.si/user/example/ollama.app")
  ("austrian_reddit_post_election_clean.csv" "")
  ("austrian_reddit_pre_election_clean.csv" "")
  ("paraphrase-multilingual-MiniLM-L12-v2.tgz" "https://dcache.sling.si:2880/gen.vo.sling.si/user/example/paraphrase-multilingual-MiniLM-L12-v2.tgz")
)
(outputfiles =
  ("results_html.zip" "")
  ("test.log" "")
  ("ollama_server.log" "")
)
```

## Container Execution Script

The inner analysis script starts an Ollama server on a random local port, waits for it to become available, runs the Python analysis, and cleans up the background server.

```bash
#!/bin/bash

PORT=$(shuf -i 11000-15000 -n 1)
export OLLAMA_HOST=127.0.0.1:$PORT
export HOME=/tmp/ollama_home_$PORT
mkdir -p "$HOME"

echo "Starting Ollama server on port $PORT..."
ollama serve > "/mnt/project/ollama_server.log" 2>&1 &
OLLAMA_PID=$!

cleanup() {
    if [[ -n "${OLLAMA_PID:-}" ]]; then
        kill "$OLLAMA_PID" 2>/dev/null || true
        wait "$OLLAMA_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT

echo "Waiting for Ollama to respond..."
ITER=0
while ! curl -s "http://127.0.0.1:$PORT/api/tags" > /dev/null; do
    sleep 1
    ITER=$((ITER+1))
    if [ "$ITER" -eq 30 ]; then
        echo "Timed out waiting for Ollama."
        exit 1
    fi
done

echo "Ollama is ready. Executing Python script..."
python3 /mnt/project/bert_script-ollama.py "$PORT"
EXIT_CODE=$?

echo "Analysis complete. Exiting with code $EXIT_CODE."
exit "$EXIT_CODE"
```

## Outer Wrapper Script

The outer script prepares the working directory, unpacks embeddings, launches the container, and packages HTML results:

```bash
#!/bin/bash

echo "--- STAGE 1: Setup and Untar ---"
mkdir -p ./project_data
mv *.csv ./project_data/
mv bert_script-ollama.py ./project_data/
mv run_analysis.sh ./project_data/

tar -xzf paraphrase-multilingual-MiniLM-L12-v2.tgz
mv paraphrase-multilingual-MiniLM-L12-v2 ./project_data/

echo "--- STAGE 2: Launching Container ---"
apptainer exec --nv --containall \
  --bind /tmp:/tmp \
  --bind "$(pwd)/project_data":/mnt/project \
  ollama.app /bin/bash /mnt/project/run_analysis.sh

echo "--- STAGE 3: Zip and Cleanup ---"
if ls ./project_data/*.html >/dev/null 2>&1; then
    zip -j results_html.zip ./project_data/*.html
else
    echo "Warning: no HTML files found to zip."
fi

echo "Job complete."
```
