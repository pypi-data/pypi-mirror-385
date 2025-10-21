import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
import pickle
import os
import sys
import time

try:
    from src.models import HepatitisNet, evaluate_model, save_model, load_model
    from src.data import load_raw_data, clean_data, prepare_features, HepatitisDataset
    from src.train import ModelTrainer
    from sklearn.preprocessing import LabelEncoder
    from torch.utils.data import DataLoader
    # Try to import visualization functions
    try:
        from src.visualization import plot_correlation_matrix, plot_feature_distributions
    except ImportError:
        st.warning("Visualization functions not found. Using built-in alternatives.")
        def plot_correlation_matrix(data):
            return None
        def plot_feature_distributions(data):
            return None
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Hepatitis C Classification Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ff7f0e;
        margin: 1rem 0;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def load_sample_data():
    """Load and cache sample data"""
    try:
        # Try to load real data first  
        return load_raw_data()
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

@st.cache_data
def prepare_data(data):
    """Prepare and preprocess data"""
    if data is None:
        return None, None, None, None, None, None
    
    try:
        # Implement preprocessing directly in app.py
        # Clean the data
        cleaned_data, sex_encoder = clean_data(data)
        
        # Prepare features  
        X_processed, y_processed, imputer = prepare_features(cleaned_data)
        
        # Split the data
        X_train, X_temp, y_train, y_temp = train_test_split(
            X_processed, y_processed, test_size=0.4, random_state=42, stratify=y_processed
        )
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
        )
        
        # Scale the features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        X_test_scaled = scaler.transform(X_test)
        
        return X_train_scaled, X_val_scaled, X_test_scaled, y_train, y_val, y_test
        
    except Exception as e:
        st.error(f"Error preprocessing data: {e}")
        return None, None, None, None, None, None

def main():
    st.markdown('<div class="main-header">🏥 Hepatitis C Classification Dashboard</div>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a section:",
        ["Data Exploration", "Model Training", "Model Evaluation"]
    )
    
    # Load data
    data = load_sample_data()
    
    if data is None:
        st.error("Failed to load data. Please check your data files.")
        return
    
    # Prepare data
    X_train, X_val, X_test, y_train, y_val, y_test = prepare_data(data)
    
    if page == "Data Exploration":
        data_exploration_page(data)
    elif page == "Model Training":
        model_training_page(X_train, X_val, y_train, y_val, data)
    elif page == "Model Evaluation":
        model_evaluation_page(X_test, y_test, data)

