# MetaChat
## Brief introduction
MetaChat is a Python package to screen metabolic cell communication (MCC) from spatial multi-omics data of transcriptomics and metabolomics. 
It contains many intuitive visualization and downstream analysis tools, provides a great practical toolbox for biomedical researchers.

### Metabolic cell communication
Metabolic cell-cell communication (MCC) occurs when sensor proteins in the receiver cells detect metabolites in their environment, activating intracellular signaling events. There are three major potential sensors of metabolites: surface receptors, nuclear receptors, and transporters. Metabolites secreted from cells are either transported over short-range distances (a few cells) via diffusion through extracellular space, or over long-range distances via the bloodstream and the cerebrospinal fluid (CSF).

<img width="500" alt="image" src="https://github.com/SonghaoLuo/MetaChat/assets/138028157/f08f21de-eeae-4626-8fbe-c26a307ec225">

### MetaChatDB
MetaChatDB is a literature-supported database for metabolite-sensor interactions for both human and mouse. All the metabolite-sensor interactions are reported based on peer-reviewed publications. Specifically, we manually build MetaChatDB by integrating three high-quality databases (PDB, HMDB, UniProt) that are being continually updated.

<img width="500" alt="image" src="https://github.com/SonghaoLuo/MetaChat/assets/138028157/20e168c2-2409-47c4-881f-3b80d38326f3">

## Installation
### System requirements
Recommended operating systems: macOS or Linux. MetaChat was developed and tested on Linux and macOS.
### Python requirements
MetaChat was developed using python 3.9.
### Installation using `pip`
We suggest setting up MetaChat in a separate `mamba` or `conda` environment to prevent conflicts with other software dependencies. Create a new Python environment specifically for MetaChat and install the required libraries within it.

```bash
mamba create -n metachat_env python=3.9 r-base=4.3.2
mamba activate metachat_env
pip install metachat
```
if you use `conda`, `r-base=4.3.2` may not included in the channels. Instead, you can `r-base=4.3.1` in `conda`.

## Documentation, and Tutorials

For more realistic and simulation examples, please see MetaChat documentation that is available through the link https://metachat.readthedocs.io/en/latest/.

## Quick start
Let's get a quick start on using metachat to infer MCC by using simulation data generated from a PDE dynamic model.

### Import packages
```python
import os
import numpy as np
import pandas as pd
import scanpy as sc
import squidpy as sq
import matplotlib.pyplot as plt
import metachat as mc
```

### Setting work dictionary
To run the examples, you'll need to download the some pre-existing files in `docs/tutorials/simulated_data` folder and change your working directory to the `simulated_data` folder.

```python
os.chdir("your_path/simulated_data")
```

### Multi-omics data from simulation
```python
adata = sc.read("data/example1/adata_example1.h5ad")
```
This dataset consists of a metabolite `M1` and a sensor `S1`. Their spatial distributions are shown below:
```python
fig, ax = plt.subplots(1, 2, figsize = (8,4))
sq.pl.spatial_scatter(adata = adata, color = "M1", size = 80, cmap = "Blues", shape = None, ax = ax[0])
ax[0].invert_yaxis()
ax[0].set_box_aspect(1)
sq.pl.spatial_scatter(adata = adata, color = "S1", size = 80, cmap = "Reds", shape = None, ax = ax[1])
ax[1].invert_yaxis()
ax[1].set_box_aspect(1)
plt.show()
```
<img src="https://github.com/SonghaoLuo/MetaChat/assets/138028157/7176aabd-7e3e-4439-9f9c-9b0346fd5da8" alt="Spatial Distributions" width="600"/>

### Long-range channels (LRC)
Import the pre-defined long range channel and add it to the `adata` object.
```python
LRC_channel = np.load('data/example1/LRC_channel.npy')
adata.obs['LRC_type1_filtered'] = LRC_channel.flatten()
adata.obs['LRC_type1_filtered'] = adata.obs['LRC_type1_filtered'].astype('category')
```
It's spatial distribution are shown in orange color:
```python
fig, ax = plt.subplots(figsize = (3,3))
sq.pl.spatial_scatter(adata = adata, color = "LRC_type1_filtered", size = 80, shape = None, ax = ax)
ax.invert_yaxis()
ax.set_box_aspect(1)
plt.show()
```
<img src="https://github.com/SonghaoLuo/MetaChat/assets/138028157/c7cc5dbd-1725-4726-a973-8555cf4f6ad0" alt="Spatial Distributions" width="300"/>

### Metabolite-sensor database construction
We need to artificially create a simple database which must include three columns: 'Metabolite', 'Sensor', 'Long.Range.Channel', representing the metabolite name, the sensor name, and the type of long range channel that metabolites may be entered, respectively.  
In this example, we assume that the metabolite `M1` can communicate with proximal cells by short-range diffusion and with distal cells by long-range channel transport (`type1`).
```python
M_S_pair = [['M1', 'S1', 'type1']]
df_metasen = pd.DataFrame(M_S_pair)
df_metasen.columns = ['Metabolite', 'Sensor', 'Long.Range.Channel']
```

### Compute the cost matrix based on the long-range channels
To utilize flow-optimal transport, we need to compute the cost matrix depends mainly on two parameters:maximum communication distance (`dis_thr`) and long-range communication strength (`LRC_strength`).
```python
mc.pp.compute_costDistance(adata = adata,
                           LRC_type = ["type1"],
                           dis_thr = 10,
                           k_neighb = 5,
                           LRC_strength = 4,
                           plot = True,
                           spot_size = 1)
```

### Run the inference function
```python
mc.tl.metabolic_communication(adata = adata,
                              database_name = 'msdb_example1',
                              df_metasen = df_metasen,
                              LRC_type = ["type1"],
                              dis_thr = 15,
                              fot_weights = (1.0,0.0,0.0,0.0),
                              fot_eps_p = 0.25,
                              fot_rho = 1.0,
                              cost_type = 'euc')
```

### Compare MetaChat results with the PDE model
Comparative results showed that the distribution of M1-S1 inferred by MetaChat had a high correlation with that simulated by the PDE model.
```python
MCC_PDE = np.load('data/example1/pde_result.npy')
MCC_infer = adata.obsm['MetaChat-msdb_example1-sum-receiver']['r-M1-S1'].values.reshape(50,50)
```
```python
fig, ax = plt.subplots(1,2, figsize = (7,14))
ax[0].imshow(MCC_PDE[2].T, cmap='viridis', origin='lower')
ax[0].set_xlabel('x')
ax[0].set_ylabel('y')
ax[0].set_title('M1-S1 distribution from PDE')
ax[0].set_box_aspect(1)
ax[1].imshow(MCC_infer.T, cmap='viridis', origin='lower')
ax[1].set_xlabel('x')
ax[1].set_ylabel('y')
ax[1].set_title('M1-S1 distribution with LRC')
ax[1].set_box_aspect(1)
plt.tight_layout()
```
<img src="https://github.com/SonghaoLuo/MetaChat/assets/138028157/9aec37b3-a266-4d86-b486-5b6409c06293" alt="Spatial Distributions" width="600"/>  

## Reference
Luo, S., Almet, A.A., Nie, Q.. Spatial metabolic communication flow of single cells.
