# Automatic z-Projections

This module generates automatic z-projections from microscopy image stacks (e.g. multi-slice TIFF files). It uses common projection methods to create 2D images suitable for analysis or visualization.
The script is designed to be run on your favorite code editor.
---


## 🗂️ Define parameters 

The script requires the following parameters

-**`folder`** *(str)*
Path to the folder containing the `.tif` files to be processed.

- **`channels`** *(list of str)*:  
  Names of the fluorescent channels to process.  
  Filenames in the folder should include the channel names to allow filtering.  

  **Example:**  
  If your folder contains images for *mCherry* and *sfGFP*, the filenames should clearly indicate the channel, such as:  
  - `smp00_sfGFP.tif`  
  - `smp00_mCherry.tif`

- **`projection_type`** *(str)*:
Type of projection to perform. The script is designed to perform either maximum or mean projections,

- **`z_range`** *(int)*:
Number of slices to take below or after the best focused slice. 
For example, if set to 1 it will project 3 slices: (best focused-1, best focused, best focused +1)



## 🔎 Step-by-Step Breakdown

** Load the z-stack image **

- Reads a multi-slice 3D or 4D (containing time-points) TIFF file (.tif)




What it does: Finds which Z-slice is most in focus
How: Calculates standard deviation for each slice (higher = more focused)
Returns: The index of the best-focused slice


What it does: Combines multiple Z-slices into one 2D image
Options: Maximum projection (brightest pixel) or mean projection (average)



-
- Maximum intensity projection
- Mean intensity projection
- Customizable input/output paths
- Easy command-line interface (optional)
