# -*- coding: utf-8 -*-
"""yolov4-OD.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1gXukWr8wDYmydxdnkyIMtBhQRB9CSjqk

# How to Train Scaled-YOLOv4 on Custom Objects

Scaled-YOLOv4 uses the same training procedures as YOLOv5.

This tutorial is based on the [YOLOv5 repository](https://github.com/ultralytics/yolov5) by [Ultralytics](https://www.ultralytics.com/). This notebook shows training on **your own custom objects**. Many thanks to Ultralytics for putting this repository together - we hope that in combination with clean data management tools at Roboflow, this technologoy will become easily accessible to any developer wishing to use computer vision in their projects.

### Accompanying Blog Post

A blog on Scaled-YOLOv4 is to come, in the meantime having the blog for [how to train YOLOv5](https://blog.roboflow.ai/how-to-train-yolov5-on-a-custom-dataset/)will be useful.

### Steps Covered in this Tutorial

In this tutorial, we will walk through the steps required to train Scaled-YOLOv4 on your custom objects. We use a [public blood cell detection dataset](https://public.roboflow.ai/object-detection/bccd), which is open source and free to use. You can also use this notebook on your own data.

To train our detector we take the following steps:

* Install Scaled-YOLOv4 dependencies
* Download custom Scaled-YOLOv4 object detection data
* Write our Scaled-YOLOv4 Training configuration
* Run Scaled-YOLOv4 training
* Evaluate Scaled-YOLOv4 performance
* Visualize Scaled-YOLOv4 training data
* Run Scaled-YOLOv4 inference on test images
* Export saved Scaled-YOLOv4 weights for future inference



### **About**

[Roboflow](https://roboflow.com) enables teams to deploy custom computer vision models quickly and accurately. Convert data from to annotation format, assess dataset health, preprocess, augment, and more. It's free for your first 1000 source images.

**Looking for a vision model available via API without hassle? Try Roboflow Train.**

![Roboflow Wordmark](https://i.imgur.com/dcLNMhV.png)

#Install Dependencies

_(Remember to choose GPU in Runtime if not already selected. Runtime --> Change Runtime Type --> Hardware accelerator --> GPU)_
"""

# Commented out IPython magic to ensure Python compatibility.
# clone Scaled_YOLOv4
!git clone https://github.com/roboflow-ai/ScaledYOLOv4.git  # clone repo
# %cd /content/ScaledYOLOv4/
#checkout the yolov4-large branch
!git checkout yolov4-large

import torch
print('Using torch %s %s' % (torch.__version__, torch.cuda.get_device_properties(0) if torch.cuda.is_available() else 'CPU'))

# Commented out IPython magic to ensure Python compatibility.
#install mish activation funciton for cuda
# %cd /content/
!git clone https://github.com/JunnYu/mish-cuda
# %cd mish-cuda
!python setup.py build install

!pip install -U PyYAML

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/ScaledYOLOv4/

"""# Download Correctly Formatted Custom Dataset 

We'll download our dataset from Roboflow. Use the "**YOLOv5 PyTorch**" export format. Note that the Ultralytics implementation calls for a YAML file defining where your training and test data is. The Roboflow export also writes this format for us.

To get your data into Roboflow, follow the [Getting Started Guide](https://blog.roboflow.ai/getting-started-with-roboflow/).

![YOLOv5 PyTorch export](https://i.imgur.com/5vr9G2u.png)
"""

# Commented out IPython magic to ensure Python compatibility.
# %cd /content
!pip install roboflow

from roboflow import Roboflow
rf = Roboflow(api_key="0a4WwzoVWX7OLQHdybod")
project = rf.workspace("roboflow-universe-projects").project("construction-site-safety")
dataset = project.version(30).download("yolov5")

# Commented out IPython magic to ensure Python compatibility.
# this is the YAML file Roboflow wrote for us that we're loading into this notebook with our data
# %cat {dataset.location}/data.yaml

"""#Inspect Model Configuration and Architecture

Let's look at the Scaled-YOLOv4 Configuration architecture
"""

# Commented out IPython magic to ensure Python compatibility.
# %cat /content/ScaledYOLOv4/models/yolov4-csp.yaml

