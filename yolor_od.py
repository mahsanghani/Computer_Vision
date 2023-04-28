# -*- coding: utf-8 -*-
"""yolor-OD.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18M6-FlJDxqnqcoBiGor40uvKa2FCHSiK

# How to Train YOLOR on Custom Objects

This tutorial is based on the [YOLOR repository](https://github.com/WongKinYiu/yolor) by [Wong Kin-Yiu](https://github.com/WongKinYiu). This notebook shows training on **your own custom objects**. Many thanks to Wong for putting this repository together - we hope that in combination with clean data management tools at Roboflow, this technologoy will become easily accessible to any developer wishing to use computer vision in their projects.

### Accompanying Blog Post

We recommend that you follow along in this notebook while reading the blog post on [How to Train YOLOR](blog.roboflow.com/how-to-train-yolor-on-a-custom-dataset/), concurrently.

### Steps Covered in this Tutorial

In this tutorial, we will walk through the steps required to train YOLOR on your custom objects. We use a [public blood cell detection dataset](https://public.roboflow.ai/object-detection/bccd), which is open source and free to use. You can also use this notebook on your own data.

To train our detector we take the following steps:

* Install YOLOR dependencies
* Download custom YOLOR object detection data
* Prepare Pre-Trained Weights for YOLOR
* Run YOLOR training
* Evaluate YOLOR performance
* Visualize YOLOR training data
* Run YOLOR inference on test images
* Export saved YOLOR weights for future inference

### **About**

[Roboflow](https://roboflow.com) enables teams to deploy custom computer vision models quickly and accurately. Convert data from to annotation format, assess dataset health, preprocess, augment, and more. It's free for your first 1000 source images.

**Looking for a vision model available via API without hassle? Try Roboflow Train.**

![Roboflow Wordmark](https://i.imgur.com/dcLNMhV.png)

#Install Dependencies

_(Remember to choose GPU in Runtime if not already selected. Runtime --> Change Runtime Type --> Hardware accelerator --> GPU)_
"""

# Commented out IPython magic to ensure Python compatibility.
# clone YOLOR repository
!git clone https://github.com/roboflow-ai/yolor
# %cd yolor
!git reset --hard eb3ef0b7472413d6740f5cde39beb1a2f5b8b5d1

# Install necessary dependencies
!pip install -qr requirements.txt

# Commented out IPython magic to ensure Python compatibility.
# Install Mish CUDA
!git clone https://github.com/JunnYu/mish-cuda
# %cd mish-cuda
!git reset --hard 6f38976064cbcc4782f4212d7c0c5f6dd5e315a8
!python setup.py build install
# %cd ..

# Commented out IPython magic to ensure Python compatibility.
# Install PyTorch Wavelets
!sudo apt-get install git-lfs
!git lfs install
!git clone https://github.com/fbcotter/pytorch_wavelets
# %cd pytorch_wavelets
!pip install .
# %cd ..

"""# Download Correctly Formatted Custom Dataset 

We'll download our dataset from Roboflow. Use the "**YOLOv5 PyTorch**" export format. Note that the Ultralytics implementation calls for a YAML file defining where your training and test data is. The Roboflow export also writes this format for us.

To get your data into Roboflow, follow the [Getting Started Guide](https://blog.roboflow.ai/getting-started-with-roboflow/).

![YOLOv5 PyTorch export](https://i.imgur.com/5vr9G2u.png)

"""

# follow the link below to get your download code from from Roboflow
# !pip install -q roboflow
# from roboflow import Roboflow
# rf = Roboflow(model_format="yolov5", notebook="roboflow-yolor")

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/yolov5
!pip install roboflow

from roboflow import Roboflow
rf = Roboflow(api_key="0a4WwzoVWX7OLQHdybod")
project = rf.workspace("joseph-nelson").project("bccd")
dataset = project.version(4).download("yolov5")

# Commented out IPython magic to ensure Python compatibility.
# this is the YAML file Roboflow wrote for us that we're loading into this notebook with our data
# %cat {dataset.location}/data.yaml

