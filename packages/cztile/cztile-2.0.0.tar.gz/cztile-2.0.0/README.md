# cztile - Python package to simplify the process of tiling arrays

This project provides simple-to-use tiling functionality for arrays. It is not linked directly to the CZI file format, but can be of use to process such images in an efficient and **tile-wise** manner, which is especially important when dealing with larger images.  

## Samples

The basic usage can be inferred from this sample notebook:  
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zeiss-microscopy/OAD/blob/master/jupyter_notebooks/cztile/cztile_2_0_0.ipynb)

## System setup

The current version of this toolbox only requires a fresh Python >= 3.9 installation.

## Supported Tiling Strategies

This package features the following tiling strategies:  

### AlmostEqualBorderFixedTotalAreaStrategy2D

This covers a total area with a minimal number of tiles of constant total area such that:

- the image area is completely covered by tiles and is filled up with as few tiles as possible
- the overlap/border between tiles is as small as possible, but it is ensured that at least a minimum border size is used
- all interior tiles have the same size
- a possible excess border is split among tiles and can lead to slightly different tile and border sizes at the edge  
- all interior tiles have at least a minimum border width/height on all sides  
- the edge tiles have zero border at the edge and at least the minimum border width on their inner sides.  
- The sizes of all non-zero borders differ at most by one pixel.  

![cztile - AlmostEqualBorderFixedTotalAreaStrategy2D](https://raw.githubusercontent.com/zeiss-microscopy/OAD/master/jupyter_notebooks/cztile/cztile_algo.png)

The core functionality is of course also available for 1D.  

The __AlmostEqualBorderFixedTotalAreaStrategy2D__ is based on the following algorithm:  

#### Inputs

Image width: ![equation](https://latex.codecogs.com/svg.image?W)  
Minimum interior border width (left or right): ![equation](https://latex.codecogs.com/svg.image?%5Cdelta)  
Fixed total tile width: ![equation](https://latex.codecogs.com/svg.image?w)  

#### Calculation of tile positions and borders

**Case 1:** ![equation](https://latex.codecogs.com/svg.image?W%3Cw)  
There is no solution. Fail!  

**Case 2:** ![equation](https://latex.codecogs.com/svg.image?W=w)  
Use a single tile with no borders.  

**Case 3:** ![equation](https://latex.codecogs.com/svg.image?W%3Ew)  
Maximum inner tile width of edge tiles: ![equation](https://latex.codecogs.com/svg.image?%5Chat%7B%5Comega%7D=w-%5Cdelta)  
Maximum inner tile width of interior tiles: ![equation](https://latex.codecogs.com/svg.image?%5Chat%7Bw%7D=w-2%5Cdelta)  
Total interior tile width: ![equation](https://latex.codecogs.com/svg.image?%5COmega=%5Cmax%5C%7B%5C0,W-2%5C,%5Chat%7B%5Comega%7D%5C%7D)  
Number of tiles: ![equation](https://latex.codecogs.com/svg.image?N=%5Cleft%5Clceil%7B%5COmega/%5Chat%7Bw%7D%7D%5Cright%5Crceil&plus;2)  
Excess border: ![equation](https://latex.codecogs.com/svg.image?E=2%5Chat%7B%5Comega%7D&plus;(N-2)%5Chat%7Bw%7D-W)  
Total number of non-zero left and right borders: ![equation](https://latex.codecogs.com/svg.image?%5Cnu=2(N-1))  
Fractional excess border: ![equation](https://latex.codecogs.com/svg.image?e=E/%5Cnu)  
The first non-zero border has index ![equation](https://latex.codecogs.com/svg.image?j=1), the last has index ![equation](https://latex.codecogs.com/svg.image?j=%5Cnu). Tile ![equation](https://latex.codecogs.com/svg.image?i) is surrounded by the borders with index ![equation](https://latex.codecogs.com/svg.image?2i) and ![equation](https://latex.codecogs.com/svg.image?2i&plus;1).  
Cumulative excess border for all borders up to border ![equation](https://latex.codecogs.com/svg.image?j): ![equation](https://latex.codecogs.com/svg.image?E_j=%5Cleft%5Clfloor%7Bje%7D%5Cright%5Crfloor) for ![equation](https://latex.codecogs.com/svg.image?j=0,...,%5Cnu)  
Cumulative border for all borders up to border ![equation](https://latex.codecogs.com/svg.image?j): ![equation](https://latex.codecogs.com/svg.image?%5CDelta_j=E_j&plus;j%5Cdelta) for ![equation](https://latex.codecogs.com/svg.image?j=0,...,%5Cnu)  
Tile boundaries: ![equation](https://latex.codecogs.com/svg.image?x_i=%5Cbegin%7Bcases%7D0%7Ci=0%5C%5Ci%5C,w-%5CDelta_%7B2i-1%7D%7Ci=1,...,N-1%5C%5CW%7Ci=N%5Cend%7Bcases%7D)  
Tile ![equation](https://latex.codecogs.com/svg.image?i) for ![equation](https://latex.codecogs.com/svg.image?i=0,...,N-1):  

- Left-most pixel of inner tile: ![equation](https://latex.codecogs.com/svg.image?L_i=x_i)  
- Right-most pixel of inner tile: ![equation](https://latex.codecogs.com/svg.image?R_i=x_%7Bi&plus;1%7D-1)  
- Inner tile width: ![equation](https://latex.codecogs.com/svg.image?w_i=x_%7Bi&plus;1%7D-x_i)  
- Total border width: ![equation](https://latex.codecogs.com/svg.image?b_i=w-w_i)  
- Left border width: ![equation](https://latex.codecogs.com/svg.image?%5Clambda_i=%5Cbegin%7Bcases%7D0%7Ci=0%5C%5C%5CDelta_%7B2i%7D-%5CDelta_%7B2i-1%7D%7Ci=1,...,N-2%5C%5Cb_i%7Ci=N-1%5Cend%7Bcases%7D)  
- Right border width: ![equation](https://latex.codecogs.com/svg.image?%5Crho_i=b_i-%5Clambda_i)  
- Left-most border pixel: ![equation](https://latex.codecogs.com/svg.image?%5Cl_i=L_i-%5Clambda_i)  
- Right-most-border pixel: ![equation](https://latex.codecogs.com/svg.image?r_i=R_i&plus;%5Crho_i)

## Disclaimer

The libary and the notebook are free to use for everybody. Carl Zeiss Microscopy GmbH undertakes no warranty concerning the use of those tools. Use them at your own risk.

**By using any of those examples you agree to this disclaimer.**

Version: 2025.05.20

Copyright (c) 2025 Carl Zeiss AG, Germany. All Rights Reserved.
