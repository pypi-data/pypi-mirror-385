"""
Neural network model definitions for Hepatitis C classification.

This module contains only the model architecture definitions,
following the separation of concerns principle. Training logic is in train.py
and data handling is in data.py.
"""

from __future__ import annotations
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle
from sklearn.base import BaseEstimator, ClassifierMixin
import time

class ResidualBlock(nn.Module):
    """
    Residual block with layer normalization and dropout.
    """
    def __init__(self, size: int, dropout_rate: float = 0.3):
        super(ResidualBlock, self).__init__()
        self.block = nn.Sequential(
            nn.LayerNorm(size),
            nn.Linear(size, size),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.LayerNorm(size),
            nn.Linear(size, size),
            nn.Dropout(dropout_rate)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.block(x)

class HepatitisNet(nn.Module):
    """
    Neural Network for Hepatitis C classification with residual connections.

    Parameters
    -----------
    input_size : int
        Number of input features.
    hidden_sizes : list of int
        List of hidden layer sizes.
    num_classes : int
        Number of output classes.
    dropout_rate : float
        Dropout rate for regularization.
    num_residual_blocks : int
        Number of residual blocks to use.

    Attributes
    -----------
    layers : nn.ModuleList
        List of network layers including residual blocks.
    input_size : int
        Number of input features.
    num_classes : int
        Number of output classes.
    """


    def __init__(self, input_size: int = 12, hidden_sizes: list = [128, 64, 32], 
                 num_classes: int = 2, dropout_rate: float = 0.3, num_residual_blocks: int = 2):
        super(HepatitisNet, self).__init__()
        
        self.input_size = input_size
        self.num_classes = num_classes

        # Build network architecture
        layers = nn.ModuleList()
        
        # Input projection
        layers.append(nn.Linear(input_size, hidden_sizes[0]))
        layers.append(nn.LayerNorm(hidden_sizes[0]))
        layers.append(nn.ReLU())
        layers.append(nn.Dropout(dropout_rate))
        
        # Add residual blocks at each hidden layer
        for i in range(len(hidden_sizes) - 1):
            # Add residual blocks
            for _ in range(num_residual_blocks):
                layers.append(ResidualBlock(hidden_sizes[i], dropout_rate))
            
            # Project to next hidden size
            layers.append(nn.Linear(hidden_sizes[i], hidden_sizes[i + 1]))
            layers.append(nn.LayerNorm(hidden_sizes[i + 1]))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout_rate))
        
        # Add final residual blocks
        for _ in range(num_residual_blocks):
            layers.append(ResidualBlock(hidden_sizes[-1], dropout_rate))
        
        # Output projection
        layers.append(nn.Linear(hidden_sizes[-1], num_classes))
        
        self.layers = layers
        self._initialize_weights()
    
    def _initialize_weights(self):
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.constant_(module.bias, 0)
            elif isinstance(module, nn.BatchNorm1d):
                nn.init.constant_(module.weight, 1)
                nn.init.constant_(module.bias, 0)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for layer in self.layers:
            x = layer(x)
        return x


def evaluate_model(model: nn.Module, test_loader: DataLoader, device: str = 'cpu') -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Evaluate the model on the test dataset.
    
    Parameters
    -----------
    model : nn.Module
        The trained model to be evaluated.
    test_loader : DataLoader
        DataLoader for the test dataset.
    device : str
        Device to run the evaluation on (default: 'cpu').

    Returns
    -----------
    tuple[np.ndarray, np.ndarray, np.ndarray]
        - y_true: Ground truth labels.
        - y_pred: Predicted labels.
        - y_probs: Predicted probabilities.

    Examples
    ---------
    >>> y_true, y_pred, y_probs = evaluate_model(model, test_loader, device='cuda')
    """
    model.eval()
    y_true = []
    y_pred = []
    y_probs = []
    
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            probs = torch.softmax(output, dim=1)
            pred = output.argmax(dim=1)
            
            y_true.extend(target.cpu().numpy())
            y_pred.extend(pred.cpu().numpy())
            y_probs.extend(probs.cpu().numpy())
    
    return np.array(y_true), np.array(y_pred), np.array(y_probs)

def save_model(model: nn.Module, filepath: str, additional_info: dict = None) -> None:
    """
    Save the model to a file.

    Parameters
    -----------
    model : nn.Module
        The model to be saved.
    filepath : str
        Path to the file where the model will be saved.
    additional_info : dict, optional
        Any additional information to save with the model (e.g., training parameters).
        

    Examples
    ---------
    >>> save_model(model, 'models/hepatitis_model.pth', {'input_size': 12, 'num_classes': 2})
    """

    torch.save({
        'model_state_dict': model.state_dict(),
        'model_class': model.__class__.__name__,
        'additional_info': additional_info
    }, filepath, _use_new_zipfile_serialization=False)
    print(f"Model saved to: {filepath}")

def load_model(filepath: str, model_class: type[HepatitisNet] = HepatitisNet, input_size: int = 12) -> tuple[nn.Module, dict]:
    """
    Load a model from a file.
    
    Parameters
    -----------
    filepath : str
        Path to the file from which the model will be loaded.
    model_class : type
        The class of the model to be loaded (default: HepatitisNet).
    input_size : int
        Number of input features (default: 12).

    Returns
    -----------
    tuple[nn.Module, dict]
        - model: The loaded model.
        - additional_info: Any additional information saved with the model.
    
    Examples
    ---------
    >>> model, info = load_model('models/hepatitis_model.pth')
    >>> print(info)
    """
    checkpoint = torch.load(filepath, map_location='cpu', weights_only=False)
    
    model = model_class(input_size=input_size)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    return model, checkpoint.get('additional_info', None)

class TorchWrapper(BaseEstimator, ClassifierMixin):
    """
    A wrapper to make PyTorch models compatible with scikit-learn.
    
    Parameters
    -----------
    model : HepatitisNet
        The PyTorch model instance.
    device : str
        Device to run inference on ('cpu' or 'cuda').
    classes : array-like
        Class labels for the classifier.

    Attributes
    -----------
    model : HepatitisNet
        The PyTorch model instance.
    device : str
        Device to run inference on ('cpu' or 'cuda').
    classes_ : array-like
        Class labels for the classifier.

    Examples
    ---------
    >>> model, _ = load_model('models/hepatitis_model.pth')
    >>> wrapper = TorchWrapper(model, device='cuda', classes=[0, 1])
    >>> CalibrationDisplay.from_estimator(wrapper, X_test, y_test, n_bins=10)
    """

    def __init__(self, model: type[HepatitisNet], device: str, classes: any):
        self.model = model
        self.device = device
        self.classes_ = classes
    def fit(self, X: np.ndarray, y: np.ndarray) -> TorchWrapper:
        return self
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        X_tensor = torch.FloatTensor(X).to(self.device)
        with torch.no_grad():
            outputs = self.model(X_tensor)
            probs = torch.softmax(outputs, dim=1).cpu().numpy()
        return probs
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.argmax(self.predict_proba(X), axis=1)

