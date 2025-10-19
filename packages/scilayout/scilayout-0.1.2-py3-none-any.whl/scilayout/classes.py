"""Classes for handling panel layout in cm with upper left origin."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib as mpl
from matplotlib import figure
from matplotlib.axes import Axes
from matplotlib.text import Text

from . import base, locations, style
from .grid import GuideGridClass
from .types import BoundCM, ExtentCM, centimetres


# TODO: make docs here the best
class SciFigure(figure.Figure):
    """Figure object that handles panel layout in cm with upper left origin.

    Methods
    -------
    draw_grid()
        Add a centimetre grid overlay onto the figure.

    """

    grid: GuideGridClass
    """Handler for guide grid."""

    def __init__(
        self,
        *args: tuple,
        **kwargs: dict,
    ) -> None:
        """Initialise a figure with extra scientific-figure ready features.

        Arguments and keyword arguments are fed into matplotlib's figure.Figure.
        Please see https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html
        """
        # must initialise before super because it'll call clear
        self.grid = GuideGridClass(self)
        super().__init__(*args, **kwargs)
        self.cm_overlay = None
        self.transCM = locations.CMTransform(self)

    def set_size_cm(self, w: float, h: float) -> None:
        """Set size of figure in cm.

        Parameters
        ----------
        w : float
            Width (cm) of figure.
        h : float
            Height (cm) of figure.

        """
        base.set_figure_size_cm(self, w, h)
        # TODO: resize panels to preserve their position

        if self.cm_overlay is not None:
            # redraw overlay
            self.remove_overlay()
            self.add_overlay()

    def add_panel(
        self,
        location: BoundCM
        | ExtentCM
        | tuple[centimetres, centimetres, centimetres, centimetres],
        panellabel: str = None,
        method: str = "bbox",
        **kwargs: dict,
    ) -> PanelAxes:
        """Add panel (axes) to the figure.

        Creates a PanelAxes object positioned with cms
        args and kwargs are passed to PanelAxes.
        Required args is location (x1, y1, x2, y2) in cm from top left corner of figure.

        Call signature ::

            fig.add_panel((1, .5, 5, 6.5), method="size")


        Parameters
        ----------
        location : BoundCM | ExtentCM | tuple[float, float, float, float]
            Location of the panel in cm (x0, y0, x1, y1). Can be:
            - Bound: (x, y, w, h)
            - Extent: (x0, y0, x1, y1)
        panellabel : str | None
            Letter to initialise the panel with.
        method : str
            How to interpret the coordinates of the location.
            "bbox" (default) interprets x2 and y2 as coordinates.
            "size" interprets x2 and y2 as width and height.
        kwargs : dict
            Key word arguments to pass to PanelAxes initialisation.

        Returns
        -------
        PanelAxes
            The panel object

        """
        # TODO: should this be return self.fig.add_axes(rect, axes_class=PanelAxes)
        # add_axes(rect, projection=None, polar=False, **kwargs)
        # add_axes(ax)
        # with rect being converted into bm?
        return PanelAxes(
            self,
            location=location,
            panellabel=panellabel,
            method=method,
            **kwargs,
        )

    def draw_grid(
        self,
        **kwargs: dict,
    ) -> None:
        """Add cm grid guide to the figure."""
        if self.grid is None:
            self.grid = GuideGridClass(self, **kwargs)
        else:
            # if kwargs are given print warning of
            # changing settings with this function is not implemented
            if kwargs:
                # TODO: implement changing grid settings
                print(
                    "Warning: Setting grid settings with draw_grid() is not implemented.",
                )
            self.grid.show()

    def clear(
        self,
        **kwargs: dict,
    ) -> None:
        """Clear the figure (including removal of grid)."""
        super().clear(**kwargs)
        self.cm_overlay = None
        if self.grid:
            self.grid._detach_ax()

    def clf(
        self,
        **kwargs: dict,
    ) -> None:
        """Clear the figure entirely."""
        super().clf(**kwargs)
        self.cm_overlay = None

    def set_location(
        self,
        x: int,
        y: int,
        method: str = "px",
    ) -> None:
        """Set location of a figure window on the screen.

        :param x: Horizontal coordinate from left
        :type x: int
        :param y: Vertical coordinate from top
        :type y: int
        :param method: Method to set location, defaults to "px"
        :type method: str, optional
        """
        # TODO: add support for other backends

        backend = mpl.get_backend()
        window = self.canvas.manager.window

        if method != "px":
            # TODO: add support for method='fraction' and 'cm'?
            msg = 'Only method="px" is implemented'
            raise NotImplementedError(msg)

        if backend.startswith("Qt"):
            _, _, dx, dy = window.geometry().getRect()
            window.setGeometry(x, y, dx, dy)
        else:
            msg = f"Backend {backend} not implemented. Submit issue to add suport."
            raise NotImplementedError(msg)

    def export(self, savepath: Path | str, **kwargs: dict) -> None:
        """Export the figure to a file.

        Parameters
        ----------
        savepath : str | Path
            The path to save the figure to
        kwargs : dict
            Additional arguments to pass to savefigure

        """
        base.savefigure(self, savepath, **kwargs)

    def close(self) -> None:
        """Close figure window (convenience function)."""
        mpl.pyplot.close(self)


class PanelAxes(Axes):
    """Extension of Axes object to handle panel layout in cm with upper left origin.

    To use cm 'location' is used instead of 'position' e.g. set_location().
    """

    panellabel: PanelLabel

    def __init__(
        self,
        fig: mpl.figure.Figure,
        location: BoundCM | ExtentCM,
        panellabel: str = None,
        method: str = "bbox",
        **kwargs,
    ) -> None:
        rect = (0, 0, 1, 1)  # dummy rect
        super().__init__(fig, rect, **kwargs)
        fig.add_axes(self)  # apparently this isn't in the super or something
        # TODO: test this behaves as expected
        self.panellabel = None
        if panellabel is not None:
            self.add_label(panellabel)
        self.set_location(location, method=method)

    def set_location(
        self,
        location: tuple,
        method: str = "bbox",
    ) -> None:
        """Set location of panel in cm.

        If method is 'size' then location is (x, y, width, height)

        location : ExtentCM | BoundCM | Tuple[float, float, float, float]
            Coordinates from top left corner in cm
        method : str
            Coordinate system of 'bbox' or 'size', default 'bbox'
        """
        assert len(location) == 4, "Location must be of length 4"
        if method == "size":
            location = (
                location[0],
                location[1],
                location[0] + location[2],
                location[1] + location[3],
            )
            # location = ExtentCM(*location)  # TODO: can't set attribute

        elif method == "bbox":
            pass
        else:
            msg = 'Method must be either "size" or "bbox"'
            raise ValueError(msg)
        self.set_position(locations.locationcm_to_position(self.get_figure(), location))
        if self.panellabel is not None:
            self.panellabel.set_offset(self.panellabel.xoffset, self.panellabel.yoffset)

    def get_location(self) -> tuple:
        """Get location of axes in cm (from top left corner)."""
        # TODO: use self.get_figure().transCM?
        figsize = locations.inch_to_cm(self.get_figure().get_size_inches())
        bbox_pos = self.get_position().get_points()
        xmin, ymax = bbox_pos[0]
        xmax, ymin = bbox_pos[1]
        ymin = 1 - ymin
        ymax = 1 - ymax

        xmin = xmin * figsize[0]
        xmax = xmax * figsize[0]
        ymin = ymin * figsize[1]
        ymax = ymax * figsize[1]
        # TODO: improve type hinting
        return xmin, ymin, xmax, ymax

    def add_label(
        self,
        label: str,
        ha: str = None,
    ) -> None:
        """Add a label to the panel, or set its value.

        Parameters
        ----------
        label : str
            Identifier string for the panel e.g. 'a'
        ha : str (optional)
            Horizontal alignment, defaults to None

        """
        # TODO: allow for more complexity at inisitalisation (especially x/y offsets, positions)
        if self.panellabel is not None:
            self.panellabel.text.set_text(label)
        else:
            self.panellabel = PanelLabel(self, label)
        if ha is not None:
            self.panellabel.set_alignment(h=ha)

    def clear(self) -> None:
        """Clear the axes."""
        # Handle the panel label during clear
        super().clear()
        # check if panellabel is attr
        if "panellabel" in self.__dict__ and self.panellabel is not None:
            try:
                self.panellabel.text.remove()
            except NotImplementedError:
                # Newer versions of matplotlib do something funky here.
                pass
            self.panellabel = None


class PanelLabel:
    """A label for a multi-part figure.

    The letter has its initialisation position at exactly the upper left corner of the
    axes, so if you use `fill_yaxis` on it then the letter will be touching the data. An
    upper case 12 point letter is just under 0.5cm tall, so an offset of 0.1 looks good.

    The 'anchor position' is the top left corner of the associated PanelAxes.

    To change the properties of the text, use the `text` attribute directly.
    (e.g. `panellabel.text.set_horizontal_alignment('right')`)

    """

    ax: PanelAxes
    xoffset: float
    """cm from top left corner"""
    yoffset: float
    """cm from top left corner"""
    text: Text
    """The actual text object"""

    def __init__(self, ax: PanelAxes, label: str) -> None:
        """Create text item to identify the panel."""
        self.text = base.create_panel_label(ax, label)
        self.ax = ax
        self.xoffset = style.params["panellabel.xoffset"]
        self.yoffset = style.params["panellabel.yoffset"]
        self.set_offset(x=self.xoffset, y=self.yoffset)

    @property
    def anchorlocation(self) -> tuple:
        """Top left location of the panel."""
        return self.ax.get_location()[0:2]

    def get_location(self) -> tuple[centimetres, centimetres]:
        """Get position on figure in cm."""
        figfrac = self.text.get_position()
        return locations.fraction_to_cm(self.ax.get_figure(), figfrac)

    def set_location(self, x: float = None, y: float = None) -> None:
        """Set position of label on figure in cm directly."""
        currentpos = self.get_location()
        tempxy = (currentpos[0] if x is None else x, currentpos[1] if y is None else y)
        convertedfrac = locations.cm_to_fraction(self.ax.get_figure(), tempxy)
        setfrac = (convertedfrac[0], convertedfrac[1])
        self.text.set_position(setfrac)

    # TODO: add some method for determining position if it's on a plot graph (i.e. label over ylabel position?)

    def set_offset(self, x: float = None, y: float = None) -> None:
        """Set position of label relative to the upper left corner of the axes.

        Parameters
        ----------
        x : float
            Distance (cm) from location to horizontally offset label.
            Negative values move label left.
        y : float
            Distance (cm) from location to vertically offset label.
            Negative values move label upwards.

        """
        # x_cm, y_cm = fraction_to_cm(self.ax.get_figure(), self.text.get_location())
        true_x, true_y = self.anchorlocation[0], self.anchorlocation[1]
        x = self.xoffset if x is None else x
        y = self.yoffset if y is None else y
        x_cm = true_x + x
        y_cm = true_y + y
        self.xoffset = x
        self.yoffset = y
        self.set_location(x_cm, y_cm)

    def set_alignment(self, h: str = "left", v: str = "baseline") -> None:
        """Align the panel letter.

        For more info on alignment options see:
        https://matplotlib.org/stable/gallery/text_labels_and_annotations/text_alignment.html

        Parameters
        ----------
        h : str
            Text horizontal alignment
        v : str
            Text vertical alignment

        """
        # todo: change this behaviour?
        if h == "right":
            self.set_offset(x=-1)


class FigureText:
    """A text object that is positioned relative to the figure."""

    text: Text
    """Text object."""

    def __init__(
        self,
        x: centimetres,
        y: centimetres,
        text: str,
        figure: mpl.figure.Figure,
        **kwargs: dict[str, Any],
    ) -> None:
        """Create FigureText object."""
        x, y = locations.cm_to_fraction(figure, (x, y))
        self.text = figure.text(
            x,
            y,
            text,
            figure=figure,
            transform=figure.transFigure,
            **kwargs,
        )

    def set_position(self, x: centimetres, y: centimetres) -> None:
        """Set position of figure text in cm."""
        x, y = locations.cm_to_fraction(self.text.get_figure(), (x, y))
        self.text.set_position((x, y))

    def remove(self) -> None:
        """Remove the text from the figure (for use with live figures)."""
        self.text.remove()
        self.text.set_visible(False)
