from __future__ import annotations
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.metrics import confusion_matrix, roc_curve, auc, precision_recall_curve
import pandas as pd

plt.style.use('default')
sns.set_palette("inferno")

def plot_data_overview(df: pd.DataFrame) -> plt.Figure:
    """
    Generate an overview of the dataset with key statistics and visualizations. \
    Includes a bar plot of disease categories, a histogram of age distribution  \
    of patients, a bar plot of sex distribution, and missing value counts per column.

    Parameters
    ----------
    df: pd.DataFrame
        DataFrame containing the data

    Returns
    -------
    fig: plt.Figure
        Matplotlib figure object containing the overview plots.
    """

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    if 'Category' in df.columns:
        category_counts = df['Category'].value_counts()
        colors = sns.color_palette("inferno", len(category_counts))
        
        # Create a single stacked bar
        bottom = 0
        bar_width = 0.6
        for i, (category, count) in enumerate(category_counts.items()):
            axes[0,0].bar(['Total'], [count], bottom=bottom, color=colors[i], 
                         label=f'{category}: {count}', width=bar_width)
            bottom += count
        
        axes[0,0].set_title('Disease Categories')
        axes[0,0].set_xlabel('Population')
        axes[0,0].set_ylabel('Count')
        axes[0,0].legend(loc='lower left')
        axes[0,0].tick_params(axis='x', rotation=0)
    
    if 'Age' in df.columns:
        df['Age'].hist(bins=20, ax=axes[0,1], color=sns.color_palette("inferno", 10)[0])
        axes[0,1].set_title('Age Distribution')
        axes[0,1].set_xlabel('Age (years)')
        axes[0,1].set_ylabel('Frequency')
    
    if 'Sex' in df.columns:
        sex_counts = df['Sex'].value_counts()
        colors = sns.color_palette("inferno", len(sex_counts))
        
        # Create a single stacked bar
        bottom = 0
        bar_width = 0.6
        for i, (sex, count) in enumerate(sex_counts.items()):
            axes[1,0].bar(['Total'], [count], bottom=bottom, color=colors[i], 
                         label=f'{sex}: {count}', width=bar_width)
            bottom += count
        
        axes[1,0].set_title('Sex Distribution')
        axes[1,0].set_xlabel('Population')
        axes[1,0].set_ylabel('Count')
        axes[1,0].legend()
        axes[1,0].tick_params(axis='x', rotation=0)
    
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if len(missing) > 0:
        missing.plot(kind='bar', ax=axes[1,1], color=sns.color_palette("inferno", len(missing)))
        axes[1,1].set_title('Missing Values by Column')
        axes[1,1].set_ylabel('Count')
        axes[1,1].tick_params(axis='x', rotation=45)
        axes[1,1].yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    else:
        axes[1,1].text(0.5, 0.5, 'No Missing Values', ha='center', va='center', transform=axes[1,1].transAxes)
        axes[1,1].set_title('Missing Values')
    
    plt.tight_layout()
    return fig

def plot_correlation_matrix(df: pd.DataFrame) -> plt.Figure:
    """
    Plot a clustered correlation matrix for numeric features in the DataFrame.
    
    Parameters
    ----------
    df: pd.DataFrame
        DataFrame containing the data

    Returns
    -------
    plt.Figure
        Matplotlib figure object containing the correlation matrix plot.
    """

    from scipy.cluster.hierarchy import linkage, dendrogram
    from scipy.spatial.distance import squareform
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) > 1:
        plt.figure(figsize=(12, 10))
        correlation_matrix = df[numeric_cols].corr()
        
        # Perform hierarchical clustering on the correlation matrix
        # Convert correlation to distance (1 - |correlation|)
        distance_matrix = 1 - np.abs(correlation_matrix)
        condensed_distances = squareform(distance_matrix, checks=False)
        linkage_matrix = linkage(condensed_distances, method='average')
        
        # Get the order from clustering
        dendro = dendrogram(linkage_matrix, labels=correlation_matrix.columns, no_plot=True)
        cluster_order = dendro['leaves']
        
        # Reorder the correlation matrix
        ordered_corr = correlation_matrix.iloc[cluster_order, cluster_order]
        
        # Create mask for upper triangle
        mask = np.triu(np.ones_like(ordered_corr, dtype=bool))
        
        sns.heatmap(ordered_corr, mask=mask, annot=True, cmap='inferno', 
                   center=0, square=True, fmt='.2f')
        plt.title('Feature Correlation Matrix (Clustered)')
        plt.tight_layout()
        return plt.gcf()
    else:
        print("Not enough numeric columns for correlation matrix")
        return None

