"""
NMF model training using scikit-learn's NMF for microbiome data analysis.

This module contains the NMFTrainer class for:
- Training NMF models across multiple numbers of components (K)
- Processing and saving model outputs in the same format as LDATrainer
- Generating sample-component and component-feature probability matrices
- Integration with existing pipeline visualization tools

NMF (Non-negative Matrix Factorization) decomposes the sample-feature matrix into:
- W matrix (samples × components): How much each sample belongs to each component
- H matrix (components × features): How much each feature contributes to each component

This is conceptually similar to LDA but uses matrix factorization instead of probabilistic modeling.
"""

from typing import List, Dict, Tuple, Any, Optional
import os
import pandas as pd
import numpy as np
import warnings
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize
import pickle
import json

warnings.filterwarnings("ignore", category=FutureWarning)


class NMFTrainer:
    """
    A class for training NMF models across multiple component numbers and managing results.

    This class handles:
    - Setting up directory structure for NMF analysis (same as LDA)
    - Training sklearn NMF models for different numbers of components
    - Processing and saving model outputs in LDA-compatible format
    - Generating probability matrices for visualization
    """

    def __init__(self, base_directory: str, **nmf_params):
        """
        Initialize the NMF Trainer.

        Args:
            base_directory (str): Base directory for storing all results
            **nmf_params: Additional parameters for sklearn NMF model
                         Default: init='nndsvd', solver='cd', beta_loss='frobenius',
                         max_iter=1000, random_state=42, alpha_W=0.0, alpha_H=0.0
        """
        self.base_directory = base_directory
        
        # Set default NMF parameters
        self.nmf_params = {
            'init': 'nndsvd',  # Non-Negative Double Singular Value Decomposition
            'solver': 'cd',    # Coordinate Descent solver
            'beta_loss': 'frobenius',  # Frobenius norm
            'max_iter': 1000,
            'random_state': 42,
            'alpha_W': 0.0,    # Regularization for W matrix
            'alpha_H': 0.0,    # Regularization for H matrix
            'tol': 1e-4
        }
        # Update with user-provided parameters
        self.nmf_params.update(nmf_params)

        # Set up directory structure (same as LDA)
        self.paths = self._setup_directories()

        # Initialize result storage
        self.all_results = {}  # Store all model results for different K values
        self.all_metrics = pd.DataFrame(columns=['K'])  # For compatibility with existing pipeline
        
        # Data containers (to be set later)
        self.count_matrix = None
        self.feature_names = None
        self.sample_names = None
        
        print(f"NMFTrainer initialized")
        print(f"  NMF parameters: {self.nmf_params}")

    def _setup_directories(self) -> Dict[str, str]:
        """Set up directory structure and return path dictionary (same as LDA)."""
        intermediate_directory = os.path.join(self.base_directory, 'intermediate')
        loop_directory = os.path.join(self.base_directory, 'lda_loop')  # Keep same name for compatibility
        lda_directory = os.path.join(self.base_directory, 'lda_results')  # Keep same name for compatibility
        MC_sample_directory = os.path.join(lda_directory, 'MC_Sample')
        MC_feature_directory = os.path.join(lda_directory, 'MC_Feature')

        # Create all directories
        directories = [
            intermediate_directory, loop_directory, lda_directory,
            MC_sample_directory, MC_feature_directory
        ]

        print(f"Setting up NMF directory structure in: {self.base_directory}")
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"  ✓ Created/verified: {directory}")

        return {
            'intermediate_directory': intermediate_directory,
            'loop_directory': loop_directory,
            'lda_directory': lda_directory,
            'MC_sample_directory': MC_sample_directory,
            'MC_feature_directory': MC_feature_directory
        }

    def load_training_data(self):
        """
        Load training data from files created by TaxonomyProcessor.

        This method loads the ASV table with random IDs and converts it to
        the count matrix format needed for NMF.
        """
        # Load the sample table with random IDs
        sampletable_path = os.path.join(self.paths['intermediate_directory'], 'annotaed_randomid.csv')
        if not os.path.exists(sampletable_path):
            raise FileNotFoundError(f"Sample table not found: {sampletable_path}. Run TaxonomyProcessor first.")

        sampletable = pd.read_csv(sampletable_path, index_col=0)
        print(f"  ✓ Loaded sample table: {sampletable.shape}")

        # For NMF, we need samples as rows and features as columns
        # The sampletable from TaxonomyProcessor has samples as rows and ASVs as columns (perfect!)
        self.count_matrix = sampletable.values.astype(float)
        self.sample_names = sampletable.index.tolist()
        self.feature_names = sampletable.columns.tolist()
        
        print(f"  ✓ Prepared count matrix: {self.count_matrix.shape} (samples × features)")
        print(f"  ✓ Number of samples: {len(self.sample_names)}")
        print(f"  ✓ Number of features: {len(self.feature_names)}")
        
        # Check for non-negative values
        if np.any(self.count_matrix < 0):
            print("  ! Warning: Negative values detected in count matrix. Setting to 0.")
            self.count_matrix = np.maximum(self.count_matrix, 0)
        
        print("Training data loaded successfully.")

    def train_single_model(self, n_components: int) -> Dict[str, Any]:
        """
        Train a single NMF model for a specific number of components.

        Args:
            n_components: Number of components (topics) to extract

        Returns:
            Dictionary containing model results
        """
        print(f"\nTraining NMF model with {n_components} components...")
        
        # Create and fit NMF model
        nmf_model = NMF(n_components=n_components, **self.nmf_params)
        
        # Fit the model and transform the data
        W = nmf_model.fit_transform(self.count_matrix)  # Sample-component matrix
        H = nmf_model.components_  # Component-feature matrix
        
        print(f"  ✓ Model training completed")
        print(f"  ✓ W matrix shape: {W.shape} (samples × components)")
        print(f"  ✓ H matrix shape: {H.shape} (components × features)")
        print(f"  ✓ Reconstruction error: {nmf_model.reconstruction_err_:.4f}")
        
        # Convert to probability matrices (normalize)
        # W_prob: each row sums to 1 (sample probabilities over components)
        W_prob = normalize(W, axis=1, norm='l1')
        
        # H_prob: each row sums to 1 (component probabilities over features) 
        H_prob = normalize(H, axis=1, norm='l1')
        
        # Create DataFrames with proper labels
        component_labels = [f"MC{i}" for i in range(n_components)]
        
        # Sample-Component probabilities (equivalent to LDA's topic distributions)
        sample_component_probs = pd.DataFrame(
            W_prob.T,  # Transpose to match LDA format (components × samples)
            index=component_labels,
            columns=self.sample_names
        )
        
        # Component-Feature probabilities (equivalent to LDA's word topics)
        component_feature_probs = pd.DataFrame(
            H_prob,
            index=component_labels,
            columns=self.feature_names
        )
        
        # Save results
        self._save_model_results(n_components, sample_component_probs, component_feature_probs, nmf_model)
        
        return {
            'n_components': n_components,
            'model': nmf_model,
            'W_matrix': W,
            'H_matrix': H,
            'W_prob': W_prob,
            'H_prob': H_prob,
            'sample_component_probs': sample_component_probs,
            'component_feature_probs': component_feature_probs,
            'reconstruction_error': nmf_model.reconstruction_err_
        }

    def _save_model_results(self, n_components: int, sample_probs: pd.DataFrame, 
                          feature_probs: pd.DataFrame, model: NMF):
        """Save model results to files in LDA-compatible format."""
        
        # Save sample-component probabilities (same format as LDA)
        sample_probs_path = os.path.join(
            self.paths['MC_sample_directory'], 
            f'MC_Sample_probabilities{n_components}.csv'
        )
        sample_probs.to_csv(sample_probs_path)
        
        # Save component-feature probabilities (same format as LDA)
        feature_probs_path = os.path.join(
            self.paths['MC_feature_directory'], 
            f'MC_Feature_Probabilities_{n_components}.csv'
        )
        feature_probs.to_csv(feature_probs_path)
        
        # Save model object
        model_path = os.path.join(self.paths['loop_directory'], f'nmf_model_{n_components}.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        print(f"  ✓ Results saved for K={n_components}")

    def train_models(self, k_range: List[int]) -> Dict[int, Dict[str, Any]]:
        """
        Train NMF models for multiple numbers of components.

        Args:
            k_range: List of K values (number of components) to train

        Returns:
            Dictionary containing results for all K values
        """
        if self.count_matrix is None:
            raise ValueError("Training data not loaded. Call load_training_data() first.")
        
        print(f"\n{'='*60}")
        print(f"Training NMF models for K values: {k_range}")
        print(f"{'='*60}")
        
        all_results = {}
        
        for k in k_range:
            try:
                results = self.train_single_model(k)
                all_results[k] = results
                print(f"  ✓ Completed K={k}")
            except Exception as e:
                print(f"  ✗ Error training K={k}: {str(e)}")
                continue
        
        self.all_results = all_results
        
        # Update all_metrics for compatibility with existing pipeline
        self._update_all_metrics()
        
        print(f"\n{'='*60}")
        print(f"NMF training completed for {len(all_results)} models")
        print(f"Successful K values: {sorted(all_results.keys())}")
        print(f"{'='*60}")
        
        return all_results

    def get_model_summary(self) -> pd.DataFrame:
        """
        Get a summary of all trained models.

        Returns:
            DataFrame with model statistics
        """
        if not self.all_results:
            return pd.DataFrame()
        
        summary_data = []
        for k, results in self.all_results.items():
            summary_data.append({
                'K': k,
                'Reconstruction_Error': results['reconstruction_error'],
                'N_Components': results['n_components'],
                'N_Samples': len(self.sample_names),
                'N_Features': len(self.feature_names)
            })
        
        return pd.DataFrame(summary_data).sort_values('K')

    def save_summary(self, k_range: List[int]):
        """
        Save a summary of all models (minimal version, no complex metrics).

        Args:
            k_range: Range of K values trained
        """
        summary_df = self.get_model_summary()
        
        if not summary_df.empty:
            range_str = f"{min(k_range)}-{max(k_range)}"
            summary_path = os.path.join(
                self.paths['lda_directory'], 
                f'nmf_summary_{range_str}.csv'
            )
            summary_df.to_csv(summary_path, index=False)
            print(f"✓ Model summary saved to: {summary_path}")
        
    def get_top_features_per_component(self, k: int, top_n: int = 10) -> Dict[str, List[Tuple[str, float]]]:
        """
        Get top features for each component in a specific model.

        Args:
            k: Number of components 
            top_n: Number of top features to return per component

        Returns:
            Dictionary mapping component names to top features
        """
        if k not in self.all_results:
            raise ValueError(f"Model with K={k} not found. Available K values: {list(self.all_results.keys())}")
        
        H_prob = self.all_results[k]['H_prob']
        top_features = {}
        
        for comp_idx in range(k):
            comp_name = f"MC{comp_idx}"
            # Get feature weights for this component
            feature_weights = H_prob[comp_idx, :]
            # Get top features
            top_indices = np.argsort(feature_weights)[::-1][:top_n]
            top_features[comp_name] = [
                (self.feature_names[idx], feature_weights[idx]) 
                for idx in top_indices
            ]
        
        return top_features
    
    def _update_all_metrics(self):
        """Update all_metrics DataFrame for compatibility with existing pipeline."""
        if not self.all_results:
            return
        
        metrics_data = []
        for k in sorted(self.all_results.keys()):
            metrics_data.append({'K': k})
        
        self.all_metrics = pd.DataFrame(metrics_data)
        print(f"✓ Updated all_metrics with {len(metrics_data)} models")

    @classmethod
    def from_taxonomy_processor(cls, taxonomy_processor, **nmf_params):
        """
        Create NMFTrainer from a TaxonomyProcessor instance.

        Args:
            taxonomy_processor: TaxonomyProcessor instance that has completed processing
            **nmf_params: Additional parameters for NMF model

        Returns:
            NMFTrainer instance
        """
        if taxonomy_processor.sampletable_randomID is None:
            raise ValueError("TaxonomyProcessor must have completed processing before creating NMFTrainer")

        trainer = cls(
            base_directory=taxonomy_processor.base_directory,
            **nmf_params
        )
        
        # Load the data directly from the processor
        trainer.count_matrix = taxonomy_processor.sampletable_randomID.values.astype(float)
        trainer.sample_names = taxonomy_processor.sampletable_randomID.index.tolist()
        trainer.feature_names = taxonomy_processor.sampletable_randomID.columns.tolist()
        
        # Ensure non-negative values
        if np.any(trainer.count_matrix < 0):
            print("Warning: Negative values detected in count matrix. Setting to 0.")
            trainer.count_matrix = np.maximum(trainer.count_matrix, 0)
        
        print(f"NMFTrainer created from TaxonomyProcessor")
        print(f"  Count matrix shape: {trainer.count_matrix.shape}")
        
        return trainer
