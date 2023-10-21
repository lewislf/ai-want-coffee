# Overview

This project aims to create a neural network that guides the coffee-making process based on object identification in the kitchen. It uses YOLO for real-time object detection and LLAVA for further processing.

Table of Contents
- Prerequisites
- Clone the repository
- Installation
- Running the Prediction Script

# Installation
## 1. Prerequisites

- Make sure to install `GPU` drivers in your system if you want to use `GPU` .
- Make sure you have [MS Build tools](https://aka.ms/vs/17/release/vs_BuildTools.exe) installed in system if using windows. 
- [Download git for windows](https://git-scm.com/download/win) if not installed.

## 2. Clone the repository
``` shell
# ultralytics
https://github.com/ultralytics/ultralytics.git
# ai-want-coffee
https://github.com/lewislf/ai-want-coffee.git
```

## 3. Installation
```shell
# Using the env is optional; you can proceed without it if you prefer.
python -m venv AI-Want-Coffee-env
AI-Want-Coffee-env\Scripts\activate
pip install numpy Cython 
pip install lap
pip install -e git+https://github.com/samson-wang/cython_bbox.git#egg=cython-bbox

pip install asone onnxruntime-gpu==1.12.1
pip install super-gradients==3.1.3
# for CPU
pip install torch torchvision

# for GPU
pip install torch torchvision --extra-index-url https://download.pytorch.org/whl/cu113
or
pip install torch==1.10.1+cu113 torchvision==0.11.2+cu113 torchaudio===0.10.1+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html
```

## 4. Running the Prediction Script
```shell
# Navigate to the ai-want-coffee repository and execute the following:
python predict.py
# Note: You may need to change the filename in the script to match the video you want to analyze.
```