def plot_feature_distributions(df: pd.DataFrame, target_col: str = 'target') -> plt.Figure:
    """
    Create histograms of feature distributions for each numeric feature, separated by target class.
    
    Parameters
    ----------
    df: pd.DataFrame
        DataFrame containing the data
    target_col: str
        Name of the target column to separate classes. Default is 'target'.

    Returns
    -------
    plt.Figure
        Matplotlib figure object containing the feature distribution histograms.
    """

    numeric_cols = ['ALB', 'ALP', 'ALT', 'AST', 'BIL', 'CHE', 'CHOL', 'CREA', 'GGT', 'PROT']
    available_cols = [col for col in numeric_cols if col in df.columns]
    
    if not available_cols:
        print("No feature columns found")
        return None
    
    n_cols = 5
    n_rows = (len(available_cols) + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 4*n_rows))
    axes = axes.flatten() if n_rows > 1 else [axes] if n_rows == 1 else axes
    
    for i, feature in enumerate(available_cols):
        if i < len(axes):
            if target_col in df.columns:
                for target_value in df[target_col].unique():
                    subset = df[df[target_col] == target_value][feature]
                    label = 'Healthy' if target_value == 0 else 'Hepatitis C'
                    axes[i].hist(subset, alpha=0.7, label=label, bins=20, color=sns.color_palette("inferno", 2)[target_value])
                axes[i].set_title(f'{feature} Distribution')
                axes[i].set_xlabel(feature)
                axes[i].set_ylabel('Frequency')
                axes[i].legend()
            else:
                df[feature].hist(bins=20, ax=axes[i])
                axes[i].set_title(f'{feature} Distribution')
    
    for i in range(len(available_cols), len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    return fig

def plot_violin_with_outliers(df, numeric_cols=None):
    """
    Create violin plots with overlaid box plots to show outliers for each numeric feature.
    
    Parameters
    ----------
    df: pd.DataFrame
        DataFrame containing the data
    numeric_cols: list[str]
        List of column names to plot. If None, uses default hepatitis C features.

    Returns
    -------
    plt.Figure
        Matplotlib figure object containing the violin plots with outliers.
    """
    if numeric_cols is None:
        numeric_cols = ['Age','ALB','ALP','ALT','AST','BIL','CHE','CHOL','CREA','GGT','PROT']
    
    # Filter columns that exist in the dataframe
    available_cols = [col for col in numeric_cols if col in df.columns]
    
    if not available_cols:
        print("No numeric columns found")
        return None
    
    # Create subplots arranged horizontally
    fig, axes = plt.subplots(1, len(available_cols), figsize=(20, 6))
    colors = sns.color_palette("inferno", len(available_cols))
    
    # Handle case where there's only one column
    if len(available_cols) == 1:
        axes = [axes]
    
    for i, col in enumerate(available_cols):
        # Create violin plot
        sns.violinplot(y=df[col], ax=axes[i], color=colors[i], alpha=0.7)
        # Add box plot to show outliers and quartiles
        sns.boxplot(y=df[col], ax=axes[i], width=0.3, boxprops={'facecolor':'None'}, 
                   showfliers=True, flierprops={'marker':'o', 'markersize':3, 'markerfacecolor':'red'})
        axes[i].set_title(col, fontsize=12)
        axes[i].set_xlabel('')
        axes[i].set_ylabel('Values' if i == 0 else '')
    
    plt.suptitle("Violin Plots with Outliers for Each Feature", fontsize=16, y=1.02)
    plt.tight_layout()
    return fig

def plot_training_history(history: dict) -> plt.Figure:
    """
    Plot training and validation loss and accuracy over epochs.

    Parameters
    ----------
    history: dict
        Dictionary containing training history with keys 'train_loss', 'val_loss', 'train_acc', 'val_acc'.

    Returns
    -------
    plt.Figure
        Matplotlib figure object containing the training history plots.
    """

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    axes[0].plot(history['train_loss'], label='Training Loss', linewidth=2, color=sns.color_palette("inferno", 10)[0])
    axes[0].plot(history['val_loss'], label='Validation Loss', linewidth=2, color=sns.color_palette("inferno", 10)[-1])
    axes[0].set_title('Model Loss')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(history['train_acc'], label='Training Accuracy', linewidth=2, color=sns.color_palette("inferno", 10)[0])
    axes[1].plot(history['val_acc'], label='Validation Accuracy', linewidth=2, color=sns.color_palette("inferno", 10)[-1])
    axes[1].set_title('Model Accuracy')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Accuracy (%)')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def plot_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, class_names: list[str] = ['No Hepatitis C', 'Hepatitis C'], use_percentages: bool = True) -> plt.Figure:
    """
    Plot confusion matrix with option for percentages or absolute values.
    
    Parameters
    -----------
    y_true: np.ndarray
        Ground truth labels.
    y_pred: np.ndarray
        Predicted labels
    class_names: string
        List of class names for labels
    use_percentages: bool
        If True, show percentages by true class; if False, show absolute counts

    Returns
    --------
    plt.Figure
        Matplotlib figure object containing the confusion matrix plot.
    """
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(8, 6))
    
    if use_percentages:
        # Calculate percentage confusion matrix (row-wise normalization)
        cm_percent = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100
        sns.heatmap(cm_percent, annot=True, fmt='.1f', cmap='inferno',
                    xticklabels=class_names, yticklabels=class_names)
        plt.title('Confusion Matrix (Percentages)', fontsize=16)
    else:
        sns.heatmap(cm, annot=True, fmt='d', cmap='inferno',
                    xticklabels=class_names, yticklabels=class_names)
        plt.title('Confusion Matrix (Counts)', fontsize=16)
    
    plt.xlabel('Predicted', fontsize=12)
    plt.ylabel('Actual', fontsize=12)

    # Add accuracy information
    accuracy = np.trace(cm) / np.sum(cm)
    plt.figtext(0.1, 0.02, f'Overall Accuracy: {accuracy:.3f}', fontsize=12)
    
    plt.tight_layout()
    return plt.gcf()

