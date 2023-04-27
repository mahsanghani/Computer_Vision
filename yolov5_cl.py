# -*- coding: utf-8 -*-
"""yolov5-CL.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-U_J62A8vKnxsUT7n3WEKZ_-f7t3sJqO

# YOLOv5 Classification Tutorial

YOLOv5 supports classification tasks too. This is the official YOLOv5 classification notebook tutorial. YOLOv5 is maintained by [Ultralytics](https://github.com/ultralytics/yolov5).

This notebook covers:

*   Inference with out-of-the-box YOLOv5 classification on ImageNet
*  [Training YOLOv5 classification](https://blog.roboflow.com//train-YOLOv5-classification-custom-data) on custom data

*Looking for custom data? Explore over 66M community datasets on [Roboflow Universe](https://universe.roboflow.com).*

This notebook was created with Google Colab. [Click here](https://colab.research.google.com/drive/1FiSNz9f_nT8aFtDEU3iDAQKlPT8SCVni?usp=sharing) to run it.

# Setup

Pull in respective libraries to prepare the notebook environment.
"""

# Commented out IPython magic to ensure Python compatibility.
!git clone https://github.com/ultralytics/yolov5  # clone
# %cd yolov5
# %pip install -qr requirements.txt  # install

import torch
import utils
display = utils.notebook_init()  # checks

"""# 1. Infer on ImageNet

To demonstrate YOLOv5 classification, we'll leverage an already trained model. In this case, we'll download the ImageNet trained models pretrained on ImageNet using YOLOv5 Utils.
"""

from utils.downloads import attempt_download

p5 = ['n', 's', 'm', 'l', 'x']  # P5 models
cls = [f'{x}-cls' for x in p5]  # classification models

for x in cls:
    attempt_download(f'weights/yolov5{x}.pt')

"""Now, we can infer on an example image from the ImageNet dataset."""

#Download example image
import requests
image_url = "https://i.imgur.com/OczPfaz.jpg"
img_data = requests.get(image_url).content
with open('bananas.jpg', 'wb') as handler:
    handler.write(img_data)

#Infer using classify/predict.py
!python classify/predict.py --weights ./weigths/yolov5s-cls.pt --source bananas.jpg

"""From the output, we can see the ImageNet trained model correctly predicts the class `banana` with `0.95` confidence.

## 2. (Optional) Validate

Use the `classify/val.py` script to run validation for the model. This will show us the model's performance on each class.

First, we need to download ImageNet.
"""

# # WARNING: takes ~20 minutes
# !bash data/scripts/get_imagenet.sh --val

# # run the validation script
# !python classify/val.py --weights ./weigths/yolov5s-cls.pt --data ../datasets/imagenet

"""The output shows accuracy metrics for the ImageNet validation dataset including per class accuracy.

# 3. Train On Custom Data

To train on custom data, we need to prepare a dataset with custom labels.

To prepare custom data, we'll use [Roboflow](https://roboflow.com). Roboflow enables easy dataset prep with your team, including labeling, formatting into the right export format, deploying, and active learning with a `pip` package. 

If you need custom data, there are over 66M open source images from the community on [Roboflow Universe](https://universe.roboflow.com).

(For more guidance, here's a detailed blog on [training YOLOv5 classification on custom data](https://blog.roboflow.com/train-YOLOv5-classification-custom-data).)


Create a free Roboflow account, upload your data, and label. 

![](https://s4.gifyu.com/images/fruit-labeling.gif)

### Load Custom Dataset

Next, we'll export our dataset into the right directory structure for training YOLOv5 classification to load into this notebook. Select the `Export` button at the top of the version page, `Folder Structure` type, and `show download code`.

The ensures all our directories are in the right format:

```
dataset
├── train
│   ├── class-one
│   │   ├── IMG_123.jpg
│   └── class-two
│       ├── IMG_456.jpg
├── valid
│   ├── class-one
│   │   ├── IMG_789.jpg
│   └── class-two
│       ├── IMG_101.jpg
├── test
│   ├── class-one
│   │   ├── IMG_121.jpg
│   └── class-two
│       ├── IMG_341.jpg
```

![](https://i.imgur.com/BF9BNR8.gif)


Copy and paste that snippet into the cell below.
"""

