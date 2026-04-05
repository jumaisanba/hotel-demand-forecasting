import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def create_sequences(
    df: pd.DataFrame,
    feature_cols: list,
    target_col: str,
    window_size: int
) -> tuple[np.ndarray, np.ndarray]:
    """
    Преобразует DataFrame в обучающие последовательности.

    Returns:
        X: массив (n_samples, window_size, n_features).
        y: массив (n_samples,).
    """
    sequences, targets = [], []
    for i in range(len(df) - window_size):
        seq = df[feature_cols].iloc[i:i + window_size].values
        target = df[target_col].iloc[i + window_size]
        sequences.append(seq)
        targets.append(target)

    logger.debug(f"Сформировано {len(sequences)} последовательностей для обучения")
    return np.array(sequences), np.array(targets)
