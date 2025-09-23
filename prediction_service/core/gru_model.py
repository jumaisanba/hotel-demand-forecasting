import torch
import torch.nn as nn
from typing import Dict, Tuple, List


class GRUForecaster(nn.Module):
    """
    Модель прогнозирования временных рядов на основе GRU.

    Args:
        num_numeric_features (int): количество числовых признаков.
        embedding_sizes (dict): словарь {feature_name: (num_embeddings, embedding_dim)}
            для категориальных признаков.
        hidden_size (int, optional): размер скрытого состояния GRU. По умолчанию 64.
        gru_layers (int, optional): число слоёв GRU. По умолчанию 2.
        dropout (float, optional): вероятность dropout. По умолчанию 0.2.
        forecast_horizon (int, optional): горизонт прогноза (число шагов вперёд). По умолчанию 30.
        output_dims (int, optional): размерность выхода (например, 2 — бронирования и отмены). По умолчанию 2.
    """

    def __init__(self,
                 num_numeric_features: int,
                 embedding_sizes: Dict[str, Tuple[int, int]],
                 hidden_size: int = 64,
                 gru_layers: int = 2,
                 dropout: float = 0.2,
                 forecast_horizon: int = 30,
                 output_dims: int = 2):
        super().__init__()

        # Фиксированный порядок категориальных признаков
        self.categorical_order: List[str] = list(embedding_sizes.keys())

        # Embedding-слои
        self.embeddings = nn.ModuleDict({
            name: nn.Embedding(num_embeddings, emb_dim)
            for name, (num_embeddings, emb_dim) in embedding_sizes.items()
        })

        self.embedding_dim = sum(emb_dim for _, (_, emb_dim) in embedding_sizes.items())
        self.total_input_dim = num_numeric_features + self.embedding_dim

        # GRU
        self.gru = nn.GRU(
            input_size=self.total_input_dim,
            hidden_size=hidden_size,
            num_layers=gru_layers,
            dropout=dropout if gru_layers > 1 else 0.0,
            batch_first=True
        )

        # Финальный слой
        self.fc = nn.Linear(hidden_size, forecast_horizon * output_dims)

        self.forecast_horizon = forecast_horizon
        self.output_dims = output_dims

    def forward(self, x_numeric: torch.Tensor, x_cat: Dict[str, torch.Tensor]) -> torch.Tensor:
        """
        Прямой проход модели.

        Args:
            x_numeric (Tensor): числовые признаки [B, T, num_numeric_features].
            x_cat (dict): словарь категориальных признаков {name: Tensor[B, T]}.

        Returns:
            Tensor: прогноз [B, forecast_horizon, output_dims].
        """
        # Embeddings в фиксированном порядке
        embedded = [self.embeddings[name](x_cat[name]) for name in self.categorical_order]
        x_cat_embedded = torch.cat(embedded, dim=-1) if embedded else None  # [B, T, embedding_total_dim]

        # Объединение признаков
        if x_cat_embedded is not None:
            x = torch.cat([x_numeric, x_cat_embedded], dim=-1)  # [B, T, total_input_dim]
        else:
            x = x_numeric

        # GRU
        output, _ = self.gru(x)  # [B, T, hidden_size]
        last_output = output[:, -1, :]  # берём последнее состояние [B, hidden_size]

        # Финальный слой + reshape
        out = self.fc(last_output)  # [B, forecast_horizon * output_dims]
        return out.view(-1, self.forecast_horizon, self.output_dims)  # [B, H, O]
