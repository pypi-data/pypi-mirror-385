# Embeddings Module

The embeddings module converts text and structured data into dense vector representations suitable for similarity search.

## Overview

Embeddings are the core of modern similarity search. This module provides:
- **Text Embeddings**: Deep learning models for semantic similarity
- **PII Tokenization**: Specialized processing for names, emails, addresses, and phone numbers
- **Numeric Features**: Encoding and scaling of numeric data
- **Categorical Features**: One-hot and target encoding

## Text Embeddings

Deep learning-based embeddings capture semantic meaning beyond keyword matching.

### Module: `privacy_similarity.embeddings.text_embeddings`

#### Class: `TextEmbedder`

Generates embeddings using Sentence Transformers.

**Parameters:**
- `model_name` (str): Hugging Face model name or path
  - Default: 'sentence-transformers/all-MiniLM-L6-v2'
  - Other options: 'all-mpnet-base-v2' (better quality), 'paraphrase-multilingual-MiniLM-L12-v2' (multilingual)
- `device` (str): 'cpu' or 'cuda' (default: 'cpu')
- `batch_size` (int): Batch size for encoding (default: 32)
- `normalize` (bool): L2-normalize embeddings (default: True)

**Example:**
```python
from privacy_similarity.embeddings import TextEmbedder

embedder = TextEmbedder(
    model_name='sentence-transformers/all-MiniLM-L6-v2',
    device='cpu',
    normalize=True
)
```

#### Methods

##### `encode(texts: List[str]) -> np.ndarray`

Encodes a list of texts into embeddings.

**Parameters:**
- `texts`: List of strings to encode

**Returns:**
- Array of shape (len(texts), embedding_dim)

**Example:**
```python
texts = [
    'Customer interested in sports equipment',
    'Looking for athletic gear and accessories',
    'Technology enthusiast, loves gadgets'
]

embeddings = embedder.encode(texts)
print(embeddings.shape)  # (3, 384) for MiniLM-L6-v2
```

**Performance:**
- MiniLM-L6-v2: ~1000 texts/sec on CPU, 384 dimensions
- MPNet-base-v2: ~400 texts/sec on CPU, 768 dimensions
- GPU: 5-10x faster

##### `encode_batch(texts: List[str], batch_size: int = 32) -> np.ndarray`

Encodes texts in batches for large datasets.

**Parameters:**
- `texts`: List of strings
- `batch_size`: Number of texts per batch

**Returns:**
- Array of embeddings

**Example:**
```python
# Encode 10,000 customer descriptions
large_texts = [...]  # 10,000 descriptions
embeddings = embedder.encode_batch(large_texts, batch_size=64)
```

**Memory Tip:** Larger batch sizes are faster but use more memory. If you get OOM errors, reduce batch_size.

##### `similarity(text1: str, text2: str) -> float`

Computes cosine similarity between two texts.

**Parameters:**
- `text1`: First text
- `text2`: Second text

**Returns:**
- Similarity score in [-1, 1] (typically [0, 1] for real text)

**Example:**
```python
sim = embedder.similarity(
    'I love sports and outdoor activities',
    'Passionate about athletics and fitness'
)
print(f'Similarity: {sim:.3f}')  # ~0.75-0.85
```

### Model Selection Guide

| Model | Dim | Speed | Quality | Use Case |
|-------|-----|-------|---------|----------|
| all-MiniLM-L6-v2 | 384 | Fast | Good | General purpose, large scale |
| all-mpnet-base-v2 | 768 | Medium | Best | High accuracy needed |
| paraphrase-multilingual | 384 | Fast | Good | Multiple languages |
| multi-qa-MiniLM-L6 | 384 | Fast | Good | Question answering |

**Recommendation:** Start with MiniLM-L6-v2, upgrade to MPNet if accuracy is insufficient.

## PII Tokenization

Specialized processing for personally identifiable information.

#### Class: `PIITokenizer`

Tokenizes and normalizes PII fields for similarity matching.

**Parameters:**
- `lowercase` (bool): Convert to lowercase (default: True)
- `remove_punctuation` (bool): Remove punctuation (default: True)
- `phonetic` (bool): Use phonetic encoding (default: False)

**Example:**
```python
from privacy_similarity.embeddings import PIITokenizer

tokenizer = PIITokenizer(
    lowercase=True,
    remove_punctuation=True,
    phonetic=True
)
```

#### Methods

##### `tokenize_name(name: str) -> List[str]`

Tokenizes a person's name into components.

**Parameters:**
- `name`: Full name string

