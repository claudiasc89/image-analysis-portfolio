# Creation of a classifier

This module generates a classifier to distinguish between different types of blood cells.
Data was obtained from this [publication](https://www.nature.com/articles/s41597-025-06223-x).

## 🔎 Step-by-Step Breakdown

1. **Imports and Setup**
	- Loads essential libraries for image processing (OpenCV, PIL), data handling (NumPy, os), plotting (matplotlib), and machine learning (scikit-learn, Keras).
	- Sets a random seed for reproducibility.

2. **Data Loading**
	- Specifies the directory containing the blood cell images.
	- Lists the available images for each cell type (hairy cell and monocyte).

3. **Dataset Creation**
	- Defines `create_dataset()` to:
	  - Load images from two classes.
	  - Convert images to arrays and assign labels (0 for hairy cell, 1 for monocyte).
	  - Limit the number of images per class for balanced training.

4. **Model Architecture**
	- Defines `model_architecture()` to:
	  - Build a Convolutional Neural Network (CNN) using Keras.
	  - Includes convolutional, pooling, batch normalization, dropout, and dense layers.
	  - Uses softmax activation for binary classification.

5. **Training History Plotting**
	- Defines `plot_training_history()` to visualize training/validation loss and accuracy over epochs.

6. **Main Execution**
	- Loads and labels the dataset.
	- Splits data into training and testing sets.
	- Builds the CNN model.
	- Trains the model (unless a saved model already exists).
	- Saves the trained model.
	- Plots training history.
	- Evaluates the model on the test set and prints the results.

## 🔎 Graphical explanation 

![Graphical explanation of the classifier workflow] (./figures/classifier_workflow.png)