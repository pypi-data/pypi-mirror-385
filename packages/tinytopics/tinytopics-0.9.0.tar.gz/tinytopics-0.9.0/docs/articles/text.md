# Text data topic modeling


<!-- `.md` and `.py` files are generated from the `.qmd` file. Please edit that file. -->

!!! tip

    Prerequisite: run [text.R](static/example-text/text.R)
    to get the count data and the model fitted with fastTopics for comparison:

    ```bash
    Rscript docs/articles/static/example-text/text.R
    ```

    To run the code from this article as a Python script:

    ```bash
    python3 examples/text.py
    ```

We show a minimal example of text data topic modeling using tinytopics.
The NIPS dataset contains a count matrix for 2483 research papers on
14036 terms. More details about the dataset can be found in [this GitHub
repo](https://github.com/stephenslab/fastTopics-experiments).

## Import tinytopics

``` python
from safetensors.numpy import load_file as load_safetensors_numpy
from safetensors.torch import load_file as load_safetensors_torch

import tinytopics as tt
```

## Read count data

``` python
def read_safetensors_numpy(file_path):
    tensors = load_safetensors_numpy(file_path)
    first_key = next(iter(tensors))
    return tensors[first_key]

def read_safetensors_torch(file_path):
    tensors = load_safetensors_torch(file_path)
    first_key = next(iter(tensors))
    return tensors[first_key]
```

``` python
X = read_safetensors_torch("counts.safetensors")

with open("terms.txt") as file:
    terms = [line.strip() for line in file]
```

## Fit topic model

``` python
tt.set_random_seed(42)

k = 10
model, losses = tt.fit_model(X, k)
tt.plot_loss(losses, output_file="loss.png")
```

![](images/text/loss.png)

## Post-process results

We first load the L and F matrices fitted by fastTopics and then compare
them with the tinytopics model. For easier visual comparison, we will
try to “align” the topics fitted by tinytopics with those from
fastTopics, and sort documents grouped by dominant topics.

``` python
L_tt = model.get_normalized_L().numpy()
F_tt = model.get_normalized_F().numpy()

L_ft = read_safetensors_numpy("L_fastTopics.safetensors")
F_ft = read_safetensors_numpy("F_fastTopics.safetensors")

aligned_indices = tt.align_topics(F_ft, F_tt)
F_aligned_tt = F_tt[aligned_indices]
L_aligned_tt = L_tt[:, aligned_indices]

sorted_indices_ft = tt.sort_documents(L_ft)
L_sorted_ft = L_ft[sorted_indices_ft]
sorted_indices_tt = tt.sort_documents(L_aligned_tt)
L_sorted_tt = L_aligned_tt[sorted_indices_tt]
```

## Visualize results

Use Structure plot to check the document-topic distributions:

``` python
tt.plot_structure(
    L_sorted_ft,
    title="fastTopics document-topic distributions (sorted)",
    output_file="L-fastTopics.png",
)
```

![](images/text/L-fastTopics.png)

``` python
tt.plot_structure(
    L_sorted_tt,
    title="tinytopics document-topic distributions (sorted and aligned)",
    output_file="L-tinytopics.png",
)
```

![](images/text/L-tinytopics.png)

Plot the probability of top 15 terms in each topic from both models to
inspect their concordance:

``` python
tt.plot_top_terms(
    F_ft,
    n_top_terms=15,
    term_names = terms,
    title="fastTopics top terms per topic",
    output_file="F-top-terms-fastTopics.png",
)
```

![](images/text/F-fastTopics.png)

``` python
tt.plot_top_terms(
    F_aligned_tt,
    n_top_terms=15,
    term_names = terms,
    title="tinytopics top terms per topic (aligned)",
    output_file="F-top-terms-tinytopics.png",
)
```

![](images/text/F-tinytopics.png)