def plot_roc_curve(y_true: np.ndarray, y_probs: np.ndarray) -> plt.Figure:
    """
    Plot ROC curve with AUC.

    Parameters
    -----------
    y_true: np.ndarray
        Ground truth binary labels.
    y_probs: np.ndarray
        Predicted probabilities for the positive class.

    Returns
    --------
    plt.Figure
        Matplotlib figure object containing the ROC curve plot.

    Examples
    ---------
    >>> fig = plot_roc_curve(y_true, y_probs)
    >>> fig.show()
    """

    fpr, tpr, _ = roc_curve(y_true, y_probs[:, 1])
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC Curve (AUC = {roc_auc:.3f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC) Curve')
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    return plt.gcf()

def plot_precision_recall_curve(y_true: np.ndarray, y_probs: np.ndarray) -> plt.Figure:
    """
    Plot precision-recall curve with AUC.

    Parameters
    -----------
    y_true: np.ndarray
        Ground truth binary labels.
    y_probs: np.ndarray
        Predicted probabilities for the positive class.

    Returns
    --------
    plt.Figure
        Matplotlib figure object containing the precision-recall curve plot.

    Examples
    ---------
    >>> fig = plot_precision_recall_curve(y_true, y_probs)
    >>> fig.show()
    """
    precision, recall, _ = precision_recall_curve(y_true, y_probs[:, 1])
    pr_auc = auc(recall, precision)
    
    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, color='blue', lw=2, label=f'PR Curve (AUC = {pr_auc:.3f})')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.legend(loc="lower left")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    return plt.gcf()

def plot_prediction_confidence(y_true: np.ndarray, y_probs: np.ndarray, class_names: list[str] = ['Healthy', 'Hepatitis C']) -> plt.Figure:
    """
    Plot histograms of prediction confidence for each class, separated by predicted and true labels.

    Parameters
    -----------
    y_true: np.ndarray
        Ground truth binary labels.
    y_probs: np.ndarray
        Predicted probabilities for each class (shape: [n_samples, n_classes]).
    class_names: list of str
        Names of the classes for labeling.

    Returns
    --------
    plt.Figure
        Matplotlib figure object containing the prediction confidence histograms.

    Examples
    ---------
    >>> fig = plot_prediction_confidence(y_true, y_probs)
    >>> fig.show()
    """
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    y_pred = np.argmax(y_probs, axis=1)
    max_probs = np.max(y_probs, axis=1)
    
    for class_idx in [0, 1]:
        mask = y_pred == class_idx
        if np.any(mask):
            axes[0].hist(max_probs[mask], bins=20, alpha=0.7, 
                        label=f'Predicted: {class_names[class_idx]}')
    
    axes[0].set_title('Prediction Confidence by Predicted Class')
    axes[0].set_xlabel('Confidence')
    axes[0].set_ylabel('Frequency')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    for class_idx in [0, 1]:
        mask = y_true == class_idx
        if np.any(mask):
            axes[1].hist(max_probs[mask], bins=20, alpha=0.7, 
                        label=f'True: {class_names[class_idx]}')
    
    axes[1].set_title('Prediction Confidence by True Class')
    axes[1].set_xlabel('Confidence')
    axes[1].set_ylabel('Frequency')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig
