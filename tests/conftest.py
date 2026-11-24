from __future__ import annotations

from collections.abc import Iterator

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest


@pytest.fixture(autouse=True)
def reset_matplotlib_state() -> Iterator[None]:
    """Reset global Matplotlib rcParams and close all figures around every test."""
    matplotlib.rcdefaults()
    plt.close("all")
    yield
    plt.close("all")
    matplotlib.rcdefaults()
