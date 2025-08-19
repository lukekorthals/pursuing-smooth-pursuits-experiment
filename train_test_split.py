import numpy as np
import os

np.random.seed(1)
data_dir = ("data")
participant_ids = [folder for folder in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, folder)) if folder != "pilot" and folder != "excluded"]
train_ids = np.random.choice(participant_ids, size=7, replace=False)
test_ids = [id for id in participant_ids if id not in train_ids]

# Create new folder data/train and data/test
if not os.path.exists("data/train"):
    os.makedirs("data/train")
if not os.path.exists("data/test"):
    os.makedirs("data/test")

# Move data into train and test folders
for id in train_ids:
    os.rename(f"data/{id}", f"data/train/{id}")
for id in test_ids:
    os.rename(f"data/{id}", f"data/test/{id}")