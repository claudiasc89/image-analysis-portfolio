# classifier for blood cells dataset from Roche publication
# article: https://www.nature.com/articles/s41597-025-06223-x
# dataset: https://zenodo.org/records/14277609
# with the help of tutorial: https://www.youtube.com/watch?v=R9PPxpzj5tI
# more info: https://poloclub.github.io/cnn-explainer/
# CNN networs for image classification
# libraries
import numpy as np
import cv2
import os
import matplotlib.pyplot as plt
from PIL import Image # for image processing
from sklearn.model_selection import train_test_split
from keras.layers import Convolution2D, MaxPooling2D, Flatten, Dense, BatchNormalization, Dropout
from keras.models import Sequential
from keras.utils import to_categorical
# TO DO: import keras and set environment for tensorflow

# set the np.random.seed for reproducibility
np.random.seed(23)

# step1: load the data
img_dir = '/Users/claudiasalatcanela/Documents/Python/data/cnn_blood_cells'
size=288 #pixels

hairy = os.listdir(os.path.join(img_dir, 'hairy_cell'))
monocyte = os.listdir(os.path.join(img_dir, 'monocyte'))

#### FUNCTIONS ####

def create_dataset(img_dir, cell_type1_name, cell_type2_name, num_images=500):
    # load the images from the two classes and append them to the dataset list
    # create dataset list to store the images and labels
    dataset = []
    labels = []
    # reconstitute whole paths
    cell_type1 = os.listdir(os.path.join(img_dir, cell_type1_name))
    cell_type2 = os.listdir(os.path.join(img_dir, cell_type2_name))
    
    for i, filename in enumerate(cell_type1):
        # check if the file is an image                   
        if filename.endswith('.TIF'):
            filepath = os.path.join(img_dir, cell_type1_name, filename)
            #open the image using cv2
            img = cv2.imread(filepath)
            # append the image to the dataset list
            dataset.append(np.array(img))
            # append the label to the labels list
            labels.append(0) # label 0 for hairy cell
            if i == num_images - 1: # limit to num_images for each class
                break
    for i, filename in enumerate(cell_type2):
        # check if the file is an image                   
        if filename.endswith('.TIF'):
            filepath = os.path.join(img_dir, cell_type2_name, filename)
            #open the image using cv2
            img = cv2.imread(filepath)
            # append the image to the dataset list
            dataset.append(np.array(img))
            # append the label to the labels list
            labels.append(1) # label 1 for monocyte
            if i == num_images - 1: # limit to num_images for each class
                break
    return dataset, labels

def model_architecture(size):
    # define the CNN model architecture
    input_shape = (size, size, 3) # 3 channels for RGB images
    model = Sequential()
    # Convolutional block 1
    model.add(Convolution2D(32, (3, 3), activation='relu', input_shape=input_shape, data_format='channels_last',padding='same'))
    model.add(MaxPooling2D(pool_size=(2, 2), data_format='channels_last'))
    model.add(BatchNormalization(axis=-1)) # to stabilize activations
    # Convolutional block 2
    model.add(Convolution2D(32, (3, 3), activation = 'relu', padding='same'))
    model.add(MaxPooling2D(pool_size = (2, 2), data_format="channels_last"))
    model.add(BatchNormalization(axis = -1))
    model.add(Dropout(0.2))

    model.add(Flatten()) # to convert 2D feature maps to 1D feature vectors for the dense layers
    # Dense layers for classification
    model.add(Dense(activation = 'relu', units=512))
    model.add(BatchNormalization(axis = -1))
    model.add(Dropout(0.2))
    # further compression of the feature space to 256 units to reduce overfitting and improve generalization
    model.add(Dense(activation = 'relu', units=256))
    model.add(BatchNormalization(axis = -1))
    model.add(Dropout(0.2))
    model.add(Dense(activation = 'softmax', units=2))
    model.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])
    return model

def plot_training_history(history):
    # plot the training history
    plt.figure(figsize=(12, 4))
    # plot loss
    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'], label='train_loss')
    plt.plot(history.history['val_loss'], label='val_loss')
    plt.title('Model Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    # plot accuracy
    plt.subplot(1, 2, 2)
    plt.plot(history.history['accuracy'], label='train_accuracy')
    plt.plot(history.history['val_accuracy'], label='val_accuracy')
    plt.title('Model Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.show()

####### MAIN CODE #######
if __name__ == "__main__":
    # generate dataset and labels (default with 500 images per class)
    dataset, labels = create_dataset(img_dir, 'hairy_cell', 'monocyte')
    print(f"Dataset size: {len(dataset)}, type(dataset[0]): {type(dataset[0])}, image shape: {dataset[0].shape}")
    # split the dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(dataset, to_categorical(labels), test_size=0.2, random_state=23)
    # define the CNN model architecture
    model = model_architecture(size)
    print(model.summary())
    # train the model
    saving_path = os.path.join (img_dir, 'model')
    if not os.path.exists(saving_path):
        os.makedirs(saving_path)
    model_name= 'blodcells_cnn_20260211.h5'
    model_path = os.path.join(saving_path, model_name)
    
    if not os.path.isfile(model_path): # to avoid retraining if the code is run multiple times
        history = model.fit(np.array(X_train),
                        y_train,
                        batch_size=64,# number of samples per gradient update
                        epochs=50, # number of iterations to train the model
                        validation_split=0.1, # fraction of the training data to be used as validation data
                        shuffle=False, # to keep the order of the data (not to shuffle) since the data is already shuffled in the train_test_split
                        verbose=1) # to print the training progress
    
    #Save the model
    model.save(os.path.join(model_path, model_name))
    # plot the training history
    plot_training_history(history)
    
    # test the model on the test set
    test_loss, test_accuracy = model.evaluate(np.array(X_test), y_test, verbose=0)
    print(f"Test Loss: {test_loss:.4f}, Test Accuracy: {test_accuracy:.4f}")