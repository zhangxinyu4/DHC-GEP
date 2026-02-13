# coding=utf-8
"""
Data loading and preprocessing utilities for DHC-GEP experiments.

This module provides functions for loading and preprocessing data
from various sources, with support for subsampling and normalization.
"""

import numpy as np
import scipy.io as scio


def load_mat_data(filepath, variable_names, subsample=None, seed=None):
    """
    Load data from MATLAB .mat file.
    
    Args:
        filepath: Path to .mat file
        variable_names: List of variable names to load from the file
        subsample: Number of samples to randomly select (optional)
        seed: Random seed for reproducibility (optional)
        
    Returns:
        dict: Dictionary mapping variable names to loaded arrays
        
    Example:
        data = load_mat_data('../data/Diffusion_flow.mat', 
                           ['rho', 'rho_y', 'rho_yy', 'rho_3y', 'rho_t'],
                           subsample=720, seed=0)
    """
    # Load the entire .mat file
    mat_data = scio.loadmat(filepath)
    
    # Extract requested variables
    data = {}
    for var_name in variable_names:
        if var_name in mat_data:
            data[var_name] = mat_data[var_name]
        else:
            raise KeyError(f"Variable '{var_name}' not found in {filepath}")
    
    # Apply subsampling if requested
    if subsample is not None:
        if seed is not None:
            np.random.seed(seed)
        
        # Get the length from the first variable
        data_length = len(data[variable_names[0]])
        
        # Generate random indices
        indices = np.random.randint(data_length, size=subsample)
        
        # Apply indices to all variables
        for var_name in variable_names:
            data[var_name] = data[var_name][indices, :]
    
    return data


def prepare_training_data(data_dict, input_vars, target_var):
    """
    Prepare training data from a data dictionary.
    
    Args:
        data_dict: Dictionary of loaded data arrays
        input_vars: List of input variable names
        target_var: Name of target variable
        
    Returns:
        tuple: (X_data, y_data) where X_data is a tuple of input arrays
               and y_data is the target array
               
    Example:
        X, y = prepare_training_data(data, 
                                     ['rho', 'rho_y', 'rho_yy', 'rho_3y'],
                                     'rho_t')
    """
    X_data = tuple(data_dict[var] for var in input_vars)
    y_data = data_dict[target_var]
    return X_data, y_data


def normalize_data(data, method='standard'):
    """
    Normalize data using specified method.
    
    Args:
        data: NumPy array to normalize
        method: Normalization method ('standard', 'minmax', 'none')
                - 'standard': (x - mean) / std
                - 'minmax': (x - min) / (max - min)
                - 'none': no normalization
                
    Returns:
        tuple: (normalized_data, normalization_params)
               normalization_params is a dict with 'method' and relevant parameters
    """
    if method == 'standard':
        mean = np.mean(data)
        std = np.std(data)
        normalized = (data - mean) / std if std != 0 else data
        params = {'method': 'standard', 'mean': mean, 'std': std}
        return normalized, params
        
    elif method == 'minmax':
        min_val = np.min(data)
        max_val = np.max(data)
        normalized = (data - min_val) / (max_val - min_val) if max_val != min_val else data
        params = {'method': 'minmax', 'min': min_val, 'max': max_val}
        return normalized, params
        
    else:  # 'none'
        return data, {'method': 'none'}


def denormalize_data(normalized_data, normalization_params):
    """
    Reverse normalization on data.
    
    Args:
        normalized_data: Normalized NumPy array
        normalization_params: Dictionary with normalization parameters
        
    Returns:
        np.ndarray: Denormalized data
    """
    method = normalization_params['method']
    
    if method == 'standard':
        mean = normalization_params['mean']
        std = normalization_params['std']
        return normalized_data * std + mean
        
    elif method == 'minmax':
        min_val = normalization_params['min']
        max_val = normalization_params['max']
        return normalized_data * (max_val - min_val) + min_val
        
    else:  # 'none'
        return normalized_data


class DataLoader:
    """
    Convenience class for loading and managing experimental data.
    """
    
    def __init__(self, filepath, variable_names, subsample=None, seed=None):
        """
        Initialize data loader.
        
        Args:
            filepath: Path to data file
            variable_names: List of variable names to load
            subsample: Number of samples to randomly select (optional)
            seed: Random seed for reproducibility (optional)
        """
        self.filepath = filepath
        self.variable_names = variable_names
        self.subsample = subsample
        self.seed = seed
        self.data = None
        self.normalization_params = {}
        
    def load(self):
        """Load data from file."""
        self.data = load_mat_data(
            self.filepath, 
            self.variable_names,
            self.subsample,
            self.seed
        )
        return self.data
    
    def normalize(self, var_names, method='standard'):
        """
        Normalize specified variables.
        
        Args:
            var_names: List of variable names to normalize
            method: Normalization method
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load() first.")
        
        for var_name in var_names:
            if var_name in self.data:
                self.data[var_name], self.normalization_params[var_name] = \
                    normalize_data(self.data[var_name], method)
    
    def get_training_data(self, input_vars, target_var):
        """
        Get training data in format suitable for GEP.
        
        Args:
            input_vars: List of input variable names
            target_var: Name of target variable
            
        Returns:
            tuple: (X_data, y_data)
        """
        if self.data is None:
            raise ValueError("Data not loaded. Call load() first.")
        
        return prepare_training_data(self.data, input_vars, target_var)


__all__ = [
    'load_mat_data',
    'prepare_training_data',
    'normalize_data',
    'denormalize_data',
    'DataLoader'
]
