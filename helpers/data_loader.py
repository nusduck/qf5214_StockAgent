import pandas as pd
import numpy as np
import os
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

class DataLoader:
    """Utility class for loading and basic preprocessing of data"""
    
    @staticmethod
    def load_data(file_path: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Load data from a file and optimize dtypes
        
        Args:
            file_path: Path to the data file
            
        Returns:
            Tuple of (dataframe, error_message)
        """
        try:
            if not os.path.exists(file_path):
                return None, f"File not found: {file_path}"
            
            # Load data based on file extension
            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path)
            elif file_path.endswith(".xlsx") or file_path.endswith(".xls"):
                df = pd.read_excel(file_path)
            elif file_path.endswith(".json"):
                df = pd.read_json(file_path)
            elif file_path.endswith(".parquet"):
                df = pd.read_parquet(file_path)
            else:
                return None, f"Unsupported file format: {file_path}"
            
            # ----- 新增数据类型转换逻辑 -----
            for col in df.columns:
                if df[col].dtype == "int64":
                    df[col] = df[col].astype("int32")
                elif df[col].dtype == "float64":
                    df[col] = df[col].astype("float32")
            return df, None
        except Exception as e:
            return None, f"Error loading data: {str(e)}"
    
    @staticmethod
    def get_data_info(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get basic information about the dataframe
        
        Args:
            df: Pandas dataframe
            
        Returns:
            Dictionary with basic information
        """
        if df is None:
            return {}
        
        # Basic info
        info = {
            "num_rows": len(df),
            "num_columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "missing_values": df.isnull().sum().to_dict(),
            "memory_usage": df.memory_usage(deep=True).sum(),
        }
        
        # Numeric columns
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        if numeric_cols:
            info["numeric_columns"] = numeric_cols
            info["numeric_stats"] = {
                col: {
                    "min": df[col].min() if not pd.isna(df[col].min()) else None,
                    "max": df[col].max() if not pd.isna(df[col].max()) else None,
                    "mean": df[col].mean().astype(float) if not pd.isna(df[col].mean()) else None,
                    "median": df[col].median().astype(float) if not pd.isna(df[col].median()) else None,
                    "std": df[col].std().astype(float) if not pd.isna(df[col].std()) else None,
                }
                for col in numeric_cols
            }
        
        # Categorical columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if categorical_cols:
            info["categorical_columns"] = categorical_cols
            info["categorical_stats"] = {
                col: {
                    "unique_values": df[col].nunique(),
                    "top_values": df[col].value_counts().head(5).to_dict(),
                }
                for col in categorical_cols
            }
        
        # Datetime columns
        datetime_cols = []
        for col in df.columns:
            try:
                if df[col].dtype == 'datetime64[ns]':
                    datetime_cols.append(col)
                elif df[col].dtype == 'object':
                    # Try to parse as datetime
                    pd.to_datetime(df[col], errors='raise')
                    datetime_cols.append(col)
            except:
                pass
        
        if datetime_cols:
            info["datetime_columns"] = datetime_cols
        
        return info
    
    @staticmethod
    def generate_data_description(df: pd.DataFrame) -> str:
        """
        Generate a textual description of the data
        
        Args:
            df: Pandas dataframe
            
        Returns:
            String with data description
        """
        if df is None:
            return "No data available"
        
        info = DataLoader.get_data_info(df)
        
        description = f"Dataset with {info['num_rows']} rows and {info['num_columns']} columns.\n\n"
        
        # Column types summary
        description += "Column Types:\n"
        numeric_count = len(info.get('numeric_columns', []))
        categorical_count = len(info.get('categorical_columns', []))
        datetime_count = len(info.get('datetime_columns', []))
        other_count = info['num_columns'] - numeric_count - categorical_count - datetime_count
        
        description += f"- Numeric columns: {numeric_count}\n"
        description += f"- Categorical columns: {categorical_count}\n"
        description += f"- Datetime columns: {datetime_count}\n"
        if other_count > 0:
            description += f"- Other columns: {other_count}\n"
        
        # Missing values
        missing_vals = sum(info['missing_values'].values())
        if missing_vals > 0:
            description += f"\nMissing Values: {missing_vals} total missing values "
            description += f"({missing_vals / (info['num_rows'] * info['num_columns']) * 100:.2f}% of all cells)\n"
            
            # Columns with most missing values
            missing_cols = {k: v for k, v in info['missing_values'].items() if v > 0}
            if missing_cols:
                sorted_missing = sorted(missing_cols.items(), key=lambda x: x[1], reverse=True)
                description += "Top columns with missing values:\n"
                for col, count in sorted_missing[:3]:  # Top 3 columns with missing values
                    description += f"- {col}: {count} missing values ({count / info['num_rows'] * 100:.2f}%)\n"
        
        return description
    @staticmethod
    def get_data_samples(df: pd.DataFrame, num_samples: int = 5) -> pd.DataFrame:
        """
        Get random samples from the dataframe
        """
        if df is None:
            return None
        return df.sample(n=num_samples)
    @staticmethod
    def basic_preprocessing(df: pd.DataFrame) -> pd.DataFrame:
        """
        Perform basic preprocessing on the dataframe
        
        Args:
            df: Pandas dataframe
            
        Returns:
            Preprocessed dataframe
        """
        if df is None:
            return None
        
        # Create a copy to avoid modifying the original
        df_processed = df.copy()
        
        # Handle datetime columns
        for col in df_processed.columns:
            try:
                if df_processed[col].dtype == 'object':
                    # Try to convert to datetime
                    df_processed[col] = pd.to_datetime(df_processed[col], errors='ignore')
            except:
                pass
        
        return df_processed
    
    @staticmethod
    def save_data(df: pd.DataFrame, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Save dataframe to a file
        
        Args:
            df: Pandas dataframe
            file_path: Path to save the file
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            if df is None:
                return False, "No data to save"
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            if file_path.endswith(".csv"):
                df.to_csv(file_path, index=False)
            elif file_path.endswith(".xlsx") or file_path.endswith(".xls"):
                df.to_excel(file_path, index=False)
            elif file_path.endswith(".json"):
                df.to_json(file_path, orient="records")
            elif file_path.endswith(".parquet"):
                df.to_parquet(file_path, index=False)
            else:
                return False, f"Unsupported file format: {file_path}"
            
            return True, None
        except Exception as e:
            return False, f"Error saving data: {str(e)}"