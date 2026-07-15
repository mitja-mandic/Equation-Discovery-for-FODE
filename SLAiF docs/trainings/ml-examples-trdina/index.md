---
title: "Become a Master of Supercomputing: Intensive HPC Training at FIS"
subTitle: "ML Examples on HPC Trdina"
language: "en"
tocInHeader: true
---

**Author:** Biljana Mileva Boskoska
**Presenter** Srdjan Skrbic  
**Email:** srdjan.skrbic@fis.unm.si  
**Affiliation:** Faculty of Information Studies in Novo mesto (FIS)

# ML Examples on HPC Trdina

Overview
This document describes an end-to-end setup so that students can copy and paste the commands
and run small machine learning experiments on the HPC TRDINA cluster using SLURM. It
contains:
* Exact Miniconda installation commands (for HPC-TRDINA).
* Creation of aml-envConda environment with modern Python and scikit-learn.
* A small Python test script plus a SLURM test script.
* Final SLURM scripts for two ML exercises:
–Exercise 1 (intermediate): Iris classification.
–Exercise 2 (harder): Breast cancer classification with SLURM array jobs.

## 1 Install Miniconda on the Cluster

All commands in this section are to be run on the HPC-TRDINA login node (e.g.trdina-login)
in the user's home directory.

### 1.1 Download and Install Miniconda