def data_exploration_page(data):
    st.markdown('<div class="section-header">📊 Data Exploration</div>', unsafe_allow_html=True)
    
    # Dataset Overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Samples", len(data))
    with col2:
        st.metric("Features", len(data.columns) - 1)
    with col3:
        # Calculate positive rate
        if 'target' in data.columns:
            positive_rate = (data['target'] == 1).mean() * 100
        else:
            # Simple check for non-blood donor cases
            positive_rate = (~data['Category'].str.contains('Blood Donor', na=False)).mean() * 100
        st.metric("Positive Rate", f"{positive_rate:.1f}%")
    
    # Display sample data
    st.subheader("Sample Data")
    st.dataframe(data.head(10))
    
    # Basic statistics
    st.subheader("Statistical Summary")
    st.dataframe(data.describe())
    
    # Feature distributions
    st.subheader("Feature Distributions")
    
    # Select only numeric features to plot
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    feature_cols = [col for col in numeric_cols if col not in ['Category', 'target']]
    
    selected_features = st.multiselect(
        "Select features to visualize:",
        feature_cols,
        default=feature_cols[:4] if len(feature_cols) >= 4 else feature_cols
    )
    
    if selected_features:
        # Create simple distribution plots without categories
        fig = make_subplots(
            rows=(len(selected_features) + 1) // 2, 
            cols=2,
            subplot_titles=selected_features
        )
        
        for i, feature in enumerate(selected_features):
            row = i // 2 + 1
            col = i % 2 + 1
            
            # Simple histogram
            fig.add_trace(
                go.Histogram(
                    x=data[feature],
                    name=feature,
                    showlegend=False
                ),
                row=row, col=col
            )
        
        fig.update_layout(height=300 * ((len(selected_features) + 1) // 2))
        st.plotly_chart(fig, use_container_width=True)
    
    # Correlation matrix
    st.subheader("Correlation Matrix")
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    corr_matrix = data[numeric_cols].corr()
    
    fig = px.imshow(
        corr_matrix,
        title="Feature Correlation Matrix",
        color_continuous_scale="RdBu",
        aspect="auto"
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)
    
    # Class distribution
    st.subheader("Class Distribution")
    
    # Use target column if available, otherwise create binary from Category
    if 'target' in data.columns:
        class_counts = data['target'].value_counts().sort_index()
        labels = ['Healthy', 'Hepatitis C']
    else:
        # Create simple binary classification
        healthy_mask = data['Category'].str.contains('Blood Donor', na=False)
        binary_target = (~healthy_mask).astype(int)
        class_counts = pd.Series(binary_target).value_counts().sort_index()
        labels = ['Healthy', 'Hepatitis C']
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            values=class_counts.values,
            names=labels,
            title="Class Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            x=labels,
            y=class_counts.values,
            title="Class Counts"
        )
        st.plotly_chart(fig, use_container_width=True)

def model_training_page(X_train, X_val, y_train, y_val, data):
    st.markdown('<div class="section-header">🚀 Model Training</div>', unsafe_allow_html=True)
    
    # Training parameters
    st.subheader("Training Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        epochs = st.slider("Number of Epochs", 10, 100, 50)
        learning_rate = st.selectbox("Learning Rate", [0.001, 0.01, 0.1], index=0)
        batch_size = st.selectbox("Batch Size", [16, 32, 64], index=1)
    
    with col2:
        hidden_sizes = st.text_input("Hidden Layer Sizes (comma-separated)", "128,64,32")
        dropout_rate = st.slider("Dropout Rate", 0.0, 0.5, 0.3)
        num_residual_blocks = st.slider("Residual Blocks", 1, 4, 2)
    
    # Parse hidden sizes
    try:
        hidden_sizes_list = [int(x.strip()) for x in hidden_sizes.split(',')]
    except:
        hidden_sizes_list = [128, 64, 32]
        st.warning("Invalid hidden sizes format. Using default: [128, 64, 32]")
    
    # Training button
    if st.button("Start Training", type="primary"):
        # Create model
        input_size = X_train.shape[1]
        model = HepatitisNet(
            input_size=input_size,
            hidden_sizes=hidden_sizes_list,
            num_classes=2,
            dropout_rate=dropout_rate,
            num_residual_blocks=num_residual_blocks
        )
        
        # Create data loaders
        train_dataset = HepatitisDataset(X_train, y_train)
        val_dataset = HepatitisDataset(X_val, y_val)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        
        # Create trainer
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        trainer = ModelTrainer(model, device)
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Create placeholders for real-time plots
        col1, col2 = st.columns(2)
        with col1:
            loss_chart = st.empty()
        with col2:
            acc_chart = st.empty()
        
        # Modified training loop for real-time updates
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-4)
        
        history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
        
        start_time = time.time()
        
        for epoch in range(epochs):
            # Training
            train_loss, train_acc = trainer.train_epoch(train_loader, criterion, optimizer)
            val_loss, val_acc = trainer.validate_epoch(val_loader, criterion)
            
            # Update history
            history['train_loss'].append(train_loss)
            history['train_acc'].append(train_acc)
            history['val_loss'].append(val_loss)
            history['val_acc'].append(val_acc)
            
            # Update progress
            progress = (epoch + 1) / epochs
            progress_bar.progress(progress)
            status_text.text(f'Epoch {epoch + 1}/{epochs} - Train Loss: {train_loss:.4f}, Val Acc: {val_acc:.2f}%')
            
            # Update plots every 5 epochs
            if epoch % 5 == 0 or epoch == epochs - 1:
                # Loss plot
                with loss_chart.container():
                    fig_loss = go.Figure()
                    fig_loss.add_trace(go.Scatter(
                        y=history['train_loss'],
                        mode='lines',
                        name='Train Loss',
                        line=dict(color='blue')
                    ))
                    fig_loss.add_trace(go.Scatter(
                        y=history['val_loss'],
                        mode='lines',
                        name='Validation Loss',
                        line=dict(color='red')
                    ))
                    fig_loss.update_layout(title='Training Loss', xaxis_title='Epoch', yaxis_title='Loss')
                    st.plotly_chart(fig_loss, use_container_width=True)
                
                # Accuracy plot
                with acc_chart.container():
                    fig_acc = go.Figure()
                    fig_acc.add_trace(go.Scatter(
                        y=history['train_acc'],
                        mode='lines',
                        name='Train Accuracy',
                        line=dict(color='blue')
                    ))
                    fig_acc.add_trace(go.Scatter(
                        y=history['val_acc'],
                        mode='lines',
                        name='Validation Accuracy',
                        line=dict(color='red')
                    ))
                    fig_acc.update_layout(title='Training Accuracy', xaxis_title='Epoch', yaxis_title='Accuracy (%)')
                    st.plotly_chart(fig_acc, use_container_width=True)
        
        training_time = time.time() - start_time
        
        # Training summary
        st.success("Training completed!")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Final Train Accuracy", f"{history['train_acc'][-1]:.2f}%")
        with col2:
            st.metric("Final Val Accuracy", f"{history['val_acc'][-1]:.2f}%")
        with col3:
            st.metric("Training Time", f"{training_time:.2f}s")
        
        # Save model
        model_dir = os.path.join(os.path.dirname(__file__), 'saved_models')
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, 'hepatitis_model.pth')
        
        additional_info = {
            'input_size': input_size,
            'hidden_sizes': hidden_sizes_list,
            'num_classes': 2,
            'dropout_rate': dropout_rate,
            'num_residual_blocks': num_residual_blocks,
            'final_val_acc': history['val_acc'][-1]
        }
        
        save_model(model, model_path, additional_info)
        st.info(f"Model saved to: {model_path}")

