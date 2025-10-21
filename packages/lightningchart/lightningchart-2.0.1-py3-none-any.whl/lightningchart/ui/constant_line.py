from __future__ import annotations
from typing import Optional

from lightningchart.ui import UIElement, UIEWithHighlight, UserInteractions
from lightningchart.series import SeriesWith2DLines, SeriesWithoutCursorEnabel
from lightningchart.utils.utils import LegendOptions, build_series_legend_options


class ConstantLine(UIEWithHighlight, UserInteractions, SeriesWith2DLines, SeriesWithoutCursorEnabel):
    def __init__(self, chart, axis, on_top: bool, legend: Optional[LegendOptions] = None,):
        UIElement.__init__(self, chart)
        legend_options = build_series_legend_options(legend)
        self.instance.send(self.id, 'addConstantLine', {''
        'axis': axis.id, 
        'onTop': on_top,
        'legend': legend_options if legend_options else None
        })

    def set_interaction_move_by_dragging(self, enabled: bool):
        """Enable or disable default interaction of moving constant line by dragging with mouse or touch.

        Args:
            enabled (bool): Boolean flag.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setInteractionMoveByDragging', {'enabled': enabled})
        return self

    def set_value(self, value: int | float):
        """Set value of ConstantLine. This is in values of its owning Axis.

        Args:
            value (int | float): Value on Axis.

        Returns:
            The instance of the class for fluent interface.
        """
        self.instance.send(self.id, 'setValue', {'value': value})
        return self

    def set_user_interactions(self, interactions=...):
        """Configure user interactions from a set of preset options.

        Args:
            interactions (dict or None):
                - `None`: disable all interactions
                - `{}` or no argument: restore default interactions
                - `dict`: configure specific interactions

        Examples:
            # Disable all interactions:
            >>> band.set_user_interactions(None)

            # Restore default interactions:
            >>> band.set_user_interactions()
            >>> band.set_user_interactions({})

            # Move only with Control down:
            >>> chart.set_user_interactions({'move': {'drag': False, 'ctrl': {'drag': True}}})
        """
        return super().set_user_interactions(interactions)
