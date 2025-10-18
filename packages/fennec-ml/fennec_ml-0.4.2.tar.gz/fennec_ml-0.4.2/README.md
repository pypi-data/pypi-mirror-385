# fennec-ml

A suite of data science and machine learning tools for use by the LeTourneau University FENNEC senior design team.

![Fennec Logo](https://raw.githubusercontent.com/afdavisLETU/fennec-ml/main/assets/Fennec%2025-26.png)
[![PyPI version](https://img.shields.io/pypi/v/fennec-ml.svg)](https://pypi.org/project/fennec-ml/)

## Instalation

```bash
pip install fennec-ml
```

## Quick Start

### Data Utils

```python
import os
import fennec_ml as fn

# setup
root_dir = os.getcwd()
excel_dir = os.path.join(root_dir, "Raw_Data")
csv_dir = os.path.join(root_dir, "Proccessed_Data")
timesteps = 60

# excel to csv
fn.folder_cleaner(excel_dir)

# normalize and get labels
norm_data = fn.normalize(csv_dir)
labels = fn.get_CG_labels(csv_dir)

# segment and sort into train, validate, and test datasets
dataset_dict = fn.segment_and_split(norm_data, labels, timesteps)

# use dataset_dict
training_sets = dataset_dict['Training_Set']['sets']
training_labels = dataset_dict['Training_Set']['labels']
```

## Project Structure

```txt
myproject/
├── data/
│   ├── raw_data/
│   │   ├── flight123_AA_L.xlxs
│   │   └── ...
│   └── proccessed_data/
│       ├── flight123_AA_L.csv
│       └── ...
├── saved_models/
│   └── ...
├── vars_of_interest.json
├── project_dev.ipynb
└── project_training.py
```

## Features

### data_cleaner()

Preprocesses .xlsx files into fennec question-usefull .csv files.

**Args:**

- filepath (string): The .xlsx file to process.
- savepath (string): The folder to save the .csv file.
- overwrite (bool): Skips the overwrite checker if true.
- skip (bool): Skips duplicate files instead of checking or overwriting if true.
- varspath (string): The vars-of-interest.json path. Defaults to same folder as THIS script.  

Relies on the vars_of_interest.json file to determine what data is wanted

```python
fn.data_cleaner(excel_filename, overwrite= True)
```

---

### folder_cleaner()

Preprocesses a *folder* of .xlsx files into fennec question-usefull .csv files.

**Args:**

- excel_dir (string): The folder of .xlsx files to process.
- savepath (string): The folder to save the .csv file.
- overwrite (bool): Skips the overwrite checker if true.
- skip (bool): Skips duplicate files instead of checking or overwriting if true.
- varspath (string): The vars-of-interest.json path. Defaults to same folder as *this* script.

Relies on the vars_of_interest.json file to determine what data is wanted

```python
fn.folder_cleaner(excel_dir, skip= True)
```

---

### normalize()

Return a 3D array of normalized data from cleaned csv's  
**Note:** *Normalizing* means scaling the data between the min and max values

**Args:**

- csv_dir (string): The path (including the folder name) of cleaned data
- weights (list): An optional list of weights corresponding to each column
- offsets (list): An optional list of offsets corresponding to column

**Returns:**

- norm_data (list): A list of numpy arrays holding normalized data

```python
scaled_data = fn.normalize(csv_dir)
```

---

### standardize()

Return a 3D array of standardized data from cleaned csv's  
**Note:** *Standarizing* means scaling the data so the mean = 0 and the std deviation = 1

**Args:**

- csv_dir (string): The path (including the folder name) of cleaned data
- weights (list): An optional list of weights corresponding to each column
- offsets (list): An optional list of offsets corresponding to column

**Returns:**

- stand_data (list): A list of numpy arrays holding STANDARDIZED data

```python
scaled_data = fn.standardize(csv_dir)
```

---

### get_2D_CG_labels()

Reads all filenames in a folder and returns 2d CG characterization labels

**Args:**

- csv_dir (string): Directory of .csv files from which to get labels

**Returns:**

- labels (list): A list of all the characterization labels

```python
cg_labels = fn.get_CG_labels(csv_dir)
```

---

### get_1D_CG_labels()

Reads all filenames in a folder and returns 1d CG characterization labels

**Args:**

- csv_dir (string): Directory of .csv files from which to get labels

**Returns:**

- labels (list): A list of all the characterization labels

```python
cg_labels = fn.get_CG_labels(csv_dir)
```

---

### segment_and_split()

Segments, labels, and sorts data into dataset dictionary

**Args:**

- input_data (list): List of numpy arrays, 1 per proccessed and scaled files
- input_labels (list): List of characterization lables, 1 per file (should correspond to input_data)
- timesteps (int): length of desired segments
- train_split (float): Percentage of segments to save as training segments
- validate_split (float): Percentage of segments to save as validation segments

**Returns:**

- output (dict): 3 labels: "Training_Set", "Validation_Set", and "Testing_Set"  
Each set has the follwing labels: "sets" and "labels"
  - "sets" : list of sets, corresponds to "labels"
  - "labels" : list of labels, corresponds to "sets"  

```python
data_dict = fn.segment_and_split(all_data, all_labels, 60)

train_set = data_dict['Training_Set']['sets']
train_labels = data_dict['Training_Set']['labels']
```

## Contributers

- Luke Fagg  (Team Lead)
- Micah Yarbrough (Pilot ID)
- Wills Kookogey (Fault ID)
- Justin Hawk (3D CG)
