"""
JSD-PAM clustering using Jensen-Shannon Divergence and PAM clustering for microbiome data analysis.

This module contains the JSDPAMTrainer class for:
- Calculating Jensen-Shannon Divergence between samples
- Applying PAM (Partitioning Around Medoids) clustering for different numbers of clusters (K)
- Processing and saving clustering results in the same format as LDA/NMF trainers
- Integration with existing pipeline visualization tools

The approach:
1. Takes sample-genus relative abundance data
2. Calculates JSD distance matrix between all sample pairs
3. Applies PAM clustering for multiple K values
4. Assigns samples to clusters and calculates cluster-feature relationships
5. Outputs results in MC format compatible with existing pipeline
"""

from typing import List, Dict, Tuple, Any, Optional
import os
import pandas as pd
import numpy as np
import warnings
from scipy.spatial.distance import jensenshannon
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import pickle
import json

# For PAM clustering - using sklearn_extra.cluster.KMedoids
from sklearn_extra.cluster import KMedoids
PAM_AVAILABLE = True

warnings.filterwarnings("ignore", category=FutureWarning)


class JSDPAMTrainer:
    """
    A class for clustering samples using JSD distance and PAM clustering.

    This class handles:
    - Calculating Jensen-Shannon Divergence distance matrix between samples
    - Applying PAM clustering for different numbers of clusters
    - Processing and saving clustering results in LDA-compatible format
    - Generating sample-cluster and cluster-feature probability matrices
    """

    def __init__(self, base_directory: str, use_relative_abundance: bool = True, **clustering_params):
        """
        Initialize the JSD-PAM Trainer.

        Args:
            base_directory (str): Base directory for storing all results
            use_relative_abundance (bool): Whether to convert to relative abundance
            **clustering_params: Additional parameters for clustering algorithm
                                Default: max_iter=300, random_state=42, init='k-medoids++'
        """
        self.base_directory = base_directory
        self.use_relative_abundance = use_relative_abundance
        
        # Set default clustering parameters
        self.clustering_params = {
            'max_iter': 300,
            'random_state': 42,
            'init': 'k-medoids++'
        }
        # Update with user-provided parameters
        self.clustering_params.update(clustering_params)

        # Set up directory structure (same as LDA)
        self.paths = self._setup_directories()

        # Initialize result storage
        self.all_results = {}  # Store all model results for different K values
        self.all_metrics = pd.DataFrame(columns=['K'])  # For compatibility with existing pipeline
        
        # Data containers (to be set later)
        self.abundance_matrix = None
        self.jsd_matrix = None
        self.sample_names = None
        self.feature_names = None
        
        print(f"JSDPAMTrainer initialized")
        print(f"  Using: PAM (KMedoids)")
        print(f"  Clustering parameters: {self.clustering_params}")

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

        print(f"Setting up JSD-PAM directory structure in: {self.base_directory}")
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

        This method loads the genus table with random IDs and prepares it for clustering.
        """
        # Load the sample table with random IDs
        sampletable_path = os.path.join(self.paths['intermediate_directory'], 'annotaed_randomid.csv')
        if not os.path.exists(sampletable_path):
            raise FileNotFoundError(f"Sample table not found: {sampletable_path}. Run TaxonomyProcessor first.")

        sampletable = pd.read_csv(sampletable_path, index_col=0)
        print(f"  ✓ Loaded sample table: {sampletable.shape}")

        # Store abundance matrix (samples × features)
        self.abundance_matrix = sampletable.values.astype(float)
        self.sample_names = sampletable.index.tolist()
        self.feature_names = sampletable.columns.tolist()
        
        # Convert to relative abundance if requested
        if self.use_relative_abundance:
            row_sums = self.abundance_matrix.sum(axis=1, keepdims=True)
            # Avoid division by zero
            row_sums[row_sums == 0] = 1
            self.abundance_matrix = self.abundance_matrix / row_sums
            print(f"  ✓ Converted to relative abundance")
        
        print(f"  ✓ Prepared abundance matrix: {self.abundance_matrix.shape} (samples × features)")
        print(f"  ✓ Number of samples: {len(self.sample_names)}")
        print(f"  ✓ Number of features: {len(self.feature_names)}")
        
        print("Training data loaded successfully.")

    def _calculate_jsd_matrix(self):
        """Calculate Jensen-Shannon Divergence matrix between all sample pairs."""
        if self.abundance_matrix is None:
            raise ValueError("Training data not loaded. Call load_training_data() first.")
        
        print("Calculating Jensen-Shannon Divergence matrix...")
        n_samples = self.abundance_matrix.shape[0]
        self.jsd_matrix = np.zeros((n_samples, n_samples))
        
        for i in range(n_samples):
            for j in range(i+1, n_samples):
                # Calculate JSD between samples i and j
                jsd_dist = jensenshannon(self.abundance_matrix[i], self.abundance_matrix[j])
                self.jsd_matrix[i, j] = jsd_dist
                self.jsd_matrix[j, i] = jsd_dist  # Matrix is symmetric
        
        print(f"  ✓ JSD matrix calculated: {self.jsd_matrix.shape}")

    def train_single_model(self, n_clusters: int) -> Dict[str, Any]:
        """
        Train a single clustering model for a specific number of clusters.

        Args:
            n_clusters: Number of clusters to create

        Returns:
            Dictionary containing clustering results
        """
        print(f"\nTraining clustering model with {n_clusters} clusters...")
        
        # Calculate JSD matrix if not done yet
        if self.jsd_matrix is None:
            self._calculate_jsd_matrix()
        
        # Apply PAM clustering
        clusterer = KMedoids(
            n_clusters=n_clusters,
            metric='precomputed',
            **self.clustering_params
        )
        cluster_labels = clusterer.fit_predict(self.jsd_matrix)
        medoids = clusterer.medoid_indices_
        
        print(f"  ✓ Clustering completed")
        print(f"  ✓ Cluster labels: {np.unique(cluster_labels)}")
        
        # Calculate silhouette score
        if len(np.unique(cluster_labels)) > 1:
            silhouette = silhouette_score(self.jsd_matrix, cluster_labels, metric='precomputed')
        else:
            silhouette = 0.0
        
        print(f"  ✓ Silhouette score: {silhouette:.4f}")
        
        # Create sample-cluster probability matrix
        sample_cluster_probs = self._create_sample_cluster_matrix(cluster_labels, n_clusters)
        
        # Create cluster-feature probability matrix
        cluster_feature_probs = self._create_cluster_feature_matrix(cluster_labels, n_clusters)
        
        # Save results
        self._save_model_results(n_clusters, sample_cluster_probs, cluster_feature_probs, clusterer)
        
        return {
            'n_clusters': n_clusters,
            'model': clusterer,
            'cluster_labels': cluster_labels,
            'medoids': medoids,
            'sample_cluster_probs': sample_cluster_probs,
            'cluster_feature_probs': cluster_feature_probs,
            'silhouette_score': silhouette,
            'jsd_matrix': self.jsd_matrix
        }

    def _create_sample_cluster_matrix(self, cluster_labels: np.ndarray, n_clusters: int) -> pd.DataFrame:
        """Create sample-cluster probability matrix (like sample-topic in LDA)."""
        # Create binary assignment matrix (1 if sample belongs to cluster, 0 otherwise)
        cluster_matrix = np.zeros((n_clusters, len(self.sample_names)))
        
        for sample_idx, cluster_label in enumerate(cluster_labels):
            cluster_matrix[cluster_label, sample_idx] = 1.0
        
        # Create DataFrame with proper labels
        cluster_labels_names = [f"MC{i}" for i in range(n_clusters)]
        
        sample_cluster_probs = pd.DataFrame(
            cluster_matrix,
            index=cluster_labels_names,
            columns=self.sample_names
        )
        
        return sample_cluster_probs

    def _create_cluster_feature_matrix(self, cluster_labels: np.ndarray, n_clusters: int) -> pd.DataFrame:
        """Create cluster-feature probability matrix (like topic-word in LDA)."""
        # Calculate mean abundance of each feature in each cluster
        cluster_feature_matrix = np.zeros((n_clusters, len(self.feature_names)))
        
        for cluster_id in range(n_clusters):
            # Get samples in this cluster
            cluster_mask = cluster_labels == cluster_id
            if np.any(cluster_mask):
                # Calculate mean abundance across samples in this cluster
                cluster_mean = np.mean(self.abundance_matrix[cluster_mask, :], axis=0)
                cluster_feature_matrix[cluster_id, :] = cluster_mean
        
        # Normalize to probabilities (each row sums to 1)
        row_sums = cluster_feature_matrix.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1  # Avoid division by zero
        cluster_feature_matrix = cluster_feature_matrix / row_sums
        
        # Create DataFrame with proper labels
        cluster_labels_names = [f"MC{i}" for i in range(n_clusters)]
        
        cluster_feature_probs = pd.DataFrame(
            cluster_feature_matrix,
            index=cluster_labels_names,
            columns=self.feature_names
        )
        
        return cluster_feature_probs

    def _save_model_results(self, n_clusters: int, sample_probs: pd.DataFrame, 
                          feature_probs: pd.DataFrame, model):
        """Save clustering results to files in LDA-compatible format."""
        
        # Save sample-cluster probabilities (same format as LDA)
        sample_probs_path = os.path.join(
            self.paths['MC_sample_directory'], 
            f'MC_Sample_probabilities{n_clusters}.csv'
        )
        sample_probs.to_csv(sample_probs_path)
        
        # Save cluster-feature probabilities (same format as LDA)
        feature_probs_path = os.path.join(
            self.paths['MC_feature_directory'], 
            f'MC_Feature_Probabilities_{n_clusters}.csv'
        )
        feature_probs.to_csv(feature_probs_path)
        
        # Save model object
        model_path = os.path.join(self.paths['loop_directory'], f'jsd_pam_model_{n_clusters}.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        print(f"  ✓ Results saved for K={n_clusters}")

    def train_models(self, k_range: List[int]) -> Dict[int, Dict[str, Any]]:
        """
        Train clustering models for multiple numbers of clusters.

        Args:
            k_range: List of K values (number of clusters) to train

        Returns:
            Dictionary containing results for all K values
        """
        if self.abundance_matrix is None:
            raise ValueError("Training data not loaded. Call load_training_data() first.")
        
        print(f"\n{'='*60}")
        print(f"Training JSD-PAM clustering models for K values: {k_range}")
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
        print(f"JSD-PAM clustering completed for {len(all_results)} models")
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
                'Silhouette_Score': results['silhouette_score'],
                'N_Clusters': results['n_clusters'],
                'N_Samples': len(self.sample_names),
                'N_Features': len(self.feature_names)
            })
        
        return pd.DataFrame(summary_data).sort_values('K')

    def save_summary(self, k_range: List[int]):
        """
        Save a summary of all models.

        Args:
            k_range: Range of K values trained
        """
        summary_df = self.get_model_summary()
        
        if not summary_df.empty:
            range_str = f"{min(k_range)}-{max(k_range)}"
            summary_path = os.path.join(
                self.paths['lda_directory'], 
                f'jsd_pam_summary_{range_str}.csv'
            )
            summary_df.to_csv(summary_path, index=False)
            print(f"✓ Model summary saved to: {summary_path}")

    def get_top_features_per_cluster(self, k: int, top_n: int = 10) -> Dict[str, List[Tuple[str, float]]]:
        """
        Get top features for each cluster in a specific model.

        Args:
            k: Number of clusters 
            top_n: Number of top features to return per cluster

        Returns:
            Dictionary mapping cluster names to top features
        """
        if k not in self.all_results:
            raise ValueError(f"Model with K={k} not found. Available K values: {list(self.all_results.keys())}")
        
        feature_probs = self.all_results[k]['cluster_feature_probs']
        top_features = {}
        
        for cluster_idx in range(k):
            cluster_name = f"MC{cluster_idx}"
            # Get feature weights for this cluster
            feature_weights = feature_probs.iloc[cluster_idx, :]
            # Get top features
            top_indices = feature_weights.nlargest(top_n)
            top_features[cluster_name] = [
                (feature_name, weight) 
                for feature_name, weight in top_indices.items()
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
    def from_taxonomy_processor(cls, taxonomy_processor, **clustering_params):
        """
        Create JSDPAMTrainer from a TaxonomyProcessor instance.

        Args:
            taxonomy_processor: TaxonomyProcessor instance that has completed processing
            **clustering_params: Additional parameters for clustering

        Returns:
            JSDPAMTrainer instance
        """
        if taxonomy_processor.sampletable_randomID is None:
            raise ValueError("TaxonomyProcessor must have completed processing before creating JSDPAMTrainer")

        trainer = cls(
            base_directory=taxonomy_processor.base_directory,
            **clustering_params
        )
        
        # Load the data directly from the processor
        trainer.abundance_matrix = taxonomy_processor.sampletable_randomID.values.astype(float)
        trainer.sample_names = taxonomy_processor.sampletable_randomID.index.tolist()
        trainer.feature_names = taxonomy_processor.sampletable_randomID.columns.tolist()
        
        # Convert to relative abundance if requested
        if trainer.use_relative_abundance:
            row_sums = trainer.abundance_matrix.sum(axis=1, keepdims=True)
            row_sums[row_sums == 0] = 1
            trainer.abundance_matrix = trainer.abundance_matrix / row_sums
            print("✓ Converted to relative abundance")
        
        print(f"JSDPAMTrainer created from TaxonomyProcessor")
        print(f"  Abundance matrix shape: {trainer.abundance_matrix.shape}")
        
        return trainer