**Returns:**
- List of name tokens

**Processing steps:**
1. Lowercase and remove punctuation
2. Split into tokens
3. Remove common prefixes/suffixes (Dr., Jr., etc.)
4. Optional: Apply phonetic encoding (Soundex, Metaphone)

**Example:**
```python
tokens = tokenizer.tokenize_name('Dr. John A. Smith Jr.')
print(tokens)  # ['john', 'smith']

# With phonetic encoding
tokenizer_phonetic = PIITokenizer(phonetic=True)
tokens = tokenizer_phonetic.tokenize_name('John Smith')
print(tokens)  # ['J500', 'S530'] (Soundex codes)
```

**Why phonetic?** Matches names that sound alike:
- John/Jon → J500
- Smith/Smyth → S530

##### `tokenize_email(email: str) -> List[str]`

Tokenizes an email address.

**Parameters:**
- `email`: Email address

**Returns:**
- List of tokens from username and domain

**Example:**
```python
tokens = tokenizer.tokenize_email('john.smith@example.com')
print(tokens)  # ['john', 'smith', 'example', 'com']
```

**Use case:** Find similar emails even with typos:
- john.smith@gmail.com
- jon.smith@gmail.com
- j.smith@gmail.com

##### `tokenize_address(address: str) -> List[str]`

Tokenizes a physical address.

**Parameters:**
- `address`: Street address

**Returns:**
- List of address components

**Processing:**
1. Normalize abbreviations (St → Street, Ave → Avenue)
2. Extract number, street name, type
3. Remove common noise words

**Example:**
```python
tokens = tokenizer.tokenize_address('123 Main St., Apt 4B')
print(tokens)  # ['123', 'main', 'street', 'apt', '4b']
```

**Handles variations:**
- 123 Main St → 123 Main Street
- 123 Main Street, Suite 100
- 123 N Main St

##### `tokenize_phone(phone: str) -> str`

Normalizes a phone number.

**Parameters:**
- `phone`: Phone number in any format

**Returns:**
- Normalized phone string (digits only)

**Example:**
```python
normalized = tokenizer.tokenize_phone('(555) 123-4567')
print(normalized)  # '5551234567'

normalized = tokenizer.tokenize_phone('+1-555-123-4567')
print(normalized)  # '15551234567'
```

**Handles formats:**
- (555) 123-4567
- 555-123-4567
- +1 555 123 4567
- 5551234567

## Numeric Features

Encoding and scaling of numeric data for similarity search.

### Module: `privacy_similarity.embeddings.numeric_features`

#### Class: `NumericFeatureEncoder`

Encodes numeric and categorical features into vectors.

**Parameters:**
- `numeric_columns` (List[str]): Names of numeric columns
- `categorical_columns` (List[str]): Names of categorical columns
- `scaling_method` (str): 'standard', 'minmax', or 'robust' (default: 'standard')
- `categorical_encoding` (str): 'onehot' or 'target' (default: 'onehot')
- `handle_missing` (str): 'mean', 'median', 'drop' (default: 'mean')

**Example:**
```python
from privacy_similarity.embeddings import NumericFeatureEncoder

encoder = NumericFeatureEncoder(
    numeric_columns=['age', 'income', 'credit_score'],
    categorical_columns=['state', 'occupation'],
    scaling_method='standard',
    categorical_encoding='onehot'
)
```

#### Methods

##### `fit(df: pd.DataFrame) -> None`

Fits the encoder on training data.

**Parameters:**
- `df`: Training DataFrame

**Example:**
```python
import pandas as pd

df = pd.DataFrame({
    'age': [25, 30, 35, 40],
    'income': [50000, 60000, 70000, 80000],
    'state': ['CA', 'NY', 'CA', 'TX']
})

encoder.fit(df)
```

##### `transform(df: pd.DataFrame) -> np.ndarray`

Transforms data into feature vectors.

**Parameters:**
- `df`: DataFrame to transform

**Returns:**
- Numpy array of encoded features

**Example:**
```python
features = encoder.transform(df)
print(features.shape)  # (4, 5) - 2 numeric + 3 one-hot encoded states
```

##### `fit_transform(df: pd.DataFrame) -> np.ndarray`

Fits and transforms in one step.

**Example:**
```python
features = encoder.fit_transform(df)
```

### Scaling Methods

#### Standard Scaling (Z-score normalization)
- Formula: `(x - mean) / std`
- Range: Typically [-3, 3]
- Best for: Normally distributed data

```python
encoder = NumericFeatureEncoder(scaling_method='standard')
```

