# Hepatitis C Predictor

A machine learning project to predict Hepatitis C using PyTorch neural networks.

[![Documentation Status](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://ninjalice.github.io/HEPATITIS_C_MODEL/src.html)

## 🚀 Live Demo

Try the interactive demo without installing anything:

- **[Launch on Hugging Face Spaces](https://huggingface.co/spaces/Krypto02/hepatitis-c-predictor)** (Coming soon!)

Or run it locally:

```bash
streamlit run app.py
```

## Features

- 📊 **Interactive Data Exploration**: Visualize and explore the Hepatitis C dataset
- 🚀 **Model Training Interface**: Train models with custom hyperparameters
- 📈 **Model Evaluation**: Comprehensive performance metrics and visualizations
- 🤖 **Deep Learning**: PyTorch-based neural network with residual connections
- 📦 **Auto-download**: Dataset downloads automatically if not present

## Project Organization

    ├── data/
    │   ├── raw/              <- The original, immutable data dump
    │   └── processed/        <- The final, canonical data sets for modeling
    │
    ├── models/               <- Trained and serialized models
    │
    ├── notebooks/            <- Jupyter notebooks for analysis and modeling
    │   ├── 01-data-exploration.ipynb
    │   ├── 02-data-preprocessing.ipynb
    │   ├── 03-model-training.ipynb
    │   └── 04-model-prediction.ipynb
    │
    ├── reports/              <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures/          <- Generated graphics and figures
    │
    ├── src/                  <- Source code for use in this project
    │   ├── __init__.py
    │   ├── data.py           <- Scripts to download or generate data
    │   ├── features.py       <- Scripts to turn raw data into features
    │   ├── models.py         <- Scripts to train models and make predictions
    │   └── visualization.py  <- Scripts to create exploratory visualizations
    │
    ├── requirements.txt      <- The requirements file for reproducing the environment
    └── README.md            <- The top-level README for developers


## Docs

You can check the modules docs in the docs folder or directly from the deployed version on GH pages here: https://ninjalice.github.io/HEPATITIS_C_MODEL/src.html

## Getting Started

### Option 1: Quick Start (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/Ninjalice/HEPATITIS_C_MODEL.git
   cd HEPATITIS_C_MODEL
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or using `uv`:
   ```bash
   uv sync --frozen
   ```

3. Run the interactive dashboard:
   ```bash
   streamlit run app.py
   ```
   
   The app will automatically download the dataset if not present.

### Option 2: Jupyter Notebooks

Follow the notebooks in order:
1. `01-data-exploration.ipynb` - Explore the dataset
2. `02-data-preprocessing.ipynb` - Clean and prepare data
3. `03-model-training.ipynb` - Train the neural network
4. `04-model-prediction.ipynb` - Make predictions on new data (WIP)

## Dataset

The dataset contains laboratory values from blood donors and Hepatitis C patients:

- **Source**: [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/datasets/HCV+data) / [Kaggle](https://www.kaggle.com/datasets/fedesoriano/hepatitis-c-dataset)
- **Size**: 615 samples
- **Features**: 12 laboratory measurements + age and sex
- **Target**: Binary classification (Healthy vs Hepatitis C)
- **Auto-download**: The app will automatically download the dataset if not present

### Manual Download (Optional)

If auto-download fails, you can manually download from:
1. Kaggle: https://www.kaggle.com/datasets/fedesoriano/hepatitis-c-dataset
2. Place the file in `data/raw/hepatitis_data.csv`

## Model

- **Architecture**: Deep Neural Network with Residual Connections
  - Input Layer: 12 features
  - Hidden Layers: [128, 64, 32] neurons
  - Residual Blocks: 2 per hidden layer
  - Output Layer: 2 classes (Binary classification)
- **Framework**: PyTorch 2.8+
- **Regularization**: Layer Normalization + Dropout (0.3)
- **Expected Accuracy**: ~97.5% on validation set

## 🚀 Deployment

### Deploy to Hugging Face Spaces (Recommended)

1. Create a new Space on [Hugging Face](https://huggingface.co/spaces):
   - Choose **Streamlit** as the SDK
   - Set visibility to Public or Private

2. Push your code to the Space:
   ```bash
   git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/hepatitis-c-predictor
   git push hf main
   ```

3. Your app will be automatically deployed and available at:
   `https://huggingface.co/spaces/YOUR_USERNAME/hepatitis-c-predictor`

### Deploy with Docker

1. Build the Docker image:
   ```bash
   docker build -t hepatitis-c-predictor .
   ```

2. Run the container:
   ```bash
   docker run -p 8501:8501 hepatitis-c-predictor
   ```

3. Access the app at `http://localhost:8501`

### Requirements for Deployment

- Python 3.10
- All dependencies listed in `requirements.txt`
- ~500MB RAM minimum
- Dataset will be downloaded automatically on first run

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Run tests and ensure documentation is updated
5. Commit your changes:
   ```bash
   git commit -m "Add detailed description of your changes"
   ```
6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. Create a Pull Request

### Code Style
- Follow PEP 8 guidelines
- Include docstrings for all functions and classes
- Add comments for complex logic
- Update documentation when changing functionality

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Important Note

⚠️ This model is for educational purposes only. Do not use for actual medical diagnosis. Always consult healthcare professionals.
