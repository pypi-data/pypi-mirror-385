<!-- # Simple Stats

A simple Python library for basic statistical calculations.

## Features

- Calculate mean
- Calculate median
- Calculate mode
- Calculate standard deviation

## Installation

You can install the library using pip:

```bash
pip install .

## Usage
from common_stats import mean, median, mode, standard_deviation

data = [1, 2, 3, 4, 5]

print("Mean:", mean(data))
print("Median:", median(data))
print("Mode:", mode(data))
print("Standard Deviation:", standard_deviation(data)) -->

# What is String Grammar Fuzzy Clustering?

String Grammar Fuzzy Clustering is a clustering framework designed for syntactic or structural pattern recognition, where each data instance is represented not as a numeric vector but as a string that encodes structural information.

Unlike conventional numerical clustering method (e.g., Fuzzy C-Means), which assume that data have a fixed-lenght feature vector whereas structural clustering method operates directly on string data whose lenghts and internal structures may vary.

In this approach, each pattern is described by a sequence of primitives (symbols) defined by grammartical rules. This is similar to how a sentence is formed from characters following syntax rules.

To measure similarity between strings, the method employs the Levenshtein distance, which counts the minimum number of edit operations (insertions, deletions, substitutions) required to transform on string into another.

The "fuzzy" aspect of this framwork allows each string to belong partically to multiple clusters, with a membership degree that reflects how strongly it is associated with each cluster. This provieds a more flexible and realistic clustering behavior copared to traditional "hard" clustering, which forces each sample to belong to only one group.

# About This Library

This Python library implements two core algorithms:

1. String Grammar Fuzzy C-Medians (sgFCMed)
The sgFCMed algorithm extends the conventional Fuzzy C-Medians to handle string-based or syntactic data by using the Levenshtein distance instead of Euclidean distance. Each cluster is represented by a prototype string that minimizes the weighted sum of distances to all strings in the cluster, and each sample has a fuzzy membership value indicating its degree of belonging to different clusters. This method effectively clusters variable-length symbolic data, capturing structural similarity without requiring vector representations.
    ## Key Features 
    - Works directly on string-encoded or grammar-based data
    - Uses Levenshtein distance for similarity measurement
    - Maintains a fuzzy membership matrix (U) that quantifies how strongly each string belongs to each cluster.
    - Prototype refinement via modified median search for structural accuracy
    - Ideal for datasets with overlapping but relatively clean patterns

2. String Grammar Possibilistic Fuzzy C-Medians (sgPFCMed)
The sgPFCMed algorithm enhances sgFCMed by integrating possibilistic clustering theory, introducing both membership and typicality values for each string. While membership reflects relative association across clusters, typicality measures how representative a string is within a single cluster, improving robustness against noise and outliers. This combination allows sgPFCMed to produce more reliable and stable clustering results, especially in datasets with uncertain or overlapping string patterns.
    ## Key Features 
    - Integrates membership (U) and typicality (T) for dual uncertainty modeling
    - Automatically updates γ (gamma) parameters per cluster
    - Better resilience to noisy or ambiguous strings
    - Parallelized medoid and modified median updates
    - Suitable for real-world or imperfect string data where overlap and noise occur

# Installation

You can install the library using pip:

```bash
pip install stringGrammar
```

# USAGE

## Example Code

```python
import random
from stringGrammar import SGFCMed # Import the clustering class

if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)

    # Define a list of strings to cluster
    data = ["book", "back", "boon", "cook", "look", "cool", "kick", "lack", "rack", "tack"]

    # ======== Example 1: String Grammar Fuzzy C-Medians (sgFCMed) ========
    print("=== String Grammar Fuzzy C-Medians (sgFCMed) ===")
    model_fcmed = SGFCMed(C=2, m=2.0)   # 2 clusters, fuzzifier m = 2.0
    model_fcmed.fit(data)

    print("Prototypes:", model_fcmed.prototypes())
    print("\nMembership Matrix (U):")
    for s, u in zip(data, model_fcmed.membership()):
        print(f"{s:>6} → {[round(val, 3) for val in u]}")

    # Predict clusters for new data
    new_data = ["hack", "rook", "cook"]
    preds = model_fcmed.predict(new_data)
    print("\nPredictions:")
    for s, c in zip(new_data, preds):
        print(f"{s} → Cluster {c+1}")

    # ======== Example 2: String Grammar Possibilistic Fuzzy C-Medians (sgPFCMed) ========
    print("\n\n=== String Grammar Possibilistic Fuzzy C-Medians (sgPFCMed) ===")
    model_pfcmed = SGPFCMed(C=2, m=2.0, eta=2.0)  # eta = typicality fuzzifier
    model_pfcmed.fit(data)

    print("Prototypes:", model_pfcmed.prototypes())

    print("\nMembership Matrix (U):")
    for s, u in zip(data, model_pfcmed.membership()):
        print(f"{s:>6} → {[round(val, 3) for val in u]}")

    print("\nTypicality Matrix (T):")
    for s, t in zip(data, model_pfcmed.typicality()):
        print(f"{s:>6} → {[round(val, 3) for val in t]}")

    # Predict clusters for new data
    preds_pfc = model_pfcmed.predict(new_data)
    print("\nPredictions:")
    for s, c in zip(new_data, preds_pfc):
        print(f"{s} → Cluster {c+1}")