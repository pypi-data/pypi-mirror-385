from __future__ import annotations

from typing import Optional
import uuid
from lightningchart.series import FigureSeries, Series, SeriesWithClear, SeriesWithDrawOrder
from lightningchart.ui.axis import Axis
from lightningchart.utils import convert_to_dict, convert_color_to_hex
from lightningchart.utils.utils import LegendOptions, build_series_legend_options


class PolygonSeries(SeriesWithClear, SeriesWithDrawOrder, Series, FigureSeries):
    """Series for visualizing polygons in a 2D space."""

    def __init__(
        self,
        chart,        
        automatic_color_index: int = None,
        axis_x: Axis = None,
        axis_y: Axis = None, 
        legend: Optional[LegendOptions] = None
    ):
        Series.__init__(self, chart)

        legend_options = build_series_legend_options(legend)

        self.instance.send(
            self.id,
            'addPolygonSeries',
            {
                'chart': self.chart.id,
                'automaticColorIndex': automatic_color_index,
                'axisX': axis_x,
                'axisY': axis_y,
                'legend': legend_options if legend_options else None
            },
        )

    def add(self, points: list[dict]):
        """Add new figure to the series.

        Args:
            points: Dimensions that figure must represent

        Returns:
            The instance of the class for fluent interface.
        """
        points = convert_to_dict(points)

        polygon_figure = PolygonFigure(self, points)
        return polygon_figure

    def set_auto_scrolling_enabled(self, enabled: bool):
        """Set whether series is taken into account with automatic scrolling and fitting of attached axes.

        Args:
            enabled: Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setAutoScrollingEnabled', {'enabled': enabled})
        return self


class PolygonFigure:
    """Class representing a visual polygon figure in the PolygonSeries."""

    def __init__(self, series: PolygonSeries, points: list[dict]):
        self.series = series
        self.points = points
        self.instance = series.instance
        self.id = str(uuid.uuid4())
        self.instance.send(self.id, 'addPolygonFigure', {'series': self.series.id, 'points': points})

    def set_stroke(self, thickness: int | float, color: any = None):
        """Set Stroke style of the polygon.

        Args:
            thickness (int | float): Thickness of the stroke.
            color (Color): Color of the stroke.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(
            self.id,
            'setStrokeStyle',
            {'thickness': thickness, 'color': color},
        )
        return self

    def set_dimensions(self, points: list[dict]):
        """Set new dimensions for figure.

        Args:
            points: List of polygon coordinates

        Returns:
            The instance of the class for fluent interface.
        """
        points = convert_to_dict(points)

        self.instance.send(self.id, 'setDimensionsPolygon', {'points': points})
        return self

    def set_visible(self, visible: bool):
        """Set element visibility.

        Args:
            visible: Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setVisible', {'visible': visible})
        return self

    def set_color(self, color: any):
        """Set a color of the polygon.

        Args:
            color (Color): Color of the band.

        Returns:
            The instance of the class for fluent interface.
        """
        color = convert_color_to_hex(color) if color is not None else None

        self.instance.send(self.id, 'setSolidFillStyle', {'color': color})
        return self
