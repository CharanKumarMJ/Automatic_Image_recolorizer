# Automatic Image Recolorizer

This project implements an automatic image colorization pipeline using:

- SLIC Superpixels
- FFT-based texture features
- Support Vector Regression (SVR)
- Markov Random Field (MRF) smoothing

## Folder Structure
- data/        : Training and testing images
- models/      : Trained SVR models
- train_svr.py : Training script
- test_svr.py  : Colorization script

## How to Run
```bash
python train_svr.py
python test_svr.py data/test/test_image.jpg