```bash
cd ~
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

During the installer:
* Accept the license (type yes).
* Accept the default install location (e.g./home/$USER/miniconda3) or choose a path in
your home directory.
* When asked:
Do you wish the installer to initialize Miniconda3 by running conda init?
answer yes.
After installation, reload the shell configuration:

```bash
source ~/.bashrc
```

Verify that conda works:

```bash
conda --version
```

## 2 Create theml-envEnvironment

We now create a Conda environment with a modern Python version and scikit-learn.

### 2.1 Create and Activate the Environment

```bash
conda create -n ml-env python=3.10 -y
conda activate ml-env
```

### 2.2 Install scikit-learn

Using Conda (recommended on HPC):

```bash
conda install scikit-learn -y
python --version
python -c "import sklearn; print('sklearn version:', __import__('sklearn').__version__)"
```

## 3 Test Python + scikit-learn + SLURM

This section prepares a small test to verify that Python, scikit-learn, and SLURM all work
together.

### 3.1 Python Test Script

Create the file test_sklearn.py in your home directory:

```python
#!/usr/bin/env python
import sys
import sklearn
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
print("Python version:", sys.version)
print("scikit-learn version:", sklearn.__version__)
# Small sanity test with Iris
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
X, y, test_size=0.2, random_state=42
)
clf = LogisticRegression(max_iter=500, n_jobs=1)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Test accuracy on Iris: {acc:.4f}")
```

Make the script executable (optional):
chmod +x test_sklearn.py
You can test it interactively (after activating the environment):

```bash
conda activate ml-env
python test_sklearn.py
```

### 3.2 SLURM Test Script

Create the SLURM script run_test_sklearn.sh:

```txt
#!/bin/bash
#SBATCH --job-name=test_sklearn
#SBATCH --output=test_sklearn_%j.out
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:05:00
#SBATCH --mem-per-cpu=1000
echo "Running on host: $(hostname)"
# Enable conda in non-interactive shell
source ~/miniconda3/etc/profile.d/conda.sh
conda activate ml-env
python test_sklearn.py
```

Make the script executable:
chmod +x run_test_sklearn.sh
Submit the job:

```bash
sbatch run_test_sklearn.sh
```

After the job finishes, inspect the output file:
ls test_sklearn_*.out
cat test_sklearn_XXXX.out # replace XXXX with the job ID
You should see the Python version, scikit-learn version, and a test accuracy value.

## 4 Exercise 1: Iris Classification (Intermediate)

This exercise uses the Iris dataset and demonstrates:
* Passing arguments from SLURM to Python.
* Basic classification with KNN and Decision Trees.
* Adjusting the test set size.

### 4.1 Python Script:iris_classify.py

Create the file iris_classify.py:

```python
#!/usr/bin/env python
import sys
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
def main():
if len(sys.argv) < 2:
print("Usage: iris_classify.py [knn|tree] [test_size]")
sys.exit(1)
model_name = sys.argv[1]
# optional second argument: test_size (default 0.2)
if len(sys.argv) >= 3 and sys.argv[2] != "":
test_size = float(sys.argv[2])
else:
test_size = 0.2
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
X, y, test_size=test_size, random_state=42
)
if model_name == "knn":
model = KNeighborsClassifier(n_neighbors=5)
elif model_name == "tree":
model = DecisionTreeClassifier(random_state=42)
else:
print("Unknown model:", model_name)
sys.exit(1)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Model: {model_name}")
print(f"Test size: {test_size}")
print(f"Accuracy: {acc:.4f}")
if __name__ == "__main__":
main()
```

### 4.2 SLURM Script:run_iris.sh

Create the SLURM script run_iris.sh:

```bash
#!/bin/bash
#SBATCH --job-name=iris
#SBATCH --output=iris_%j.out
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:05:00
#SBATCH --mem-per-cpu=1000
echo "Running on host: $(hostname)"
echo "Model: $1"
echo "Test size: $2"
source ~/miniconda3/etc/profile.d/conda.sh
conda activate ml-env
python iris_classify.py "$1" "$2"
chmod +x run_iris.sh
```

### 4.3 Example Submissions

* KNN with default test size (0.2):

```bash
sbatch run_iris.sh knn
```

* Decision Tree with test size 0.3:

```bash
sbatch run_iris.sh tree 0.3
```

After the jobs complete, inspect the output files:
ls iris_*.out
cat iris_XXXX.out
Students can compare accuracy for different models and test sizes.

## 5 Exercise 2: Breast Cancer Classification with SLURM Array (Harder)

This exercise uses the Breast Cancer Wisconsin (Diagnostic) dataset and demonstrates:
* Binary classification with a neural network (MLPClassifier).
* Hyperparameter sweeps using SLURM array jobs.
* Collecting results for different parameter combinations.

### 5.1 Python Script:breast_cancer_mlp.py

Create the file breast_cancer_mlp.py:

```python
#!/usr/bin/env python
import sys
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
def main():
if len(sys.argv) < 3:
print("Usage: breast_cancer_mlp.py <hidden_layer_size> <alpha>")
sys.exit(1)
hidden_layer_size = int(sys.argv[1]) # e.g. 32, 64, 128
alpha = float(sys.argv[2]) # e.g. 0.0001, 0.001, 0.01
data = load_breast_cancer()
X, y = data.data, data.target
X_train, X_test, y_train, y_test = train_test_split(
X, y, test_size=0.2, stratify=y, random_state=42
)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)
clf = MLPClassifier(
hidden_layer_sizes=(hidden_layer_size,),
alpha=alpha,
max_iter=200,
random_state=42
)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Hidden layer size: {hidden_layer_size}")
print(f"Alpha: {alpha}")
print(f"Accuracy: {acc:.4f}")
if __name__ == "__main__":
main()
```

### 5.2 SLURM Array Script:run_breast_cancer_array.sh

Create the SLURM array script run_breast_cancer_array.sh:

```txt
#!/bin/bash
#SBATCH --job-name=bc_mlp
#SBATCH --output=bc_mlp_%A_%a.out
#SBATCH --array=0-8 # 9 combinations (3 hidden sizes x 3 alphas)
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:10:00
#SBATCH --mem-per-cpu=2000
echo "Running on host: $(hostname)"
echo "Array task ID: ${SLURM_ARRAY_TASK_ID}"
# Activate conda env
source ~/miniconda3/etc/profile.d/conda.sh
conda activate ml-env
# Parameter grids
HIDDEN_SIZES=(32 64 128)
ALPHAS=(0.0001 0.001 0.01)
TASK_ID=${SLURM_ARRAY_TASK_ID}
HS_INDEX=$(( TASK_ID / 3 ))
ALPHA_INDEX=$(( TASK_ID % 3 ))
HIDDEN_SIZE=${HIDDEN_SIZES[$HS_INDEX]}
ALPHA=${ALPHAS[$ALPHA_INDEX]}
echo "Hidden size: ${HIDDEN_SIZE}"
echo "Alpha: ${ALPHA}"
python breast_cancer_mlp.py "${HIDDEN_SIZE}" "${ALPHA}"
```

Make the script executable:
chmod +x run_breast_cancer_array.sh

### 5.3 Submitting the Array Job and Inspecting Results

Submit the job:

```bash
sbatch run_breast_cancer_array.sh
ls bc_mlp_*.out
cat bc_mlp_JOBID_0.out # inspect one output file
```
Each output file corresponds to one combination of hidden layer size and alpha, and prints:
* Hidden layer size.
* Alpha (regularization parameter).
* Classification accuracy on the test set.
Task for the students: collect the results into a table (e.g. in a spreadsheet or a small Python
script) with columns:
* hidden_size
* alpha
* accuracy
and identify the best hyperparameter combination.
Next try different max_iter and see how training time and convergence change.
Exploring Convergence and Training Time in MLP Classifiers
Teaching goal: "Try different max_iterand see how training time and convergence change."
The following is a nice little mini-experiment. Change one thing in breast_cancer_mlp.py:
themax_iter parameter of the MLPClassifier. You can explore this in two ways.
1. Simple Version: Editmax_iterDirectly in the Code
The original classifier definition:
```python
clf = MLPClassifier(
    hidden_layer_sizes=(hidden_layer_size,),
    alpha=alpha,
    max_iter=200,
    random_state=42
)
```

Students should change the max_itervalue to explore its impact:
* max_iter = 50
* max_iter = 200
* max_iter = 500
* max_iter = 1000
Then they re-run the jobs and observe:
* Whether the Convergence Warning appears
* Changes inaccuracy
* Changes intraining time(visible via SLURM logs)
This is the simplest way to see the effect of iteration count on optimization.
2. Passing max_iter as a Command-line Argument
For a more flexible experiment, modify the script to accept an optional max_iter argument.
Change the beginning of main():

```python
def main():
if len(sys.argv) < 3:
print("Usage: breast_cancer_mlp.py <hidden_layer_size> <alpha> [max_iter]")
sys.exit(1)
hidden_layer_size = int(sys.argv[1])
alpha = float(sys.argv[2])
if len(sys.argv) >= 4:
max_iter = int(sys.argv[3])
else:
max_iter = 200 # default
```
Then update the classifier definition:
```python
clf = MLPClassifier(
hidden_layer_sizes=(hidden_layer_size,),
alpha=alpha,
max_iter=max_iter,
random_state=42
)
```
And include it in the printed output:
```python
print(f"Hidden layer size: {hidden_layer_size}")
print(f"Alpha: {alpha}")
print(f"Max iter: {max_iter}")
print(f"Accuracy: {acc:.4f}")
```
Now students can run experiments like:
python breast_cancer_mlp.py 64 0.001 100
python breast_cancer_mlp.py 64 0.001 500
python breast_cancer_mlp.py 64 0.001 1000
This allows varying the number of iterations without editing the code each time.

3. Optional: Measuring Training Time
To quantify the effect of max_iteron training time, add:
```python
import time
start = time.perf_counter()
clf.fit(X_train, y_train)
fit_time = time.perf_counter() - start
print(f"Fit time (s): {fit_time:.3f}")
```
This clearly shows:
* Whether the model converges
* How long training takes
* Whether accuracy improves with more iterations
