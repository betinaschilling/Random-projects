"""Utilitários experimentais."""
import random as _random


def sample(items, k, seed=None):
    """Amostra reprodutível de k itens sem reposição."""
    return _random.Random(seed).sample(list(items), k)
