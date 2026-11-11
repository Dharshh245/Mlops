# Reproducible ML experiment — Git + DVC + CML (Iris)

```
Mlops/
├── notebooks/iris_experiment.ipynb   (a) exploratory notebook, outputs included
├── src/
│   ├── get_data.py                   writes data/iris.csv (raw dataset)
│   ├── prepare.py                    (b) stage 1: stratified train/test split
│   ├── train.py                      (b) stage 2: RandomForest training
│   └── evaluate.py                   (b) stage 3: accuracy + macro-F1, confusion matrix
├── params.yaml                       (b) all hyper-parameters
├── dvc.yaml                          (d) pipeline definition
├── data/iris.csv                     (c) dataset, tracked by DVC (not Git)
├── .github/workflows/cml.yaml        (e) CI: reproduce + post report on PR
└── requirements.txt
```

All commands below are for **PowerShell on Windows**, run from inside the `Mlops` folder.

## 0. Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## (a) Notebook — baseline result

Open `notebooks/iris_experiment.ipynb` (`jupyter notebook`) and run all cells.

| Setting | Value |
|---|---|
| Model | RandomForestClassifier |
| Split | 70 / 30, stratified, `random_state=42` |
| `n_estimators`, `max_depth` | 100, 3 |
| **Accuracy** | **0.9111** |
| **F1 (macro)** | **0.9107** |

Setosa is classified perfectly; the 4 errors (out of 45) are between versicolor and virginica.

## (b) Scripts + params.yaml

The notebook is split into three scripts, each reading its section of `params.yaml`:

| Script | Reads | Writes |
|---|---|---|
| `src/prepare.py` | `data/iris.csv`, `prepare.*` | `data/prepared/train.csv`, `test.csv` |
| `src/train.py` | `train.csv`, `train.*` | `models/model.pkl` |
| `src/evaluate.py` | model, `test.csv` | `metrics.json`, `plots/confusion_matrix.png` |

Running them by hand gives the same numbers as the notebook:

```powershell
python src/prepare.py; python src/train.py; python src/evaluate.py
# {'accuracy': 0.9111, 'f1_macro': 0.9107}
```

## (c) Git + DVC, track the dataset, configure a remote

```powershell
git init
git branch -M main
dvc init
git commit -m "Initialize DVC"

python src/get_data.py          # writes data/iris.csv (already included)
dvc add data/iris.csv           # creates data/iris.csv.dvc + data/.gitignore
git add data/iris.csv.dvc data/.gitignore
git commit -m "Track Iris dataset with DVC"

# Remote: a local folder outside the repo
mkdir ..\dvc-storage
dvc remote add -d localremote ..\dvc-storage
git add .dvc/config
git commit -m "Configure DVC remote"
dvc push                        # uploads the dataset to the remote
```

Check: `git ls-files data` shows only `iris.csv.dvc` and `.gitignore`, not the CSV, and `..\dvc-storage` now has the cached file.

> For a cloud remote instead (lets CI `dvc pull`), e.g. DagsHub:
> `dvc remote add -d origin https://dagshub.com/<user>/<repo>.dvc` then
> `dvc remote modify origin --local auth basic`, `user`, `password <token>`.

## (d) Pipeline, `dvc repro`, change a param, compare

`dvc.yaml` defines `prepare → train → evaluate`, with deps, the params each stage uses, outputs, and `metrics.json` as a metric (`cache: false`, so Git tracks it).

```powershell
dvc repro                       # runs all 3 stages, writes dvc.lock
dvc dag                         # shows the pipeline graph
dvc metrics show
git add dvc.yaml dvc.lock params.yaml src notebooks metrics.json plots .gitignore requirements.txt README.md .github
git commit -m "Baseline pipeline: max_depth=3"
dvc push
```

Now change a parameter. In `params.yaml`, set `train.max_depth: 3` → `1`, then:

```powershell
dvc repro                       # 'prepare' is skipped (its params didn't change); train + evaluate rerun
dvc params diff
dvc metrics diff
```

Expected output:

```
Path         Param            HEAD  workspace
params.yaml  train.max_depth  3     1

Path          Metric    HEAD    workspace  Change
metrics.json  accuracy  0.9111  0.8889     -0.0222
metrics.json  f1_macro  0.9107  0.8888     -0.0219
```

The shallower trees (single splits) lose about 2 points of accuracy. `dvc repro` skipping `prepare` shows that DVC reruns only the stages whose deps or params changed.

## (e) GitHub Actions + CML report on a pull request

`.github/workflows/cml.yaml` runs on every PR to `main`. It installs the dependencies and gets the data (`dvc pull`, or regenerates the same file with `get_data.py` if the remote can't be reached from CI). It then runs `dvc repro` and builds a Markdown report with the metrics, the metrics and params diff against `main`, and the confusion matrix. `cml comment create` posts the report on the PR. It uses the built-in `GITHUB_TOKEN`, so no secrets are needed.

```powershell
# 1. Put the baseline on GitHub (create an empty repo "Mlops" first)
git checkout params.yaml        # back to max_depth: 3 if you still have the change
dvc repro
git remote add origin https://github.com/Dharshh245/Mlops.git
git push -u origin main

# 2. Experiment branch
git checkout -b exp/max-depth-1
# edit params.yaml: max_depth: 1
dvc repro
git add params.yaml dvc.lock metrics.json plots
git commit -m "Experiment: max_depth=1"
git push -u origin exp/max-depth-1
```

Open a pull request `exp/max-depth-1 → main`. The **CML experiment report** workflow runs, and a bot comment appears on the PR showing the metrics table, the diffs above, and the confusion matrix.

If the comment isn't posted, go to **Settings → Actions → General → Workflow permissions** and select **Read and write permissions**.
