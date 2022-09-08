# -*- coding: utf-8 -*-
"""solution.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1sr9sso21LzWZ6jgRSQdscXrebzcUYCa3

# Importing Librairies
"""

import os
from os import walk

import cv2
import time

import shutil
import numpy as np
import PIL
from PIL import Image
import os, sys
from scipy.io import loadmat

import tensorflow
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.models import Sequential
from tensorflow.keras.activations import softmax
from tensorflow.keras import optimizers
from tensorflow.keras.metrics import Accuracy

from tensorflow.keras.preprocessing.image import ImageDataGenerator

"""# Loading and Processing the dataset"""

path = "" # Please indacte the path to dataset/

def load_data(data_path, classes, dataset='train', image_size=128):

    num_images = 0

    for i in range(len(classes)):
        dirs = sorted(os.listdir(data_path + dataset + '/' + classes[i]))
        num_images += len(dirs)
                                
    x = np.zeros((num_images, image_size, image_size, 3))
    y = np.zeros((num_images, 1))
    
    current_index = 0
    
    for idx_class in range(len(classes)):
        dirs = sorted(os.listdir(data_path + dataset + '/' + classes[idx_class]))
        num_images += len(dirs)
    
        # Loading images
        for idx_img in range(len(dirs)):
            item = dirs[idx_img]
            if os.path.isfile(data_path + dataset + '/' + classes[idx_class] + '/' + item):
                # Opening the image
                img = Image.open(data_path + dataset + '/' + classes[idx_class] + '/' + item)
                # RGB conversion
                img = img.convert('RGB')
                # Resizing
                img = img.resize((image_size,image_size))
                x[current_index] = np.asarray(img)
                # Writing the label
                y[current_index] = idx_class
                current_index += 1
                
    return x, y

"""## Training set; Validation set; Test set"""

labels = ['shikamaru', 'naruto', 'obito', 'sakura', 'sasuke']
size = 128

x_train, y_train = load_data(path, labels, dataset='train', image_size=size)
print(x_train.shape, y_train.shape)

x_val, y_val = load_data(path, labels, dataset='validation', image_size=size)
print(x_val.shape, y_val.shape)

x_test, y_test = load_data(path, labels, dataset='test', image_size=size)
print(x_test.shape, y_test.shape)

"""### Displaying examles from the training set"""

import matplotlib.pyplot as plt

plt.figure(figsize=(12, 12))
shuffle_indices = np.random.permutation(x_train.shape[0])
for i in range(0, 9):
    plt.subplot(3, 3, i+1)
    image = x_train[shuffle_indices[i]]
    plt.title(labels[int(y_train[shuffle_indices[i]])])
    plt.imshow(image/255)

plt.tight_layout()
plt.show()

"""### [0,1] Normalization"""

x_train = x_train/255
x_val = x_val/255
x_test = x_test/255

"""# Model

## Architecture
"""

model = Sequential()

model.add(Conv2D(32, (3,3), activation="relu", input_shape=(size,size,3), padding ="valid"))
model.add(MaxPooling2D(pool_size = (2,2), padding="valid"))

model.add(Conv2D(64, (3,3), activation="relu",  padding ="valid"))
model.add(MaxPooling2D(pool_size = (2,2), padding="valid"))

model.add(Conv2D(96, (3,3), activation="relu",padding ="valid"))
model.add(MaxPooling2D(pool_size = (2,2), padding="valid"))

model.add(Conv2D(128, (3,3), activation="relu",  padding ="valid"))
model.add(MaxPooling2D(pool_size = (2,2), padding="valid"))

model.add(Flatten()) 
model.add(Dense(512, activation="relu"))
model.add(Dense(5, activation="softmax") )

"""## Model summary"""

model.summary()

"""# Training"""

lr = 3e-4
model.compile(loss='sparse_categorical_crossentropy',
              optimizer=optimizers.Adam(learning_rate=lr),
              metrics=['sparse_categorical_accuracy'])

# Callbacks

# Best weights (validation set)
checkpoint_filepath = 'best_weights'
mc_cb = tensorflow.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_filepath,
    save_weights_only=True,
    monitor='val_sparse_categorical_accuracy',
    mode='max',
    verbose=1,
    save_best_only=True)

# Early Stopping
es_cb = tensorflow.keras.callbacks.EarlyStopping(
    monitor="val_loss",
    min_delta=0.01,
    patience=7,
    mode="auto")

history = model.fit(x_train,y_train, 
                    validation_data=(x_val, y_val),
                    epochs=100,
                    callbacks = [mc_cb, es_cb]
                    )

model.load_weights('best_weights')

def plot_training_analysis():
  acc = history.history['sparse_categorical_accuracy']
  val_acc = history.history['val_sparse_categorical_accuracy']
  loss = history.history['loss']
  val_loss = history.history['val_loss']

  epochs = range(len(acc))

  plt.plot(epochs, acc, 'b', linestyle="--",label='Training acc')
  plt.plot(epochs, val_acc, 'g', label='Validation acc')
  plt.title('Training and validation accuracy')
  plt.legend()

  plt.figure()

  plt.plot(epochs, loss, 'b', linestyle="--",label='Training loss')
  plt.plot(epochs, val_loss,'g', label='Validation loss')
  plt.title('Training and validation loss')
  plt.legend()

  plt.show()

plot_training_analysis()

test_accuracy = Accuracy()

# training=False is needed only if there are layers with different
# behavior during training versus inference (e.g. Dropout).
logits = model(x_test, training=False)
prediction = tensorflow.argmax(logits, axis=1, output_type=tensorflow.int32)
test_accuracy(prediction, y_test)

print("Test set accuracy: {:.3%}".format(test_accuracy.result()))