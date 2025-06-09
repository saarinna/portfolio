## Content

- [gym_accessibility_helsinki.ipynb](gym_accessibility_helsinki.ipynb/): A python script that analyzes the accessibility of free outdoor gyms in Helsinki to understand how easily residents can reach these facilities within a 15-minute walk. Using open spatial data and network analysis, it combines population distribution, gym locations, and city district boundaries with detailed street network travel times. It demonstrates spatial data processing, transport network analysis, and interactive mapping in Python, supporting urban planning and public health initiatives.

### What it does
- Calculates walking travel times from population grid centroids to free gyms using OpenStreetMap data and r5py
- Visualizes accessibility on multiple scales: population grids and city districts
- Identifies districts with high and low access to free gyms, helping to pinpoint areas for urban health improvement
- Includes spatial statistical analysis (Moran's I) to understand spatial clustering of accessibility