# Commented out IPython magic to ensure Python compatibility.
# Ensure we're in the right directory to download our custom dataset
import os
os.makedirs("../datasets/", exist_ok=True)
# %cd ../datasets/

# REPLACE the below with your exported code snippet from above
!pip install roboflow

from roboflow import Roboflow
rf = Roboflow(api_key="0a4WwzoVWX7OLQHdybod")
project = rf.workspace("roboflow-universe-projects").project("banana-ripeness-classification")
dataset = project.version(4).download("folder")

#Save the dataset name to the environment so we can use it in a system call later
dataset_name = dataset.location.split(os.sep)[-1]
os.environ["DATASET_NAME"] = dataset_name

"""### Train On Custom Data 🎉
Here, we use the DATASET_NAME environment variable to pass our dataset to the `--data` parameter.

Note: we're training for 100 epochs here. We're also starting training from the pretrained weights. Larger datasets will likely benefit from longer training. 
"""

# Commented out IPython magic to ensure Python compatibility.
# %cd ../yolov5
!python classify/train.py --model yolov5s-cls.pt --data $DATASET_NAME --epochs 100 --img 128 --pretrained weights/yolov5s-cls.pt

"""### Validate Your Custom Model

Repeat step 2 from above to test and validate your custom model.
"""

!python classify/val.py --weights runs/train-cls/exp/weights/best.pt --data ../datasets/$DATASET_NAME

"""### Infer With Your Custom Model"""

#Get the path of an image from the test or validation set
if os.path.exists(os.path.join(dataset.location, "test")):
  split_path = os.path.join(dataset.location, "test")
else:
  os.path.join(dataset.location, "valid")
example_class = os.listdir(split_path)[0]
example_image_name = os.listdir(os.path.join(split_path, example_class))[0]
example_image_path = os.path.join(split_path, example_class, example_image_name)
os.environ["TEST_IMAGE_PATH"] = example_image_path

print(f"Inferring on an example of the class '{example_class}'")

#Infer
!python classify/predict.py --weights runs/train-cls/exp/weights/best.pt --source $TEST_IMAGE_PATH

"""We can see the inference results show ~3ms inference and the respective classes predicted probabilities.

## (OPTIONAL) Improve Our Model with Active Learning

Now that we've trained our model once, we will want to continue to improve its performance. Improvement is largely dependent on improving our dataset.

We can programmatically upload example failure images back to our custom dataset based on conditions (like seeing an underrpresented class or a low confidence score) using the same `pip` package.
"""

# # Upload example image
# project.upload(image_path)

# # Example upload code 
# min_conf = float("inf")
# for pred in results:
#     if pred["score"] < min_conf:
#         min_conf = pred["score"]
# if min_conf < 0.4:
#     project.upload(image_path)

"""# (BONUS) YOLOv5 classify/predict.py Accepts Several Input Methods
- Webcam: `python classify/predict.py --weights yolov5s-cls.pt --source 0`
- Image `python classify/predict.py --weights yolov5s-cls.pt --source img.jpg`
- Video: `python classify/predict.py --weights yolov5s-cls.pt --source vid.mp4`
- Directory: `python classify/predict.py --weights yolov5s-cls.pt --source path/`
- Glob: `python classify/predict.py --weights yolov5s-cls.pt --source 'path/*.jpg'`
- YouTube: `python classify/predict.py --weights yolov5s-cls.pt --source 'https://youtu.be/Zgi9g1ksQHc'`
- RTSP, RTMP, HTTP stream: `python classify/predict.py --weights yolov5s-cls.pt --source 'rtsp://example.com/media.mp4'`

###Directory Example
"""

#Directory infer
os.environ["TEST_CLASS_PATH"] = test_class_path = os.path.join(*os.environ["TEST_IMAGE_PATH"].split(os.sep)[:-1])
print(f"Infering on all images from the directory {os.environ['TEST_CLASS_PATH']}")
!python classify/predict.py --weights runs/train-cls/exp/weights/best.pt --source /$TEST_CLASS_PATH/

"""###YouTube Example"""

#YouTube infer
!python classify/predict.py --weights runs/train-cls/exp/weights/best.pt --source 'https://www.youtube.com/watch?v=7AlYA4ItA74'