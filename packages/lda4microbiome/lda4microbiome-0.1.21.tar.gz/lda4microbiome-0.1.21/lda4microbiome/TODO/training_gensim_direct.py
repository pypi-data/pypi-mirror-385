"""
Direct Gensim LDA implementation for microbiome data.

This module provides a Gensim-based LDA trainer that works directly with relative abundance data
using Gensim's variational Bayes implementation, which can handle continuous values.
"""

from typing import List, Dict, Tuple, Any, Optional
import os
import pandas as pd
import numpy as np
import pickle
import json
import warnings
from gensim.models import LdaModel
from gensim.corpora import Dictionary
from gensim.matutils import Sparse2Corpus
from scipy.sparse import csr_matrix

# Import metrics from your existing pipeline
from ..metrics import compute_gensim_perplexity, compute_gensim_coherence


class DirectGensimLDATrainer:
    """
    A Gensim LDA trainer that works directly with relative abundance data.
    
    This class uses the abundance matrix directly as input to Gensim's LDA,
    leveraging its variational Bayes implementation that can handle continuous values.
    """
    
    def __init__(self, base_directory: str, **gensim_params):
        """
        Initialize the Direct Gensim LDA Trainer.
        
        Args:
            base_directory (str): Base directory for storing all results
            **gensim_params: Additional parameters for Gensim LDA model
        """
        self.base_directory = base_directory
        
        # Set default Gensim parameters
        self.gensim_params = {
            'passes': 20,
            'iterations': 400,
            'alpha': 'auto',
            'eta': 'auto',
            'random_state': 42,
            'chunksize': 2000,
            'eval_every': None
        }
        # Update with user-provided parameters
        self.gensim_params.update(gensim_params)
        
        # Set up directory structure
        self.paths = self._setup_directories()
        
        # Initialize data containers
        self.abundance_matrix = None
        self.taxa_metadata = None
        self.gensim_dictionary = None
        self.gensim_corpus = None
        self.processed_texts = None  # For coherence calculation
        
        # Results storage
        self.trained_models = {}
        self.all_metrics = pd.DataFrame()
        
        print("DirectGensimLDATrainer initialized")
        print(f"  Gensim parameters: {self.gensim_params}")
    
    def _setup_directories(self) -> Dict[str, str]:
        """Set up directory structure and return path dictionary."""
        intermediate_directory = os.path.join(self.base_directory, 'intermediate')
        loop_directory = os.path.join(self.base_directory, 'lda_loop')
        lda_directory = os.path.join(self.base_directory, 'lda_results')
        MC_sample_directory = os.path.join(lda_directory, 'MC_Sample')
        MC_feature_directory = os.path.join(lda_directory, 'MC_Feature')
        diagnostics_directory = os.path.join(lda_directory, 'Diagnostics')
        
        # Create all directories
        directories = [
            intermediate_directory, loop_directory, lda_directory,
            MC_sample_directory, MC_feature_directory, diagnostics_directory
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        return {
            'intermediate_directory': intermediate_directory,
            'loop_directory': loop_directory,
            'lda_directory': lda_directory,
            'MC_sample_directory': MC_sample_directory,
            'MC_feature_directory': MC_feature_directory,
            'diagnostics_directory': diagnostics_directory
        }
    
    def load_data_from_taxonomy_processor(self, taxonomy_processor_results: Dict[str, Any]):
        """
        Load data directly from TaxonomyProcessor results.
        
        Args:
            taxonomy_processor_results: Results dictionary from TaxonomyProcessor.process_all()
        """
        self.abundance_matrix = taxonomy_processor_results['sampletable_randomID']
        self.taxa_metadata = taxonomy_processor_results['taxa_split']
        
        print(f"✓ Loaded abundance matrix: {self.abundance_matrix.shape}")
        print(f"✓ Loaded taxa metadata: {self.taxa_metadata.shape}")
        
        # Prepare data for Gensim
        self._prepare_gensim_data_from_abundance()
    
    def load_data_from_files(self):
        """
        Load data from intermediate files (alternative to taxonomy processor).
        """
        # Load the annotated abundance matrix
        abundance_path = os.path.join(self.paths['intermediate_directory'], 'annotaed_randomid.csv')
        if not os.path.exists(abundance_path):
            raise FileNotFoundError(f"Abundance matrix not found: {abundance_path}")
        
        self.abundance_matrix = pd.read_csv(abundance_path, index_col=0)
        
        # Load taxa metadata if available
        taxa_path = os.path.join(self.paths['intermediate_directory'], 'intermediate_taxa.csv')
        if os.path.exists(taxa_path):
            self.taxa_metadata = pd.read_csv(taxa_path, index_col=0)
        
        print(f"✓ Loaded abundance matrix from file: {self.abundance_matrix.shape}")
        
        # Prepare data for Gensim
        self._prepare_gensim_data_from_abundance()
    
    def _prepare_gensim_data_from_abundance(self):
        """
        Convert abundance matrix to proper Gensim format.
        
        Input: abundance_matrix with samples as rows, features (taxa) as columns
               Values should be integer counts (read counts, OTU counts, etc.)
        
        Output: gensim_corpus - List of bag-of-words documents
                gensim_dictionary - Gensim Dictionary mapping feature names to IDs
                processed_texts - List of tokenized documents for coherence calculation
        
        Note: This method converts values to integers via int() casting.
              Works best with count data. Proportions < 1 will be rounded to 0.
        """
        print("Preparing abundance data for Gensim LDA (integer count approach)...")
        print(f"Input matrix shape: {self.abundance_matrix.shape} (samples x features)")
        
        # Create proper Gensim Dictionary from taxa names
        taxa_names = list(self.abundance_matrix.columns)
        self.gensim_dictionary = Dictionary([taxa_names])
        
        # Convert abundance matrix to proper bag-of-words format
        # Each sample (row) becomes a document in the corpus
        self.gensim_corpus = []
        
        # Convert to integers directly (works with count data)
        # If values are already counts, they're used as-is
        # If values are proportions, they're rounded to integers (values < 1 become 0)
        
        for sample_idx, (sample_id, abundances) in enumerate(self.abundance_matrix.iterrows()):
            # Create bag-of-words representation for this sample
            doc_bow = []
            for taxa_name, abundance in abundances.items():
                if abundance > 0:  # Only include non-zero abundances
                    word_id = self.gensim_dictionary.token2id[taxa_name]
                    # Convert to integer count
                    count = int(abundance)
                    if count > 0:  # Only add if non-zero after conversion
                        doc_bow.append((word_id, count))
            self.gensim_corpus.append(doc_bow)
        
        print(f"✓ Created dictionary with {len(self.gensim_dictionary)} unique terms")
        print(f"✓ Created corpus with {len(self.gensim_corpus)} documents")
        print(f"✓ Integer count approach: no scaling applied")
        
        # Create processed_texts for coherence calculation
        # Create document representation by repeating taxa names by their count
        self.processed_texts = []
        for idx, (sample_id, abundances) in enumerate(self.abundance_matrix.iterrows()):
            # Create text representation for coherence
            sample_text = []
            for taxa_name, abundance in abundances.items():
                if abundance > 0:
                    # Repeat taxa name by its count
                    count = int(abundance)
                    if count > 0:
                        sample_text.extend([str(taxa_name)] * count)
            self.processed_texts.append(sample_text)
        
        print(f"✓ Created processed texts for {len(self.processed_texts)} samples")
        print(f"✓ Abundance matrix shape: {self.abundance_matrix.shape} (samples x features)")
        print(f"✓ Sample names: {len(self.abundance_matrix.index)} samples")
        print(f"✓ Feature names: {len(self.abundance_matrix.columns)} features")
    
    def train_model(self, num_topics: int) -> Dict[str, Any]:
        """
        Train a single LDA model.
        
        Args:
            num_topics (int): Number of topics to train
            
        Returns:
            Dict containing model and metrics
        """
        if self.gensim_corpus is None:
            raise ValueError("Data must be prepared first. Call load_data_* method")
        
        print(f"Training Gensim LDA model with {num_topics} topics...")
        
        # Train the model
        lda_model = LdaModel(
            corpus=self.gensim_corpus,
            id2word=self.gensim_dictionary,
            num_topics=num_topics,
            **self.gensim_params
        )
        
        # Generate file paths
        file_paths = self._generate_file_paths(num_topics)
        
        # Save model and dictionary
        with open(file_paths['model'], 'wb') as f:
            pickle.dump(lda_model, f)
        with open(file_paths['dictionary'], 'wb') as f:
            pickle.dump(self.gensim_dictionary, f)
        
        # Calculate metrics
        perplexity = compute_gensim_perplexity(lda_model, self.gensim_corpus)
        coherence = compute_gensim_coherence(
            lda_model, 
            texts=self.processed_texts,
            dictionary=self.gensim_dictionary,
            coherence='c_v',
            topn=20
        )
        
        metrics = {
            'K': num_topics,
            'Perplexity': float(perplexity),
            'Coherence': float(coherence),
            'Implementation': 'gensim_direct'
        }
        
        # Process and save outputs
        self._process_and_save_outputs(lda_model, num_topics, file_paths)
        
        # Store results
        result = {
            'model': lda_model,
            'metrics': metrics,
            'file_paths': file_paths
        }
        
        self.trained_models[num_topics] = result
        
        print(f"✓ Completed training for {num_topics} topics")
        print(f"  Perplexity: {perplexity:.2f}")
        print(f"  Coherence: {coherence:.4f}")
        
        return result
    
    def train_models(self, topic_range: List[int]) -> pd.DataFrame:
        """
        Train LDA models for multiple topic numbers.
        
        Args:
            topic_range: List of topic numbers to train
            
        Returns:
            DataFrame with all metrics
        """
        print(f"Training {len(topic_range)} LDA models...")
        
        all_metrics = []
        
        for num_topics in topic_range:
            try:
                result = self.train_model(num_topics)
                all_metrics.append(result['metrics'])
            except Exception as e:
                print(f"Error training model with {num_topics} topics: {e}")
                continue
        
        # Create metrics DataFrame
        self.all_metrics = pd.DataFrame(all_metrics)
        
        # Ensure the DataFrame is not empty for SankeyDataProcessor compatibility
        if self.all_metrics.empty:
            raise ValueError("No models were successfully trained. Cannot create metrics DataFrame.")
        
        # Save metrics
        metrics_path = os.path.join(self.paths['lda_directory'], 'gensim_direct_metrics.csv')
        self.all_metrics.to_csv(metrics_path, index=False)
        print(f"✓ Saved metrics to {metrics_path}")
        print(f"✓ Training completed for {len(self.all_metrics)} models")
        
        return self.all_metrics
    
    def _generate_file_paths(self, num_topics: int) -> Dict[str, str]:
        """Generate all file paths for a specific number of topics - matching old pipeline exactly."""
        loop_path = self.paths['loop_directory']
        diagnostics_path = self.paths['diagnostics_directory']
        mc_sample_path = self.paths['MC_sample_directory']
        mc_feature_path = self.paths['MC_feature_directory']
        
        # Use exact same file naming as old pipeline
        return {
            'model': os.path.join(loop_path, f'gensim_model_{num_topics}.pkl'),
            'dictionary': os.path.join(loop_path, f'gensim_dictionary_{num_topics}.pkl'),
            'coherence': os.path.join(diagnostics_path, f'coherence_{num_topics}.json'),
            'sample_probs': os.path.join(mc_sample_path, f'MC_Sample_probabilities{num_topics}.csv'),
            'feature_probs': os.path.join(mc_feature_path, f'MC_Feature_Probabilities_{num_topics}.csv')
        }
    
    def _process_and_save_outputs(self, lda_model: LdaModel, num_topics: int, file_paths: Dict[str, str]):
        """Process and save model outputs in the expected format."""
        
        print(f"Processing outputs for {num_topics} topics...")
        print(f"Dictionary size: {len(self.gensim_dictionary)}")
        print(f"Corpus size: {len(self.gensim_corpus)} documents")
        print(f"Sample names: {len(self.abundance_matrix.index)}")
        
        # Get topic-word probabilities (feature probabilities)
        topic_word_matrix = lda_model.get_topics()  # Shape: (num_topics, vocab_size)
        print(f"Topic-word matrix shape: {topic_word_matrix.shape}")
        
        # Create feature probabilities DataFrame
        topic_names = [f"K{num_topics}_MC{i}" for i in range(num_topics)]
        word_names = [self.gensim_dictionary[i] for i in range(len(self.gensim_dictionary))]
        
        print(f"Creating feature probabilities DF: {len(topic_names)} topics x {len(word_names)} features")
        
        feature_probs_df = pd.DataFrame(
            topic_word_matrix,
            index=topic_names,
            columns=word_names
        )
        
        # Get document-topic probabilities (sample probabilities)
        print("Getting document-topic probabilities...")
        doc_topic_matrix = []
        
        for doc_idx, doc_bow in enumerate(self.gensim_corpus):
            doc_topics = lda_model.get_document_topics(doc_bow, minimum_probability=0)
            # Convert to dense vector
            topic_probs = [0.0] * num_topics
            for topic_id, prob in doc_topics:
                topic_probs[topic_id] = prob
            doc_topic_matrix.append(topic_probs)
        
        # Convert to numpy array for easier handling
        doc_topic_array = np.array(doc_topic_matrix)  # Shape: (n_samples, n_topics)
        print(f"Document-topic matrix shape: {doc_topic_array.shape}")
        print(f"Expected sample names: {len(self.abundance_matrix.index)}")
        
        # Verify dimensions match
        if doc_topic_array.shape[0] != len(self.abundance_matrix.index):
            raise ValueError(
                f"Mismatch: doc_topic_matrix has {doc_topic_array.shape[0]} documents "
                f"but abundance_matrix has {len(self.abundance_matrix.index)} samples"
            )
        
        # Create sample probabilities DataFrame
        # Expected format: topics as rows, samples as columns
        sample_probs_df = pd.DataFrame(
            doc_topic_array.T,  # Transpose to get (n_topics, n_samples)
            index=topic_names,
            columns=self.abundance_matrix.index  # Use original sample names
        )
        
        print(f"Sample probabilities DF shape: {sample_probs_df.shape}")
        
        # Save outputs
        try:
            feature_probs_df.to_csv(file_paths['feature_probs'])
            print(f"✓ Saved feature probabilities: {file_paths['feature_probs']}")
        except Exception as e:
            print(f"❌ Error saving feature probabilities: {e}")
            raise
        
        try:
            sample_probs_df.to_csv(file_paths['sample_probs'])
            print(f"✓ Saved sample probabilities: {file_paths['sample_probs']}")
        except Exception as e:
            print(f"❌ Error saving sample probabilities: {e}")
            raise
        
        # Save coherence score - matching old pipeline format exactly
        try:
            coherence_score = float(compute_gensim_coherence(
                lda_model, 
                texts=self.processed_texts,
                dictionary=self.gensim_dictionary,
                coherence='c_v'
            ))
            
            # Match the exact format from old pipeline
            coherence_data = {
                'num_topics': num_topics,
                'coherence_score': coherence_score,
                'method': 'gensim_c_v',
                'formula': 'gensim CoherenceModel with c_v measure'
            }
            with open(file_paths['coherence'], 'w') as f:
                json.dump(coherence_data, f, indent=2)
            print(f"✓ Saved coherence data: {file_paths['coherence']}")
        except Exception as e:
            print(f"❌ Error saving coherence: {e}")
            # Don't raise here, coherence is optional
        
        print(f"✓ Successfully saved model outputs for {num_topics} topics")


# Wrapper class to maintain compatibility with existing workflow
class DirectGensimLDAWrapper:
    """
    Wrapper class to maintain compatibility with existing LDATrainer interface.
    """
    
    def __init__(self, base_directory: str, path_to_mallet: Optional[str] = None, 
                 implementation: str = 'gensim_direct', **gensim_params):
        """
        Initialize with same interface as original LDATrainer.
        """
        if implementation != 'gensim_direct':
            raise ValueError("This wrapper only supports 'gensim_direct' implementation")
        
        self.trainer = DirectGensimLDATrainer(base_directory, **gensim_params)
        self.paths = self.trainer.paths
        
    @property
    def base_directory(self):
        """Expose base_directory for SankeyDataProcessor compatibility."""
        return self.trainer.base_directory
        
    @property
    def all_metrics(self):
        """Expose all_metrics for SankeyDataProcessor compatibility."""
        return self.trainer.all_metrics
        
    def load_training_data(self):
        """Load training data from files."""
        self.trainer.load_data_from_files()
        
    def train_models(self, topic_range: List[int]) -> pd.DataFrame:
        """Train models for multiple topic numbers."""
        return self.trainer.train_models(topic_range)
        
    def get_metrics(self) -> pd.DataFrame:
        """Get training metrics."""
        return self.trainer.all_metrics
