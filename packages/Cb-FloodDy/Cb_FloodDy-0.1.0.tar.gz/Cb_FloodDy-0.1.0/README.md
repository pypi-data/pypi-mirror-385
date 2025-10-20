# Cb_FloodDy

Cluster-based flood dynamics utilities and models.

## Install (editable)
```bash
pip install -e .
```

## Quick start

```python
# Access submodules directly
from Cb_FloodDy import voronoi_clusters, model_training, model_prediction, bayesian_opt_tuning

# Example: generate Voronoi clusters (see voronoi_clusters module for data expectations)
# polygons = voronoi_clusters.generate_voronoi_clusters_and_empty_areas(station_coords, floodmap_union)
```

## CLI
After installation:
```bash
cbf-train    # calls Cb_FloodDy.model_training.main()
cbf-predict  # calls Cb_FloodDy.model_prediction.main()
cbf-tune     # calls Cb_FloodDy.bayesian_opt_tuning.main()
```

> Note: the underlying modules should define a `main()` function for these CLI commands.
