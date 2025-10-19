import pytest
from matplotlib.pyplot import close

import scilayout


@pytest.fixture
def fig() -> scilayout.classes.SciFigure:
    scifig = scilayout.classes.SciFigure()
    scifig.set_size_cm(13, 10)
    yield scifig
    close(scifig)


@pytest.fixture
def grid(fig) -> scilayout.classes.GuideGridClass:
    return fig.grid


class TestGrid:
    def test_grid_init(self, fig):
        pass

    def test_grid_clearing_and_drawing(self, fig, grid):
        """Using fig.clear() and how it interacts with the grid"""
        pass

    def test_grid_parameters(self, fig, grid):
        """Test that grid can have its parameters changed properly"""
        pass