#### MinMax Scaling
- Formula: `(x - min) / (max - min)`
- Range: [0, 1]
- Best for: Data with known bounds, neural networks

```python
encoder = NumericFeatureEncoder(scaling_method='minmax')
```

#### Robust Scaling
- Formula: `(x - median) / IQR`
- Range: Variable
- Best for: Data with outliers

```python
encoder = NumericFeatureEncoder(scaling_method='robust')
```

### Categorical Encoding

#### One-Hot Encoding
- Creates binary column for each category
- Best for: Low cardinality (<50 categories)
- Memory: High for many categories

```python
encoder = NumericFeatureEncoder(categorical_encoding='onehot')

# Input: ['CA', 'NY', 'TX']
# Output: [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
```

#### Target Encoding
- Replaces category with mean of target variable
- Best for: High cardinality (>50 categories)
- Memory: Efficient

```python
encoder = NumericFeatureEncoder(
    categorical_encoding='target',
    target_column='conversion_rate'
)
```

### Missing Value Handling

**Mean Imputation:**
```python
encoder = NumericFeatureEncoder(handle_missing='mean')
# Replaces NaN with column mean
```

**Median Imputation:**
```python
encoder = NumericFeatureEncoder(handle_missing='median')
# Replaces NaN with column median (better for outliers)
```

**Drop Rows:**
```python
encoder = NumericFeatureEncoder(handle_missing='drop')
# Removes rows with missing values
```

## Combining Embeddings

Combine multiple embedding types for richer representations.

### Concatenation

```python
# Text embeddings
text_emb = text_embedder.encode(df['description'])  # Shape: (N, 384)

# PII tokens → MinHash sketches
pii_tokens = [tokenizer.tokenize_name(n) for n in df['name']]
pii_emb = create_minhash_sketches(pii_tokens)  # Shape: (N, 128)

# Numeric features
numeric_emb = numeric_encoder.transform(df)  # Shape: (N, 10)

# Combine
combined = np.concatenate([text_emb, pii_emb, numeric_emb], axis=1)
print(combined.shape)  # (N, 522)
```

### Weighted Combination

```python
# Give different importance to different features
combined = np.concatenate([
    text_emb * 1.0,      # Full weight
    pii_emb * 0.5,       # Half weight
    numeric_emb * 0.3    # Lower weight
], axis=1)
```

### Stacking

```python
# Create separate indices for each embedding type
# Then combine results at query time
text_results = search_text_index(query)
pii_results = search_pii_index(query)
numeric_results = search_numeric_index(query)

# Merge and re-rank
final_results = merge_results([text_results, pii_results, numeric_results])
```

## Performance Optimization

### Batch Processing

```python
# Process large datasets in chunks
def encode_large_dataset(texts, batch_size=1000):
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_emb = embedder.encode(batch)
        embeddings.append(batch_emb)
    return np.vstack(embeddings)
```

### GPU Acceleration

```python
# Use GPU for 5-10x speedup
embedder = TextEmbedder(
    model_name='all-MiniLM-L6-v2',
    device='cuda',
    batch_size=128  # Increase batch size for GPU
)
```

### Caching

```python
# Cache embeddings for reuse
import joblib

embeddings = embedder.encode(texts)
joblib.dump(embeddings, 'embeddings_cache.pkl')

# Later
embeddings = joblib.load('embeddings_cache.pkl')
```

## Advanced Topics

### Fine-tuning Embeddings

For domain-specific data, fine-tune the embedding model:

```python
from sentence_transformers import SentenceTransformer, losses, InputExample
from torch.utils.data import DataLoader

# Create training examples
train_examples = [
    InputExample(texts=['text1', 'text2'], label=0.9),  # Similar
    InputExample(texts=['text1', 'text3'], label=0.1),  # Dissimilar
]

# Fine-tune
model = SentenceTransformer('all-MiniLM-L6-v2')
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
train_loss = losses.CosineSimilarityLoss(model)
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=1,
    warmup_steps=100
)
```

### Dimensionality Reduction

Reduce embedding dimensions for faster search:

```python
from sklearn.decomposition import PCA

# Reduce 384D to 128D
pca = PCA(n_components=128)
reduced_embeddings = pca.fit_transform(embeddings)

# Trade-off: 3x smaller, ~5% accuracy loss
```

## References

- Reimers & Gurevych. "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks" (2019)
- Devlin et al. "BERT: Pre-training of Deep Bidirectional Transformers" (2019)
- Muennighoff et al. "SGPT: GPT Sentence Embeddings for Semantic Search" (2022)
