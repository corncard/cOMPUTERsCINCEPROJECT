"""Clustering utilities for PocketLab spending profiles."""

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from .features import build_spending_profiles


def cluster_spending(df, n_clusters=3, period="W"):
    """Group similar spending periods using K-Means."""
    profiles = build_spending_profiles(df, period=period)

    if len(profiles) < n_clusters:
        raise ValueError(
            f"Need at least {n_clusters} spending periods; "
            f"found {len(profiles)}."
        )

    features = profiles.copy()
    log_columns = ["total_amount", "transaction_count", "average_amount"]
    for column in log_columns:
        features[column] = np.log1p(features[column])

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    # This baseline fits on the full dataset; prediction on unseen periods needs
    # a train/test split or an incremental fitting strategy.
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    profiles["cluster"] = model.fit_predict(scaled_features)

    return profiles, model, scaler
