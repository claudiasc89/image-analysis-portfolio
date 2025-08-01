# Cellpose Segmentation

## 📂 Project Overview

The aim of this project was to create a model for segmenting *S. pombe* mutant cells in brightfield imaging. For this, we used [Cellpose](https://cellpose.readthedocs.io/en/latest/index.html) v2.2.3. Cellpose provides several built-in pretrained models that you can use as starting points for your own custom model. In this case, I used the `cyto3` model— a general-purpose model designed for segmenting whole cells. It works well on brightfield, phase contrast, and fluorescence images.  When you train a model in Cellpose, you’re essentially **fine-tuning** an existing pretrained model. This process adjusts the pretrained weights to better segment your specific cell type and imaging conditions.


## 📂 Dataset

Previous experiments have shown that using mean projections of brightfield z-stacks (with a distance of 1 µm between slices) is an effective strategy for segmentation of our cells.  

In this project, we will train **two models** using the same underlying images but with different preprocessing:

- **mean3**: Mean projection of 7 total slices.
- **mean2**: Mean projection of 5 slices.

Each image has a corresponding manually drawn mask, created using a drawing pad. For mask annotation, I recommend using [Napari](https://napari.org/) for its ease of use and precise labeling tools.  

![Example segmentation mask](./figures/segmentation_masks_ex.png)  
**Figure 1. Close-up area of a brightfield mean3 projection with its manually annotated segmentation mask for an S. pombe brightfield images. Each color shade in the segmentation masks correspond to a different annotated label.*

The dataset is organized into:

- **Training images**: Used to teach the model what features correspond to cell masks. *(27 images with corresponding masks)*
- **Test images**: Used to evaluate the model by comparing its predicted segmentations against the ground-truth masks. *(5 images with corresponding masks)*

```
project/
 └── data/
      ├── train/
      │    ├── image_01.tif
      │    ├── image_01_masks.tif
      │    ├── image_02.tif
      │    ├── image_02_masks.tif
      │    └── ...
      └── test/
           ├── image_01.tif
           ├── image_01_masks.tif
           ├── image_02.tif
           ├── image_02_masks.tif
           └── ...
```

All images and masks are pre-aligned and share the same dimensions, ensuring compatibility with Cellpose training workflows.

> 💡 **Tip:** Imaging is not always perfect. To create a more robust model, consider adding perturbations to a small fraction (~10%) of your training set. This helps the model generalize to variations it might see in real data.
> Some ways to do this:  
> - Create mean projections from slightly **unfocused** z-stacks.  


## ⚙️ Training Command

To train the Cellpose model on the annotated dataset, use the following command:

```bash
python -m cellpose --train \
  --dir ./project/data/train \
  --test_dir ./project/data/test \
  --pretrained_model cyto3 \
  --chan 0 \
  --learning_rate 0.1 \
  --weight_decay 0.0001 \
  --n_epochs 1000 \
  --verbose
```

### **Explanation of command options**

- **`--train`**  
  Enables training mode in Cellpose.

- **`--dir`**  
  Path to the training images and masks.  
  *Example:* `./project/data/train`

- **`--test_dir`**  
  Path to the test images and masks for validation.  
  *Example:* `./project/data/test`

- **`--pretrained_model cyto3`**  
  Specifies the pretrained model to start from.  
  `cyto3` is used here as the base model for fine-tuning.

- **`--chan 0`**  
  Defines the image channel to use.  
  `0` typically means grayscale / single-channel input.

- **`--learning_rate 0.1`**  
  Sets the learning rate for training.  
  Higher values may train faster but can risk instability.

- **`--weight_decay 0.0001`**  
  Regularization parameter to help prevent overfitting.

- **`--n_epochs 1000`**  
  Number of training epochs (iterations over the entire dataset).

- **`--verbose`**  
  Enables detailed logging output during training.

> 💡 **Tip:** Cellpose expects your input masks files to be named like the images but with `_masks` at the end. If you are using different naming scheme, you can add to the command `--mask_filter your_fav_name_for_masks` and you can do the same for the input images `--img_filter fav_images_name`.

### **What happens during training?**

- Cellpose uses the images and corresponding masks in your training set to fine-tune the selected pretrained model (`cyto3` in this case).  
- During training, Cellpose computes **flows** (vector fields) that describe cell boundaries and shapes. These flows are part of the learned representation and help the model predict accurate masks. Flows files will appear in the test and training folders. 
- The training process runs for the specified number of epochs (here, 1000), validating periodically on your test set.  
- At the end of training, Cellpose saves a **new model directory** (typically in the `models/` folder) containing the learned model.  

You can then use this custom model for segmenting new images!

## Models' evaluation

How do we assess whether our newly trained CellPose model is performing well?

To evaluate it, we'll use the **Adjusted Rand Index (ARI)** from the `sklearn` package. ARI is a metric for comparing the similarity between two clusterings—in this case, the ground truth segmentation and the model's predicted segmentation.

For this evaluation, we'll need a separate test set of images (here, I've used 5), each with its manually curated mask. We'll run these test images through our trained model to generate predicted segmentation masks. Then we'll compute the ARI to measure the agreement between the predicted and manual masks.

In simple terms, ARI tells us how consistently the model assigns pixels to the same segments as the manually curated ground truth. A higher ARI indicates better agreement, meaning our model is segmenting images more accurately. To test your own masks you can use this [Python script](./ARI_evaluation.py).

![Figure showing ARI results](./figures/ARI_figure.png)  
**Figure 2. Box-plot showing the results of Adjusted Rand Index for the generalist model (`regular_mean2`) and the phenotype-specific models (`specific_mean2` and `specific_mean3`), computed on 5 different images*

To conclude, we can see that both `specific_mean2` and `specific_mean3` show significant improvements in segmentation, producing masks that are almost identical to the manually generated ones.