"""# Train Custom Scaled-YOLOv4 Detector

### Next, we'll fire off training!


Here, we are able to pass a number of arguments:
- **img:** define input image size
- **batch:** determine batch size
- **epochs:** define the number of training epochs. (Note: often, 3000+ are common here!)
- **data:** set the path to our yaml file
- **cfg:** specify our model configuration
- **weights:** specify a custom path to weights.
- **name:** result names
- **nosave:** only save the final checkpoint
- **cache:** cache images for faster training
"""

orig_dataset_directory = dataset.location
orig_dataset_directory

# Commented out IPython magic to ensure Python compatibility.
# %cd {orig_dataset_directory}
# %cp -r {orig_dataset_directory} /content/ScaledYOLOv4

# Commented out IPython magic to ensure Python compatibility.
# # train scaled-YOLOv4 on custom data for 100 epochs
# # time its performance
# %%time
# %cd /content/ScaledYOLOv4/
# !python train.py --img 416 --batch 16 --epochs 100 --data {dataset.location}/data.yaml --cfg ./models/yolov4-csp.yaml --weights '' --name yolov4-csp-results  --cache

"""# Evaluate Custom Scaled-YOLOv4 Detector Performance

Training losses and performance metrics are saved to Tensorboard and also to a logfile defined above with the **--name** flag when we train. In our case, we named this `yolov5s_results`. (If given no name, it defaults to `results.txt`.) The results file is plotted as a png after training completes.

Note from Glenn: Partially completed `results.txt` files can be plotted with `from utils.utils import plot_results; plot_results()`.
"""

# Commented out IPython magic to ensure Python compatibility.
# Start tensorboard
# Launch after you have started training
# logs save in the folder "runs"
# %load_ext tensorboard
# %tensorboard --logdir runs

# we can also output some older school graphs if the tensor board isn't working for whatever reason... 
#from utils.general import plot_results  # plot results.txt as results.png
from IPython.display import Image, display
display(Image('/content/ScaledYOLOv4/runs/exp0_yolov4-csp-results/results.png'))  # view results.png

"""### Curious? Visualize Our Training Data with Labels

After training starts, view `train*.jpg` images to see training images, labels and augmentation effects.

Note a mosaic dataloader is used for training (shown below), a new dataloading concept developed by Glenn Jocher and first featured in [YOLOv4](https://arxiv.org/abs/2004.10934).
"""

# first, display our ground truth data
print("GROUND TRUTH TRAINING DATA:")
Image(filename='/content/ScaledYOLOv4/runs/exp0_yolov4-csp-results/test_batch0_gt.jpg', width=900)

# print out an augmented training example
print("GROUND TRUTH AUGMENTED TRAINING DATA:")
Image(filename='/content/ScaledYOLOv4/runs/exp0_yolov4-csp-results/train_batch0.jpg', width=900)

"""#Run Inference  With Trained Weights
Run inference with a pretrained checkpoint on contents of `test/images` folder downloaded from Roboflow.
"""

# Commented out IPython magic to ensure Python compatibility.
# trained weights are saved by default in our weights folder
# %ls runs/

# Commented out IPython magic to ensure Python compatibility.
# %ls ./runs/exp0_yolov4-csp-results/weights

"""Running Inference:"""

# Commented out IPython magic to ensure Python compatibility.
# when we ran this, we saw .007 second inference time. That is 140 FPS on a TESLA P100!
# use the best weights!
# %cd /content/ScaledYOLOv4/
TEST_DIR = f'{dataset.location}/test/images'
!python detect.py --weights ./runs/exp0_yolov4-csp-results/weights/best_yolov4-csp-results.pt --img 416 --conf 0.4 --source {TEST_DIR}

# Commented out IPython magic to ensure Python compatibility.
#display inference on ALL test images
#this looks much better with longer training above
import glob
from IPython.display import Image, display

# %cd /content/ScaledYOLOv4/
for imageName in glob.glob('./inference/output/*.jpg'): #assuming JPG
    display(Image(filename=imageName))
    print("\n")

"""# Export Trained Weights for Future Inference

Now that you have trained your custom detector, you can export the trained weights you have made here for inference on your device elsewhere
"""

from google.colab import files
files.download('./runs/exp0_yolov4-csp-results/weights/best_yolov4-csp-results.pt')

"""## Congrats!

Hope you enjoyed this!

--Team [Roboflow](https://roboflow.ai)
"""