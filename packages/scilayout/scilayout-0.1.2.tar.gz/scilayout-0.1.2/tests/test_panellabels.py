import pytest
from matplotlib.pyplot import close

import scilayout


@pytest.fixture
def ax() -> scilayout.classes.PanelAxes:
    fig = scilayout.figure()
    testax = fig.add_panel((1, 2, 5, 5), method="size")
    yield testax
    close(fig)


@pytest.fixture
def panellabel(ax: scilayout.classes.PanelAxes) -> scilayout.classes.PanelLabel:
    ax.add_label("a")
    return ax.panellabel


class TestPanelLabels:
    def test_initial_panel_labels(self, panellabel):
        xoffset = scilayout.style.params["panellabel.xoffset"]
        yoffset = scilayout.style.params["panellabel.yoffset"]
        assert panellabel.xoffset == pytest.approx(xoffset)
        assert panellabel.yoffset == pytest.approx(yoffset)
        pos = panellabel.get_location()
        assert pos[0] == pytest.approx(1 + xoffset)
        assert pos[1] == pytest.approx(2 + yoffset)

    def test_panel_reposition(self, ax, panellabel):
        """Test that the label is repositioned when the panel is moved"""
        ax.set_location((2, 3, 6, 6), method="size")
        xoffset = scilayout.style.params["panellabel.xoffset"]
        yoffset = scilayout.style.params["panellabel.yoffset"]
        pos = panellabel.get_location()
        assert pos[0] == pytest.approx(2 + xoffset)
        assert pos[1] == pytest.approx(3 + yoffset)

    def test_set_location(self, panellabel):
        """Set locations of panel labels manually"""
        # Test x position
        panellabel.set_location(x=3)
        pos = panellabel.get_location()
        assert pos[0] == pytest.approx(3)

        # Test y position
        panellabel.set_location(y=4.2)
        pos = panellabel.get_location()
        assert pos[1] == pytest.approx(4.2)

        # Test both x and y location changes
        panellabel.set_location(x=1.5, y=2.5)
        pos = panellabel.get_location()
        assert pos[0] == pytest.approx(1.5)
        assert pos[1] == pytest.approx(2.5)
