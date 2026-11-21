from random_projects import sample


def test_sample_is_reproducible():
    assert sample(range(100), 5, seed=42) == sample(range(100), 5, seed=42)
