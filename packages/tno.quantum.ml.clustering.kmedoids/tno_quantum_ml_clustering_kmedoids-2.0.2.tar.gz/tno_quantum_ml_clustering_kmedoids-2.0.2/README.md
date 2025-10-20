# TNO Quantum: ML - Classification - KMedoid

TNO Quantum provides generic software components aimed at facilitating the development
of quantum applications.

This package implements a scikit-learn compatible kmedoid clustering.

*Limitations in (end-)use: the content of this software package may solely be used for applications 
that comply with international export control laws.*

## Documentation

Documentation of the `tno.quantum.ml.clustering.kmedoids` package can be found [here](https://tno-quantum.github.io/documentation/).


## Install

Easily install the `tno.quantum.ml.clustering.kmedoids` package using pip:

```console
$ python -m pip install tno.quantum.ml.clustering.kmedoid
```

## Example

The K-medoids clustering can be used as shown in the following example.

- Note: This example requires `tno.quantum.optimization.solvers[dwave]` and `tno.quantum.ml.datasets` which can be installed along the package using:

  ```console
  $ python -m pip install tno.quantum.ml.clustering.kmedoids[example]
  ```

```python
import matplotlib.pyplot as plt
import numpy as np
from tno.quantum.ml.datasets import get_blobs_clustering_dataset

from tno.quantum.ml.clustering.kmedoids import QKMedoids

# Generate sample data
n_centers = 6
X, true_labels = get_blobs_clustering_dataset(
    n_samples=120, n_features=2, n_centers=n_centers
)

# Create QKMedoids object and fit
cobj = QKMedoids(
    n_clusters=n_centers,
    solver_config={
        "name": "simulated_annealing_solver",
        "options": {"random_state": 42},
    },
)
pred_labels = cobj.fit_predict(X)

# Plot results
fig, ax = plt.subplots(nrows=1, ncols=1)
unique_labels = np.unique(pred_labels)
colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
for k, col in zip(unique_labels, colors):
    class_member_mask = cobj.labels_ == k
    xy = X[class_member_mask]
    x, y = np.split(xy, 2, axis=1)
    ax.plot(x, y, "o", mfc=tuple(col), mec="k", ms=6)

x_centers, y_centers = np.split(cobj.cluster_centers_, 2, axis=1)
ax.plot(x_centers, y_centers, "o", mfc="cyan", mec="k", ms=6)

ax.set_title("Quantum KMedoids clustering")
plt.show()
```

We refer to the documentation for more information regarding possible parameters.
