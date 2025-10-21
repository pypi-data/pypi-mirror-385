"""
Hepatitis C Prediction Package

This package provides machine learning tools for Hepatitis C classification
using PyTorch neural networks with an interactive Streamlit interface.

Modules
--------
data
    Data loading, preprocessing, and dataset creation utilities.
    Contains HepatitisDataset class for PyTorch data loading.
    
models
    Neural network model definitions (HepatitisNet with residual connections).
    Includes model saving/loading and evaluation utilities.
    
train
    Training utilities and ModelTrainer class for model training workflows.
    
visualization
    Plotting and visualization functions for data exploration and results.

Quick Start
-----------
>>> from src.data import load_raw_data, clean_data, prepare_features, HepatitisDataset
>>> from src.models import HepatitisNet, evaluate_model, save_model, load_model
>>> from src.train import ModelTrainer
>>> from torch.utils.data import DataLoader
>>> 
>>> # Load and prepare data
>>> data = load_raw_data()
>>> cleaned_data, encoder = clean_data(data)
>>> X, y, imputer = prepare_features(cleaned_data)
>>> 
>>> # Create dataset
>>> dataset = HepatitisDataset(X_train, y_train)
>>> train_loader = DataLoader(dataset, batch_size=32, shuffle=True)
>>> 
>>> # Create and train model
>>> model = HepatitisNet(input_size=12, hidden_sizes=[128, 64, 32])
>>> trainer = ModelTrainer(model, device='cuda')
>>> history = trainer.train(train_loader, val_loader, epochs=50)

Authors
-------
- Ninjalice (https://github.com/Ninjalice)

License
-------
MIT License - See LICENSE file for details.

Repository
----------
https://github.com/Ninjalice/HEPATITIS_C_MODEL

Documentation
-------------
https://ninjalice.github.io/HEPATITIS_C_MODEL/src.html
"""

__version__ = "0.1.0"
__author__ = "Ninjalice"
__license__ = "MIT"

# Import key classes and functions for easier access
from src.data import (
    load_raw_data,
    download_dataset,
    clean_data,
    prepare_features,
    split_and_scale_data,
    HepatitisDataset,
    get_data_info
)

from src.models import (
    HepatitisNet,
    ResidualBlock,
    evaluate_model,
    save_model,
    load_model,
    TorchWrapper
)

from src.train import ModelTrainer

# Define what's available when using "from src import *"
__all__ = [
    # Data
    'load_raw_data',
    'download_dataset',
    'clean_data',
    'prepare_features',
    'split_and_scale_data',
    'HepatitisDataset',
    'get_data_info',
    # Models
    'HepatitisNet',
    'ResidualBlock',
    'evaluate_model',
    'save_model',
    'load_model',
    'TorchWrapper',
    # Training
    'ModelTrainer',
]
