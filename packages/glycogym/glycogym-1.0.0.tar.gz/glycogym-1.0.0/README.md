<p align="center">
  <img src="/docs/imgs/glycogym_banner.svg" style="height:100%;width:100%;">
</p>

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17313055.svg)](https://doi.org/10.5281/zenodo.17313055)
![testing](https://github.com/bojarlab/glycogym/actions/workflows/test.yaml/badge.svg)

Glycan property prediction is an increasingly popular area of machine learning research. Supervised learning approaches have shown promise in glycan modeling; however, the current literature is fragmented regarding datasets and standardized evaluation techniques, hampering progress in understanding these complex, branched carbohydrates that play crucial roles in biological processes. To facilitate progress, we introduce GlycoGym, a comprehensive benchmark suite containing six biologically relevant supervised learning tasks spanning different domains of glycobiology: glycosylation linkage identification, tissue expression prediction, taxonomy classification, tandem mass spectrometry fragmentation prediction, lectin-glycan interaction modeling, and structural property estimation. We curate tasks into specific training, validation, and test splits using multi-class stratification to ensure that each task tests biologically relevant generalization that transfers to real-life glycan property prediction scenarios. GlycoGym will help the machine learning community to focus their efforts on scientifically relevant glycan prediction problems.

## Installation

You can install GlycoGym via pip:

```bash
pip install glycogym
```

## Usage

The main intention of this package is to build the benchmark for the upload to Zenodo, everytime the datasets with `glycowork` or `GlyContact` get significantly updated.

But one can also use it to build local versions of the benchmark during the update cycles of the Zenodo repository.

```python
from glycogym import build_glycosylation, build_taxonomy, build_tissue, build_lgi

df, mapping = build_glycosylation()
df_taxonomy = build_taxonomy("Kingdom")
df_tissue = build_tissue()
df_r, df_cl, df_cg = build_lgi()
```

### Tandem Mass Spectrometry Fragmentation Prediction

One special dataset is the MS fragmentation prediction dataset, which can be built as follows:

```python
from glycogym import build_spectrum

df_ms = build_spectrum(root="path/to/folder/with/pkl/files")
```

Here, the root argument defined the path to the folder containing the `.pkl` files comprising the MS fragmentation prediction dataset by CandyCrunch, which can be downloaded from [here](https://zenodo.org/record/7940047).

### Structural Property Estimation

The second dataset that requires special handling is the structural property estimation dataset. Currently, it needs to be build from the GlyContact package. That can be installed with the following command:

```bash
pip install -e git+https://github.com/lthomes/glycontact.git#egg=glycontact[ml]
```

Then, the dataset can be built as follows:

```python
from glycontact.learning import create_dataset

train, val, test = create_dataset(splits=[0.7, 0.2, 0.1])
```

## Zenodo

The latest version of the GlycoGym benchmark can be found on Zenodo: https://doi.org/10.5281/zenodo.17313055

## Citation

tbd