"""# Prepare Pre-Trained Weights for YOLOR"""

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/yolor
!bash scripts/get_pretrain.sh

"""# Write YOLOR Configuration"""

import yaml
with open(dataset.location + "/data.yaml") as f:
    dataMap = yaml.safe_load(f)

num_classes = len(dataMap['names'])
num_filters = (num_classes + 5) * 3
from IPython.core.magic import register_line_cell_magic

@register_line_cell_magic
def writetemplate(line, cell):
    with open(line, 'w') as f:
        f.write(cell.format(**globals()))

# Commented out IPython magic to ensure Python compatibility.
# %%writetemplate /content/yolor/cfg/yolor_p6.cfg
# 
# [net]
# batch=64
# subdivisions=8
# width=1280
# height=1280
# channels=3
# momentum=0.949
# decay=0.0005
# angle=0
# saturation = 1.5
# exposure = 1.5
# hue=.1
# 
# learning_rate=0.00261
# burn_in=1000
# max_batches = 500500
# policy=steps
# steps=400000,450000
# scales=.1,.1
# 
# mosaic=1
# 
# 
# # ============ Backbone ============ #
# 
# # Stem 
# 
# # P1
# 
# # Downsample
# 
# # 0
# [reorg]
# 
# [convolutional]
# batch_normalize=1
# filters=64
# size=3
# stride=1
# pad=1
# activation=silu
# 
# 
# # P2
# 
# # Downsample
# 
# [convolutional]
# batch_normalize=1
# filters=128
# size=3
# stride=2
# pad=1
# activation=silu
# 
# # Split
# 
# [convolutional]
# batch_normalize=1
# filters=64
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [route]
# layers = -2
# 
# [convolutional]
# batch_normalize=1
# filters=64
# size=1
# stride=1
# pad=1
# activation=silu
# 
# # Residual Block
# 
# [convolutional]
# batch_normalize=1
# filters=64
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=64
# size=3
# stride=1
# pad=1
# activation=silu
# 
# [shortcut]
# from=-3
# activation=linear
# 
# [convolutional]
# batch_normalize=1
# filters=64
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=64
# size=3
# stride=1
# pad=1
# activation=silu
# 
# [shortcut]
# from=-3
# activation=linear
# 
# [convolutional]
# batch_normalize=1
# filters=64
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=64
# size=3
# stride=1
# pad=1
# activation=silu
# 
# [shortcut]
# from=-3
# activation=linear
# 
# # Transition first
# #
# #[convolutional]
# #batch_normalize=1
# #filters=64
# #size=1
# #stride=1
# #pad=1
# #activation=silu
# 
# # Merge [-1, -(3k+3)]
# 
# [route]
# layers = -1,-12
# 
# # Transition last
# 
# # 16 (previous+6+3k)
# [convolutional]
# batch_normalize=1
# filters=128
# size=1
# stride=1
# pad=1
# activation=silu
# 
# 
# # P3
# 
# # Downsample
# 
# [convolutional]
# batch_normalize=1
# filters=256
# size=3
# stride=2
# pad=1
# activation=silu
# 
# # Split
# 
# [convolutional]
# batch_normalize=1
# filters=128
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [route]
# layers = -2
# 
# [convolutional]
# batch_normalize=1
# filters=128
# size=1
# stride=1
# pad=1
# activation=silu
# 
# # Residual Block
# 
# [convolutional]
# batch_normalize=1
# filters=128
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=128
# size=3
# stride=1
# pad=1
# activation=silu
# 
# [shortcut]
# from=-3
# activation=linear
# 
# [convolutional]
# batch_normalize=1
# filters=128
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=128
# size=3
# stride=1
# pad=1
# activation=silu
# 
# [shortcut]
# from=-3
# activation=linear
# 
# [convolutional]
# batch_normalize=1
# filters=128
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=128
# size=3
# stride=1
# pad=1
# activation=silu
# 
# [shortcut]
# from=-3
# activation=linear
# 
# [convolutional]
# batch_normalize=1
# filters=128
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=128
# size=3
# stride=1
# pad=1
# activation=silu
# 
# [shortcut]
# from=-3
# activation=linear
# 
# [convolutional]
# batch_normalize=1
# filters=128
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=128
# size=3
# stride=1
# pad=1
# activation=silu
# 
# [shortcut]
# from=-3
# activation=linear
# 
# [convolutional]
# batch_normalize=1
# filters=128
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=128
# size=3
# stride=1
# pad=1
# activation=silu
# 
# [shortcut]
# from=-3
# activation=linear
# 
# [convolutional]
# batch_normalize=1
# filters=128
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=128
# size=3
# stride=1
# pad=1
# activation=silu
# 
# [shortcut]
# from=-3
# activation=linear
# 
# # Transition first
# #
# #[convolutional]
# #batch_normalize=1
# #filters=128
# #size=1
# #stride=1
# #pad=1
# #activation=silu
# 
# # Merge [-1, -(3k+3)]
# 
# [route]
# layers = -1,-24
# 
# # Transition last
# 
# # 43 (previous+6+3k)
# [convolutional]
# batch_normalize=1
# filters=256
# size=1
# stride=1
# pad=1
# activation=silu
# 
# 
# # P4
# 
# # Downsample
# 
# [convolutional]
# batch_normalize=1
# filters=384
# size=3
# stride=2
# pad=1
# activation=silu
# 
# # Split
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [route]
# layers = -2
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=1
# stride=1
# pad=1
# activation=silu
# 
# # Residual Block
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=3
# stride=1
# pad=1
# activation=silu
# 
# [shortcut]
# from=-3
# activation=linear
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=3
# stride=1
# pad=1
# activation=silu
# 
# [shortcut]
# from=-3
# activation=linear
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=3
# stride=1
# pad=1
# activation=silu
# 
# [shortcut]
# from=-3
# activation=linear
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=3
# stride=1
# pad=1
# activation=silu
# 
# [shortcut]
# from=-3
# activation=linear
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=3
# stride=1
# pad=1
# activation=silu
# 
# [shortcut]
# from=-3
# activation=linear
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=3
# stride=1
# pad=1
# activation=silu
# 
# [shortcut]
# from=-3
# activation=linear
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=3
# stride=1
# pad=1
# activation=silu
# 
# [shortcut]
# from=-3
# activation=linear
# 
# # Transition first
# #
# #[convolutional]
# #batch_normalize=1
# #filters=192
# #size=1
# #stride=1
# #pad=1
# #activation=silu
# 
# # Merge [-1, -(3k+3)]
# 
# [route]
# layers = -1,-24
# 
# # Transition last
# 
# # 70 (previous+6+3k)
# [convolutional]
# batch_normalize=1
# filters=384
# size=1
# stride=1
# pad=1
# activation=silu
# 
# 
# # P5
# 
# # Downsample
# 
# [convolutional]
# batch_normalize=1
# filters=512
# size=3
# stride=2
# pad=1
# activation=silu
# 
# # Split
# 
# [convolutional]
# batch_normalize=1
# filters=256
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [route]
# layers = -2
# 
# [convolutional]
# batch_normalize=1
# filters=256
# size=1
# stride=1
# pad=1
# activation=silu
# 
# # Residual Block
# 
# [convolutional]
# batch_normalize=1
# filters=256
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=256
# size=3
# stride=1
# pad=1
# activation=silu
# 
# [shortcut]
# from=-3
# activation=linear
# 
# [convolutional]
# batch_normalize=1
# filters=256
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=256
# size=3
# stride=1
# pad=1
# activation=silu
# 
# [shortcut]
# from=-3
# activation=linear
# 
# [convolutional]
# batch_normalize=1
# filters=256
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=256
# size=3
# stride=1
# pad=1
# activation=silu
# 
# [shortcut]
# from=-3
# activation=linear
# 
# # Transition first
# #
# #[convolutional]
# #batch_normalize=1
# #filters=256
# #size=1
# #stride=1
# #pad=1
# #activation=silu
# 
# # Merge [-1, -(3k+3)]
# 
# [route]
# layers = -1,-12
# 
# # Transition last
# 
# # 85 (previous+6+3k)
# [convolutional]
# batch_normalize=1
# filters=512
# size=1
# stride=1
# pad=1
# activation=silu
# 
# 
# # P6
# 
# # Downsample
# 
# [convolutional]
# batch_normalize=1
# filters=640
# size=3
# stride=2
# pad=1
# activation=silu
# 
# # Split
# 
# [convolutional]
# batch_normalize=1
# filters=320
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [route]
# layers = -2
# 
# [convolutional]
# batch_normalize=1
# filters=320
# size=1
# stride=1
# pad=1
# activation=silu
# 
# # Residual Block
# 
# [convolutional]
# batch_normalize=1
# filters=320
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=320
# size=3
# stride=1
# pad=1
# activation=silu
# 
# [shortcut]
# from=-3
# activation=linear
# 
# [convolutional]
# batch_normalize=1
# filters=320
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=320
# size=3
# stride=1
# pad=1
# activation=silu
# 
# [shortcut]
# from=-3
# activation=linear
# 
# [convolutional]
# batch_normalize=1
# filters=320
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=320
# size=3
# stride=1
# pad=1
# activation=silu
# 
# [shortcut]
# from=-3
# activation=linear
# 
# # Transition first
# #
# #[convolutional]
# #batch_normalize=1
# #filters=320
# #size=1
# #stride=1
# #pad=1
# #activation=silu
# 
# # Merge [-1, -(3k+3)]
# 
# [route]
# layers = -1,-12
# 
# # Transition last
# 
# # 100 (previous+6+3k)
# [convolutional]
# batch_normalize=1
# filters=640
# size=1
# stride=1
# pad=1
# activation=silu
# 
# # ============ End of Backbone ============ #
# 
# # ============ Neck ============ #
# 
# # CSPSPP
# 
# [convolutional]
# batch_normalize=1
# filters=320
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [route]
# layers = -2
# 
# [convolutional]
# batch_normalize=1
# filters=320
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=1
# pad=1
# filters=320
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=320
# size=1
# stride=1
# pad=1
# activation=silu
# 
# ### SPP ###
# [maxpool]
# stride=1
# size=5
# 
# [route]
# layers=-2
# 
# [maxpool]
# stride=1
# size=9
# 
# [route]
# layers=-4
# 
# [maxpool]
# stride=1
# size=13
# 
# [route]
# layers=-1,-3,-5,-6
# ### End SPP ###
# 
# [convolutional]
# batch_normalize=1
# filters=320
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=1
# pad=1
# filters=320
# activation=silu
# 
# [route]
# layers = -1, -13
# 
# # 115 (previous+6+5+2k)
# [convolutional]
# batch_normalize=1
# filters=320
# size=1
# stride=1
# pad=1
# activation=silu
# 
# # End of CSPSPP
# 
# 
# # FPN-5
# 
# [convolutional]
# batch_normalize=1
# filters=256
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [upsample]
# stride=2
# 
# [route]
# layers = 85
# 
# [convolutional]
# batch_normalize=1
# filters=256
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [route]
# layers = -1, -3
# 
# [convolutional]
# batch_normalize=1
# filters=256
# size=1
# stride=1
# pad=1
# activation=silu
# 
# # Split
# 
# [convolutional]
# batch_normalize=1
# filters=256
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [route]
# layers = -2
# 
# # Plain Block
# 
# [convolutional]
# batch_normalize=1
# filters=256
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=1
# pad=1
# filters=256
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=256
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=1
# pad=1
# filters=256
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=256
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=1
# pad=1
# filters=256
# activation=silu
# 
# # Merge [-1, -(2k+2)]
# 
# [route]
# layers = -1, -8
# 
# # Transition last
# 
# # 131 (previous+6+4+2k)
# [convolutional]
# batch_normalize=1
# filters=256
# size=1
# stride=1
# pad=1
# activation=silu
# 
# 
# # FPN-4
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [upsample]
# stride=2
# 
# [route]
# layers = 70
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [route]
# layers = -1, -3
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=1
# stride=1
# pad=1
# activation=silu
# 
# # Split
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [route]
# layers = -2
# 
# # Plain Block
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=1
# pad=1
# filters=192
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=1
# pad=1
# filters=192
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=1
# pad=1
# filters=192
# activation=silu
# 
# # Merge [-1, -(2k+2)]
# 
# [route]
# layers = -1, -8
# 
# # Transition last
# 
# # 147 (previous+6+4+2k)
# [convolutional]
# batch_normalize=1
# filters=192
# size=1
# stride=1
# pad=1
# activation=silu
# 
# 
# # FPN-3
# 
# [convolutional]
# batch_normalize=1
# filters=128
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [upsample]
# stride=2
# 
# [route]
# layers = 43
# 
# [convolutional]
# batch_normalize=1
# filters=128
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [route]
# layers = -1, -3
# 
# [convolutional]
# batch_normalize=1
# filters=128
# size=1
# stride=1
# pad=1
# activation=silu
# 
# # Split
# 
# [convolutional]
# batch_normalize=1
# filters=128
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [route]
# layers = -2
# 
# # Plain Block
# 
# [convolutional]
# batch_normalize=1
# filters=128
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=1
# pad=1
# filters=128
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=128
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=1
# pad=1
# filters=128
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=128
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=1
# pad=1
# filters=128
# activation=silu
# 
# # Merge [-1, -(2k+2)]
# 
# [route]
# layers = -1, -8
# 
# # Transition last
# 
# # 163 (previous+6+4+2k)
# [convolutional]
# batch_normalize=1
# filters=128
# size=1
# stride=1
# pad=1
# activation=silu
# 
# 
# # PAN-4
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=2
# pad=1
# filters=192
# activation=silu
# 
# [route]
# layers = -1, 147
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=1
# stride=1
# pad=1
# activation=silu
# 
# # Split
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [route]
# layers = -2
# 
# # Plain Block
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=1
# pad=1
# filters=192
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=1
# pad=1
# filters=192
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=192
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=1
# pad=1
# filters=192
# activation=silu
# 
# [route]
# layers = -1,-8
# 
# # Transition last
# 
# # 176 (previous+3+4+2k)
# [convolutional]
# batch_normalize=1
# filters=192
# size=1
# stride=1
# pad=1
# activation=silu
# 
# 
# # PAN-5
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=2
# pad=1
# filters=256
# activation=silu
# 
# [route]
# layers = -1, 131
# 
# [convolutional]
# batch_normalize=1
# filters=256
# size=1
# stride=1
# pad=1
# activation=silu
# 
# # Split
# 
# [convolutional]
# batch_normalize=1
# filters=256
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [route]
# layers = -2
# 
# # Plain Block
# 
# [convolutional]
# batch_normalize=1
# filters=256
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=1
# pad=1
# filters=256
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=256
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=1
# pad=1
# filters=256
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=256
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=1
# pad=1
# filters=256
# activation=silu
# 
# [route]
# layers = -1,-8
# 
# # Transition last
# 
# # 189 (previous+3+4+2k)
# [convolutional]
# batch_normalize=1
# filters=256
# size=1
# stride=1
# pad=1
# activation=silu
# 
# 
# # PAN-6
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=2
# pad=1
# filters=320
# activation=silu
# 
# [route]
# layers = -1, 115
# 
# [convolutional]
# batch_normalize=1
# filters=320
# size=1
# stride=1
# pad=1
# activation=silu
# 
# # Split
# 
# [convolutional]
# batch_normalize=1
# filters=320
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [route]
# layers = -2
# 
# # Plain Block
# 
# [convolutional]
# batch_normalize=1
# filters=320
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=1
# pad=1
# filters=320
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=320
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=1
# pad=1
# filters=320
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# filters=320
# size=1
# stride=1
# pad=1
# activation=silu
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=1
# pad=1
# filters=320
# activation=silu
# 
# [route]
# layers = -1,-8
# 
# # Transition last
# 
# # 202 (previous+3+4+2k)
# [convolutional]
# batch_normalize=1
# filters=320
# size=1
# stride=1
# pad=1
# activation=silu
# 
# # ============ End of Neck ============ #
# 
# # 203
# [implicit_add]
# filters=256
# 
# # 204
# [implicit_add]
# filters=384
# 
# # 205
# [implicit_add]
# filters=512
# 
# # 206
# [implicit_add]
# filters=640
# 
# # 207
# [implicit_mul]
# filters={num_filters}
# 
# # 208
# [implicit_mul]
# filters={num_filters}
# 
# # 209
# [implicit_mul]
# filters={num_filters}
# 
# # 210
# [implicit_mul]
# filters={num_filters}
# 
# # ============ Head ============ #
# 
# # YOLO-3
# 
# [route]
# layers = 163
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=1
# pad=1
# filters=256
# activation=silu
# 
# [shift_channels]
# from=203
# 
# [convolutional]
# size=1
# stride=1
# pad=1
# filters={num_filters}
# activation=linear
# 
# [control_channels]
# from=207
# 
# [yolo]
# mask = 0,1,2
# anchors = 19,27,  44,40,  38,94,  96,68,  86,152,  180,137,  140,301,  303,264,  238,542,  436,615,  739,380,  925,792
# classes={num_classes}
# num=12
# jitter=.3
# ignore_thresh = .7
# truth_thresh = 1
# random=1
# scale_x_y = 1.05
# iou_thresh=0.213
# cls_normalizer=1.0
# iou_normalizer=0.07
# iou_loss=ciou
# nms_kind=greedynms
# beta_nms=0.6
# 
# 
# # YOLO-4
# 
# [route]
# layers = 176
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=1
# pad=1
# filters=384
# activation=silu
# 
# [shift_channels]
# from=204
# 
# [convolutional]
# size=1
# stride=1
# pad=1
# filters={num_filters}
# activation=linear
# 
# [control_channels]
# from=208
# 
# [yolo]
# mask = 3,4,5
# anchors = 19,27,  44,40,  38,94,  96,68,  86,152,  180,137,  140,301,  303,264,  238,542,  436,615,  739,380,  925,792
# classes={num_classes}
# num=12
# jitter=.3
# ignore_thresh = .7
# truth_thresh = 1
# random=1
# scale_x_y = 1.05
# iou_thresh=0.213
# cls_normalizer=1.0
# iou_normalizer=0.07
# iou_loss=ciou
# nms_kind=greedynms
# beta_nms=0.6
# 
# 
# # YOLO-5
# 
# [route]
# layers = 189
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=1
# pad=1
# filters=512
# activation=silu
# 
# [shift_channels]
# from=205
# 
# [convolutional]
# size=1
# stride=1
# pad=1
# filters={num_filters}
# activation=linear
# 
# [control_channels]
# from=209
# 
# [yolo]
# mask = 6,7,8
# anchors = 19,27,  44,40,  38,94,  96,68,  86,152,  180,137,  140,301,  303,264,  238,542,  436,615,  739,380,  925,792
# classes={num_classes}
# num=12
# jitter=.3
# ignore_thresh = .7
# truth_thresh = 1
# random=1
# scale_x_y = 1.05
# iou_thresh=0.213
# cls_normalizer=1.0
# iou_normalizer=0.07
# iou_loss=ciou
# nms_kind=greedynms
# beta_nms=0.6
# 
# 
# # YOLO-6
# 
# [route]
# layers = 202
# 
# [convolutional]
# batch_normalize=1
# size=3
# stride=1
# pad=1
# filters=640
# activation=silu
# 
# [shift_channels]
# from=206
# 
# [convolutional]
# size=1
# stride=1
# pad=1
# filters={num_filters}
# activation=linear
# 
# [control_channels]
# from=210
# 
# [yolo]
# mask = 9,10,11
# anchors = 19,27,  44,40,  38,94,  96,68,  86,152,  180,137,  140,301,  303,264,  238,542,  436,615,  739,380,  925,792
# classes={num_classes}
# num=12
# jitter=.3
# ignore_thresh = .7
# truth_thresh = 1
# random=1
# scale_x_y = 1.05
# iou_thresh=0.213
# cls_normalizer=1.0
# iou_normalizer=0.07
# iou_loss=ciou
# nms_kind=greedynms
# beta_nms=0.6
# 
# # ============ End of Head ============ #

