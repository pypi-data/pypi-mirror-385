import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
import os
import urllib.request
import zipfile
import torch
from torch.utils.data import Dataset

class HepatitisDataset(Dataset):
    """
    Custom PyTorch Dataset for Hepatitis data.
    
    This dataset can be reused with different models and training approaches.

    Parameters
    -----------
    X : np.ndarray or pd.DataFrame
        Feature matrix.
    y : np.ndarray or pd.Series    
        Target vector.

    Attributes
    -----------
    X : torch.FloatTensor
        Feature matrix as a FloatTensor.
    y : torch.LongTensor
        Target vector as a LongTensor.
        
    Examples
    ---------
    >>> from src.data import HepatitisDataset
    >>> dataset = HepatitisDataset(X_train, y_train)
    >>> loader = DataLoader(dataset, batch_size=32, shuffle=True)
    """

    def __init__(self, X: np.ndarray, y: np.ndarray):
        self.X = torch.FloatTensor(X)
        self.y = torch.LongTensor(y.values if hasattr(y, 'values') else y)
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx: int):
        return self.X[idx], self.y[idx]

def download_dataset(target_path: str = 'data/raw/hepatitis_data.csv') -> bool:
    """
    Download the Hepatitis C dataset from a public source if not already present.
    
    Parameters
    ------------
    target_path : str
        Path where the dataset should be saved.
        
    Returns
    ------------
    bool
        True if download was successful or file already exists, False otherwise.
        
    Examples
    ---------
    >>> download_dataset()
    True
    """
    if os.path.exists(target_path):
        print(f"Dataset already exists at: {target_path}")
        return True
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    
    # URL to a reliable source - using a direct CSV link
    # This is the UCI ML Repository version of the dataset
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00571/hcvdat0.csv"
    
    try:
        print(f"Downloading dataset from {url}...")
        urllib.request.urlretrieve(url, target_path)
        print(f"✅ Dataset downloaded successfully to: {target_path}")
        return True
    except Exception as e:
        print(f"❌ Error downloading dataset: {e}")
        print("\n📌 Alternative: Download manually from:")
        print("   https://www.kaggle.com/datasets/fedesoriano/hepatitis-c-dataset")
        print(f"   and place it in: {target_path}")
        return False

def load_raw_data(filepath: str ='data/raw/hepatitis_data.csv') -> pd.DataFrame:
    '''
    Load raw data from a CSV file. If the file doesn't exist, attempts to download it automatically.
    
    Parameters
    ------------
    filepath : str
        Path to the CSV file to be loaded.

    Returns
    ------------
    pd.DataFrame
        Loaded dataset as a pandas DataFrame.   

    Examples
    ---------
    >>> df = load_raw_data()
    >>> df.head()
    '''

    try:
        df = pd.read_csv(filepath)
        # Rename the unnamed index column to Patient ID
        if 'Unnamed: 0' in df.columns:
            df = df.rename(columns={'Unnamed: 0': 'Patient ID'})
        print(f"Dataset loaded successfully: {df.shape}")
        return df
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        print("Attempting to download dataset automatically...")
        
        if download_dataset(filepath):
            # Try loading again after download
            try:
                df = pd.read_csv(filepath)
                if 'Unnamed: 0' in df.columns:
                    df = df.rename(columns={'Unnamed: 0': 'Patient ID'})
                print(f"Dataset loaded successfully: {df.shape}")
                return df
            except Exception as e:
                print(f"Error loading downloaded dataset: {e}")
                return None
        else:
            print("Please download the dataset manually from Kaggle and place it in data/raw/")
            return None

def get_data_info(df):
    if df is None:  
        return None
    
    info = {
        'shape': df.shape,
        'columns': list(df.columns),
        'missing_values': df.isnull().sum(),
        'target_distribution': df['Category'].value_counts() if 'Category' in df.columns else None,
        'data_types': df.dtypes
    }
    
    return info

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and preprocess the dataset.
    
    Parameters
    ------------
    df : pd.DataFrame
        Raw dataset to be cleaned.
        
    Returns
    ------------
    pd.DataFrame
        Cleaned dataset with necessary transformations applied.

    Examples
    ---------
    >>> cleaned_df = clean_data(df)
    >>> cleaned_df.head()
    """

    if df is None:
        return None
    data = df.copy()

    # Keep Patient ID column for identification
    # Remove it only if needed for modeling
    if 'Unnamed: 0' in data.columns:
        data = data.drop('Unnamed: 0', axis=1)
    
    def simplify_category(category: str) -> int:
        """
        Simplify the category labels.

        Parameters
        ------------
        category : str
            Original category label.

        Returns
        ------------
        int
            Simplified category label. 0 for healthy, 1 for hepatitis C.

        Examples
        ---------
        >>> simplify_category('0=Blood Donor')
        0
        >>> simplify_category('1=Hepatitis C')
        1
        """

        if category in ['0=Blood Donor', '0s=suspect Blood Donor']:
            return 0
        else:
            return 1
    
    data['target'] = data['Category'].apply(simplify_category)
    
    sex_encoder = LabelEncoder()
    data['sex_encoded'] = sex_encoder.fit_transform(data['Sex'])
    
    print(f"Data cleaned successfully")
    print(f"Healthy: {sum(data['target'] == 0)} samples")
    print(f"Hepatitis C: {sum(data['target'] == 1)} samples")
    
    return data, sex_encoder

def prepare_features(data: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare features for modeling.

    Parameters
    ------------
    data : pd.DataFrame
        Cleaned dataset with necessary transformations applied.

    Returns
    ------------
    pd.DataFrame
        Feature matrix ready for modeling.

    Examples
    ---------
    >>> prepared_features = prepare_features(cleaned_df)
    >>> prepared_features.head()
    """

    if data is None:
        return None
    feature_columns = ['Age', 'ALB', 'ALP', 'ALT', 'AST', 'BIL', 'CHE', 'CHOL', 'CREA', 'GGT', 'PROT', 'sex_encoded']
    
    X = data[feature_columns]
    y = data['target']

    imputer = SimpleImputer(strategy='median')
    X_imputed = pd.DataFrame(
        imputer.fit_transform(X), 
        columns=X.columns, 
        index=X.index
    )
    
    print(f"Features prepared: {X_imputed.shape}")
    print(f"Missing values after imputation: {X_imputed.isnull().sum().sum()}")
    
    return X_imputed, y, imputer

def split_and_scale_data(X: pd.DataFrame, y: pd.Series, test_size: float = 0.2, random_state: int = 42) -> tuple[np.ndarray, np.ndarray, pd.Series, pd.Series, StandardScaler]:
    """
    Split and scale the dataset.

    Parameters
    ------------
    X : pd.DataFrame
        Feature matrix.
    y : pd.Series
        Target vector.
    test_size : float
        Proportion of the dataset to include in the test split.
    random_state : int
        Random seed for reproducibility.

    Returns
    ------------
    tuple
        (X_train_scaled, X_test_scaled, y_train, y_test, scaler)
    """

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print(f"✅ Data split and scaled:")
    print(f"   Training set: {X_train_scaled.shape}")
    print(f"   Test set: {X_test_scaled.shape}")
    
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler
