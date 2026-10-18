"""Machine-learning utilities for PocketLab."""

from .clustering import cluster_spending
from .features import build_spending_profiles

__all__ = ["build_spending_profiles", "cluster_spending"]