# Commented out IPython magic to ensure Python compatibility.
# %cat /content/yolor/cfg/yolor_p6.cfg

"""# Train Custom YOLOR Detector

### Next, we'll fire off training!


Here, we are able to pass a number of arguments:
- **img:** define input image size
- **batch:** determine batch size
- **epochs:** define the number of training epochs. (Note: often, 3000+ are common here!)
- **data:** set the path to our yaml file
- **cfg:** specify our model configuration
- **weights:** specify a custom path to weights. (Note: We can specify the pretrained weights we downloaded up above with the shell script)
- **name:** result names
-**hyp:** Define the hyperparamters for training
"""

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/yolor
!python train.py --batch-size 8 --img 416 416 --data {dataset.location}/data.yaml --cfg cfg/yolor_p6.cfg --weights '/content/yolor/yolor_p6.pt' --device 0 --name yolor_p6 --hyp '/content/yolor/data/hyp.scratch.1280.yaml' --epochs 50

"""# Evaluate Custom YOLOR Detector Performance

Training losses and performance metrics are saved to Tensorboard and also to a logfile defined above with the **--name** flag when we train. In our case, we named this `yolor_p6`. (If given no name, it defaults to `results.txt`.) The results file is plotted as a png after training completes.
"""

# Commented out IPython magic to ensure Python compatibility.
# Start tensorboard
# Launch after you have started training
# logs save in the folder "runs"
# %load_ext tensorboard
# %tensorboard --logdir runs

