"""
Training module for Hepatitis C classification model.

This module contains the ModelTrainer class and training utilities,
separated from model definitions for better code organization.
"""

from __future__ import annotations
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
import time


class ModelTrainer:
    """
    Class to handle training and validation of neural network models.
    
    This trainer can be reused with different models and datasets,
    following the separation of concerns principle.

    Parameters
    -----------
    model : nn.Module
        The neural network model to be trained.
    device : str
        Device to run the training on ('cpu' or 'cuda').
    
    Attributes
    -----------
    model : nn.Module
        The neural network model to be trained.
    device : str
        Device to run the training on ('cpu' or 'cuda').
    history : dict
        Dictionary to store training history (losses and accuracies).
        
    Examples
    ---------
    >>> from src.models import HepatitisNet
    >>> from src.train import ModelTrainer
    >>> model = HepatitisNet(input_size=12)
    >>> trainer = ModelTrainer(model, device='cuda')
    >>> history = trainer.train(train_loader, val_loader, epochs=50)
    """

    def __init__(self, model: nn.Module, device: str = 'cpu'):
        self.model = model.to(device)
        self.device = device
        self.history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}

    def train_epoch(self, train_loader: DataLoader, criterion: nn.Module, optimizer: optim.Optimizer) -> tuple[float, float]:
        """
        Train the model for one epoch.
        
        Parameters
        -----------
        train_loader : DataLoader
            DataLoader for training data.
        criterion : nn.Module
            Loss function.
        optimizer : optim.Optimizer
            Optimizer for updating weights.
            
        Returns
        -----------
        tuple[float, float]
            Average training loss and accuracy for the epoch.
        """
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for data, target in train_loader:
            data, target = data.to(self.device), target.to(self.device)
            
            optimizer.zero_grad()
            output = self.model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            pred = output.argmax(dim=1)
            correct += pred.eq(target).sum().item()
            total += target.size(0)
        
        return total_loss / len(train_loader), 100. * correct / total

    def validate_epoch(self, val_loader: DataLoader, criterion: nn.Module) -> tuple[float, float]:
        """
        Validate the model for one epoch.
        
        Parameters
        -----------
        val_loader : DataLoader
            DataLoader for validation data.
        criterion : nn.Module
            Loss function.
            
        Returns
        -----------
        tuple[float, float]
            Average validation loss and accuracy for the epoch.
        """
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, target in val_loader:
                data, target = data.to(self.device), target.to(self.device)
                output = self.model(data)
                loss = criterion(output, target)
                
                total_loss += loss.item()
                pred = output.argmax(dim=1)
                correct += pred.eq(target).sum().item()
                total += target.size(0)
        
        return total_loss / len(val_loader), 100. * correct / total

    def train(self, train_loader: DataLoader, val_loader: DataLoader, epochs: int = 50, learning_rate: float = 0.001) -> dict:
        """
        Train the model for multiple epochs with early stopping.
        
        Parameters
        -----------
        train_loader : DataLoader
            DataLoader for training data.
        val_loader : DataLoader
            DataLoader for validation data.
        epochs : int
            Maximum number of epochs to train.
        learning_rate : float
            Learning rate for the optimizer.
            
        Returns
        -----------
        dict
            Training history containing losses and accuracies.
            
        Examples
        ---------
        >>> history = trainer.train(train_loader, val_loader, epochs=100, learning_rate=0.001)
        >>> print(f"Best validation accuracy: {max(history['val_acc']):.2f}%")
        """
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate, weight_decay=1e-4)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)
        
        best_val_acc = 0
        patience_counter = 0
        patience = 10
        
        print(f"Training on {self.device}")
        print(f"Epochs: {epochs}, Learning Rate: {learning_rate}")
        print("-" * 50)
        
        start_time = time.time()
        
        for epoch in range(epochs):
            train_loss, train_acc = self.train_epoch(train_loader, criterion, optimizer)
            val_loss, val_acc = self.validate_epoch(val_loader, criterion)
            scheduler.step(val_loss)
            
            self.history['train_loss'].append(train_loss)
            self.history['train_acc'].append(train_acc)
            self.history['val_loss'].append(val_loss)
            self.history['val_acc'].append(val_acc)
            
            if epoch % 10 == 0:
                print(f'Epoch {epoch:3d}: Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.1f}%, '
                      f'Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.1f}%')
            
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                patience_counter = 0
                self.best_model_state = self.model.state_dict().copy()
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"Early stopping at epoch {epoch}")
                    break
        
        self.model.load_state_dict(self.best_model_state)
        training_time = time.time() - start_time
        print(f"\nTraining completed in {training_time:.2f} seconds")
        print(f"Best validation accuracy: {best_val_acc:.2f}%")
        
        return self.history
