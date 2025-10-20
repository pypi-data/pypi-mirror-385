# A few custom matplotlib colormaps
![Continuous integration](https://github.com/mfschubert/ccmaps/actions/workflows/build-ci.yml/badge.svg)
![PyPI version](https://img.shields.io/pypi/v/ccmaps)

This package includes custom matplotlib colormaps that I have found to be useful. These currently include:
 - `WBGYR` (white-blue-green-yellow-red), which is often used to plot electromagnetic field intensities ([1](https://projects.iq.harvard.edu/files/muri_metasurfaces/files/1190.full_.pdf), [2](https://github.com/flexcompute/metalens/blob/main/Metalens_Simulate_Single.ipynb)).
 - `BKR` (white-blue-black-red-white), appropriate for electromagnetic field amplitudes.
 - `cmap_for_wavelength`, which generates a colormap that interpolates between the chosen background color and the color for the specified wavelength (in nanometers).

## Install
```
pip install ccmaps
```

## Examples
![cmaps](https://github.com/mfschubert/ccmaps/blob/main/docs/img/cmaps.png?raw=true)