from IPython.display import Image
# we can also output some older school graphs if the tensor board isn't working for whatever reason... 
from utils.plots import plot_results  # plot results.txt as results.png
Image(filename='/content/yolor/runs/train/yolor_p6/results.png', width=1000)  # view results.png

# first, display our ground truth data
print("GROUND TRUTH TRAINING DATA:")
Image(filename='/content/yolor/runs/train/yolor_p6/train_batch0.jpg', width=900)

print("AUGMENTED DATA:")
Image(filename='/content/yolor/runs/train/yolor_p6/train_batch0.jpg', width=900)

"""#Run Inference  With Trained Weights
Run inference with a pretrained checkpoint on contents of `test/images` folder downloaded from Roboflow.
"""

# Commented out IPython magic to ensure Python compatibility.
# trained weights are saved by default in our weights folder
# %ls runs/

# Commented out IPython magic to ensure Python compatibility.
# %ls runs/train/yolor_p6/weights

# Create names file for model
import yaml
import ast
with open("../data.yaml", 'r') as stream:
    names = str(yaml.safe_load(stream)['names'])

namesFile = open("../data.names", "w+")
names = ast.literal_eval(names)
for name in names:
  namesFile.write(name +'\n')
namesFile.close()

!python detect.py --weights "runs/train/yolor_p6/weights/best_overall.pt" --conf 0.5 --source ../test/images --names ../data.names --cfg cfg/yolor_p6.cfg

#display inference on ALL test images
#this looks much better with longer training above

import glob
from IPython.display import Image, display

for imageName in glob.glob('/content/yolor/inference/output/*.jpg'): #assuming JPG
    display(Image(filename=imageName))
    print("\n")

"""# Export Trained Weights for Future Inference

Now that you have trained your custom detector, you can export the trained weights you have made here for inference on your device elsewhere
"""

from google.colab import drive
drive.mount('/content/gdrive')

# Commented out IPython magic to ensure Python compatibility.
# %cp /content/yolor/runs/train/yolor_p6/weights/best.pt /content/gdrive/My\ Drive

"""## Congrats!

Hope you enjoyed this!

--Team [Roboflow](https://roboflow.ai)
"""