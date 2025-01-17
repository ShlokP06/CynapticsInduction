# -*- coding: utf-8 -*-
"""Classifier.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1qG5i3mXDDVGRuntLpn56aWbOb62_2VQV
"""

from keras.utils import to_categorical
from keras.preprocessing.image import load_img
from keras.models import Sequential
from keras.applications import MobileNetV2, ResNet152, VGG16, EfficientNetB0, InceptionV3
from keras.layers import Dense, Conv2D, Dropout, Flatten, MaxPooling2D, BatchNormalization, GlobalAveragePooling2D
import os
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np
from tqdm.notebook import tqdm
import PIL
import csv

! unzip Train.zip

def createdataframe(dir):
    image_paths = []
    labels = []
    for label in os.listdir(dir):
        for imagename in os.listdir(os.path.join(dir, label)):
            image_path=os.path.join(dir,label,imagename)
            if os.path.isfile(image_path):
              image_paths.append(image_path)
              labels.append(label)
        print(label, "completed")
    return image_paths, labels

def extract_features(images):
    features = []
    for image in tqdm(images):
        try:
          img = load_img(image, target_size=(320, 320))
        except PIL.UnidentifiedImageError:
          print("Error loading image...Skipped.")
          continue
        img = np.array(img)
        features.append(img)
    if not features:
      return np.zeros((0,320,320,3))
    features = np.array(features)
    features = features.reshape(features.shape[0], 320, 320, 3)  # Reshape all images in one go
    return features

TRAIN_DIR = "/content/Train"

train = pd.DataFrame()
train['image'], train['label'] = createdataframe(TRAIN_DIR)

train_features = extract_features(train['image'])

x_train = train_features / 255.0

le = LabelEncoder()
le.fit(train['label'])
y_train = le.transform(train['label'])
y_train = to_categorical(y_train, num_classes=2)

def create_model():
    model=Sequential()
    model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(320, 320, 3)))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(256, kernel_size=(3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(512, kernel_size=(3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(1024, kernel_size=(3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())
    model.add(Dense(1024, activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(2048, activation='relu'))
    model.add(Dense(2, activation='softmax'))
    model.compile(optimizer="Adam", loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(x=x_train, y=y_train, batch_size=4, epochs=100)
    return model

model=create_model()

! unzip Test.zip

def createframe(dir):
    image_paths = []
    for imagename in os.listdir(dir):
      image_path=os.path.join(dir,imagename)
      if os.path.isfile(image_path):
        image_paths.append(image_path)
        print(imagename, "completed")
    return image_paths

import pandas as pd

# Initialize the result DataFrame
header = ["Id", "Label"]
results_df = pd.DataFrame(columns=header)

TEST_DIR = "/content/Test"
test = createframe(TEST_DIR)

for image_path in test:
    test_features = extract_features([image_path])
    if test_features.shape[0] == 0:
        print(f"Skipping {image_path} due to empty features.")
        temp_df=pd.DataFrame({"Id": [image_path[14:-4]], "Label": "Real"})
        results_df = pd.concat([results_df,temp_df])
        continue
    x_test = test_features / 255.0
    prediction = model.predict(x_test)[0]
    ap, rp = prediction
    label = "Real" if rp > ap else "AI"
    # Append results to DataFrame
    temp_df=pd.DataFrame({"Id": [image_path[14:-4]], "Label": [label]})
    results_df = pd.concat([results_df,temp_df])
# Save the DataFrame to CSV
output_csv_path = "/content/ansfile130.csv"
results_df.to_csv(output_csv_path, index=False)