def model_evaluation_page(X_test, y_test, data):
    st.markdown('<div class="section-header">📈 Model Evaluation</div>', unsafe_allow_html=True)
    
    # Check if saved model exists
    model_path = os.path.join(os.path.dirname(__file__), 'saved_models', 'hepatitis_model.pth')
    
    if not os.path.exists(model_path):
        st.warning("No trained model found. Please train a model first in the 'Model Training' section.")
        return
    
    # Load model
    try:
        model, model_info = load_model(model_path, input_size=X_test.shape[1])
        st.success("Model loaded successfully!")
        
        if model_info:
            st.subheader("Model Information")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Input Size", model_info.get('input_size', 'N/A'))
            with col2:
                st.metric("Hidden Layers", str(model_info.get('hidden_sizes', 'N/A')))
            with col3:
                st.metric("Validation Accuracy", f"{model_info.get('final_val_acc', 0):.2f}%")
        
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return
    
    # Create test dataset and dataloader
    test_dataset = HepatitisDataset(X_test, y_test)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    # Evaluate model
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = model.to(device)
    y_true, y_pred, y_probs = evaluate_model(model, test_loader, device)
    
    # Performance metrics
    st.subheader("Performance Metrics")
    
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Accuracy", f"{accuracy:.3f}")
    with col2:
        st.metric("Precision", f"{precision:.3f}")
    with col3:
        st.metric("Recall", f"{recall:.3f}")
    with col4:
        st.metric("F1-Score", f"{f1:.3f}")
    
    # Confusion Matrix
    st.subheader("Confusion Matrix")
    cm = confusion_matrix(y_true, y_pred)
    
    fig = px.imshow(
        cm,
        text_auto=True,
        aspect="auto",
        title="Confusion Matrix",
        labels=dict(x="Predicted", y="Actual"),
        x=['Negative', 'Positive'],
        y=['Negative', 'Positive']
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # ROC Curve
    st.subheader("ROC Curve")
    fpr, tpr, _ = roc_curve(y_true, y_probs[:, 1])
    roc_auc = auc(fpr, tpr)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=fpr, y=tpr,
        mode='lines',
        name=f'ROC Curve (AUC = {roc_auc:.3f})',
        line=dict(color='blue', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1],
        mode='lines',
        name='Random Classifier',
        line=dict(color='red', dash='dash')
    ))
    fig.update_layout(
        title='ROC Curve',
        xaxis_title='False Positive Rate',
        yaxis_title='True Positive Rate',
        width=600, height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Prediction examples
    st.subheader("Sample Predictions")
    
    # Select random samples
    sample_indices = np.random.choice(len(X_test), min(10, len(X_test)), replace=False)
    
    for i, idx in enumerate(sample_indices[:5]):  # Show first 5 samples
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"**Sample {i+1}**")
            # Show feature values - use the processed feature names
            feature_names = ['Age', 'ALB', 'ALP', 'ALT', 'AST', 'BIL', 'CHE', 'CHOL', 'CREA', 'GGT', 'PROT', 'sex_encoded']
            # Only use as many features as we actually have
            available_features = min(len(feature_names), X_test.shape[1])
            sample_features = {feature_names[j]: float(X_test[idx, j]) for j in range(available_features)}
            st.json(sample_features)
        
        with col2:
            actual = "Positive" if y_true[idx] == 1 else "Negative"
            st.metric("Actual", actual)
        
        with col3:
            predicted = "Positive" if y_pred[idx] == 1 else "Negative"
            confidence = max(y_probs[idx]) * 100
            st.metric("Predicted", predicted)
            st.metric("Confidence", f"{confidence:.1f}%")
        
        st.divider()
    
    # Feature importance (using model weights)
    st.subheader("Feature Importance Analysis")
    
    # Get first layer weights as proxy for feature importance
    first_layer_weights = model.layers[0].weight.data.cpu().numpy()
    feature_importance = np.abs(first_layer_weights).mean(axis=0)
    
    # Use the correct processed feature names
    feature_names = ['Age', 'ALB', 'ALP', 'ALT', 'AST', 'BIL', 'CHE', 'CHOL', 'CREA', 'GGT', 'PROT', 'sex_encoded']
    # Only use as many features as we actually have
    available_features = min(len(feature_names), len(feature_importance))
    
    importance_df = pd.DataFrame({
        'Feature': feature_names[:available_features],
        'Importance': feature_importance[:available_features]
    }).sort_values('Importance', ascending=True)
    
    fig = px.bar(
        importance_df,
        x='Importance',
        y='Feature',
        orientation='h',
        title='Feature Importance (First Layer Weights)'
    )
    st.plotly_chart(fig, use_container_width=True)

def cli_main():
    """Entry point for command-line interface."""
    import sys
    import subprocess
    
    # Get the path to this file
    app_path = __file__
    
    # Launch Streamlit app
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])

if __name__ == "__main__":
    main()
