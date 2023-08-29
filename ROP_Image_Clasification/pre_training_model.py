import matplotlib.pyplot as plt
import numpy as np
import os
import PIL
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.python.keras.layers import Dense, Flatten
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.applications import InceptionV3, ResNet50
from tensorflow.keras.layers import Flatten, Activation, Dropout, Dense, Conv2D, MaxPooling2D
from tensorflow.keras.models import Model

import pandas as pd
from sklearn.model_selection import train_test_split
from shutil import copyfile
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


img_width = 300
img_height = 200
EPOCHS = 20
def load_preprocess_images(path_to_images):
  batch_size=32
  train_ds = tf.keras.preprocessing.image_dataset_from_directory(
    path_to_images,
    validation_split=0.1,
    subset="training",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=batch_size)

    # Separate images and labels from the training dataset
  train_images = []
  train_labels = []

  for images, labels in train_ds:
      train_images.append(images)
      train_labels.append(labels)

  train_images = tf.concat(train_images, axis=0)
  train_labels = tf.concat(train_labels, axis=0)

  # Manually one-hot encode the training labels
  train_labels_one_hot = to_categorical(train_labels.numpy(), num_classes=4)


  val_ds = tf.keras.preprocessing.image_dataset_from_directory(
    path_to_images,
    validation_split=0.1,
    subset="validation",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=batch_size)

  val_images = []
  val_labels = []

  for images, labels in val_ds:
      val_images.append(images)
      val_labels.append(labels)

  val_images = tf.concat(val_images, axis=0)
  val_labels = tf.concat(val_labels, axis=0)

  # Manually one-hot encode the validation labels
  val_labels_one_hot = to_categorical(val_labels.numpy(), num_classes=4)

  class_names = train_ds.class_names
  print("The classes are: ", class_names)

  return (train_images, train_labels_one_hot, val_images, val_labels_one_hot, train_ds, val_ds, class_names)

def build_inceptionV3_model():
  rop_classifier = Sequential()
  pretrained_model = ResNet50( input_shape=(img_height,img_width,3),classes=4,
                    weights='imagenet', include_top = False)
  for layer in pretrained_model.layers:
          layer.trainable=False
  rop_classifier.add(pretrained_model)
  rop_classifier.add(Flatten())
  rop_classifier.add(Activation('relu'))
  rop_classifier.add(Dropout(0.5))
  rop_classifier.add(Dense(1024, activation = 'relu'))
  rop_classifier.add(Dropout(0.5))
  rop_classifier.add(Dense(4, activation = 'softmax'))
  rop_classifier.summary()

  rop_classifier.compile(optimizer=Adam(learning_rate=0.001),loss='categorical_crossentropy',metrics=['accuracy'])
  rop_classifier.summary()
  return rop_classifier

def train_model(rop_classifier, train_images ,train_labels_one_hot, val_images, val_labels_one_hot):
  history = rop_classifier.fit(train_images, train_labels_one_hot,
                              validation_data =(val_images, val_labels_one_hot),
                              epochs = EPOCHS, batch_size = 100)
  return history

if __name__ == "__main__":
    path = "ROP_Image_Clasification/dataset"
    train_images, train_labels_one_hot, val_images, val_labels_one_hot, train_ds, val_ds, class_names = load_preprocess_images(path_to_images=path)
    classifier = build_inceptionV3_model()
    history = train_model(classifier, train_images, train_labels_one_hot, val_images, val_labels_one_hot)
    classifier.save("Retinal_trained_resnet")
