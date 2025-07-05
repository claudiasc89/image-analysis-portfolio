# Automatic z-Projections

This module generates automatic z-projections from microscopy image stacks (e.g. multi-slice TIFF files). It uses common projection methods to create z-projected images suitable for analysis or visualization.
The script is designed to be run on your favorite code editor.
---


## ⚙️ Requirements

- **`file types`**: 
Runs exclusively on .tif files.

- **`file dimensions`**: 
Designed to process time-lapse microscopy data.
It requires 4D files with dimensions organised as **(time, z-stacks, x , y)**.


## 🗂️ Define parameters 

The script requires the following parameters

- **`folder`** *(str)*:
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

**Select and load the z-stack image**
- Iterates over the files on the folder to select the ones with the specified `channel name`. It imports the selected file.

**Loop over time-points**
- Processes 3D image stacks for each time-point for subsequent analysis and processing.

**Automatically determines best focused plane**
- Uses a standard method based on standard deviation to find the best focused slice, to know [more](https://claudiasc89.github.io/imganalysis3/docs/processing/zproj_bestfocus/).
- Calculates the range of slices to include in the projection (slices below and above the central one). It controls that the output of this calculations does not exceed the image dimensions. For instance if the best focused slice is the 4 out of 5 and we have determined a z-range of two, it will short down the range to the edges. 

**Projection**
- Performs the specified projection method (e.g., maximum or mean intensity).

**Save projected image and report**
- Saves the projected image to the output folder, maintaining the original filename with a suffix indicating the projection.  
- Creates an Excel report detailing the range of z-slices used for each timepoint and image.

