# Cellpose Segmentation

## 📂 Project Overview

The aim of this project was to create a model for segmenting *S. pombe* mutant cells in brightfield imaging. For this, we used [Cellpose](https://cellpose.readthedocs.io/en/latest/index.html) v2.2.3. Cellpose provides several built-in pretrained models that you can use as starting points for your own custom model. In this case, I used the `cyto2` model— a general-purpose model designed for segmenting whole cells. It works well on brightfield, phase contrast, and fluorescence images.  When you train a model in Cellpose, you’re essentially **fine-tuning** an existing pretrained model. This process adjusts the pretrained weights to better segment your specific cell type and imaging conditions.


## 📂 Dataset

Previous experiments have shown that using mean projections of brightfield z-stacks (with a distance of 1 µm between slices) is an effective strategy for segmentation of our cells.  

In this project, we will train **two models** using the same underlying images but with different preprocessing:

- **mean3**: Mean projection of 7 total slices.
- **mean2**: Mean projection of 5 slices.

Each image has a corresponding manually drawn mask, created using a drawing pad. For mask annotation, I recommend using [Napari](https://napari.org/) for its ease of use and precise labeling tools.  

![Example segmentation mask](./figures/segmentation_masks_ex.tif)  
**Figure 1. Close-up area of a brightfield mean3 projection with its manually annotated segmentation mask for an S. pombe brightfield images. Each color shade in the segmentation masks correspond to a different annotated label.*

The dataset is organized into:

- **Training images**: Used to teach the model what features correspond to cell masks. *(27 images with corresponding masks)*
- **Test images**: Used to evaluate the model by comparing its predicted segmentations against the ground-truth masks. *(5 images with corresponding masks)*

```
project/
 └── data/
      ├── train/
      │    ├── image_01.tiff
      │    ├── image_01_masks.tiff
      │    ├── image_02.tiff
      │    ├── image_02_masks.tiff
      │    └── ...
      └── test/
           ├── image_01.tiff
           ├── image_01_masks.tiff
           ├── image_02.tiff
           ├── image_02_masks.tiff
           └── ...
```

All images and masks are pre-aligned and share the same dimensions, ensuring compatibility with Cellpose training workflows.

> 💡 **Tip:** Imaging is not always perfect. To create a more robust model, consider adding perturbations to a small fraction (~10%) of your training set. This helps the model generalize to variations it might see in real data.
> Some ways to do this:  
> - Create mean projections from slightly **unfocused** z-stacks.  
> - Adjust **brightness or contrast** to simulate uneven illumination.  


## Training commands 

## Models evaluation
