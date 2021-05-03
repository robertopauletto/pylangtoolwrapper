# tk_tooltips.py

import tkinter as tk
from time import sleep

class Tooltip:
    """
    A popup message useful to the user when entering a specific widget

    Use the function `show_tooltip` to actually show the tooltip
    """
    def __init__(self, widget, **kwargs):
        """
        allowed key parameters:

        - background = background color hex code (default #ffffff)
        - color = foreground color hex code (default #005157)
        - border = popup border thickness (default 1)

        :param widget: the widget to apply the tooltip
        """
        self._widget = widget
        self._tip_win = None
        self._bgcolor = kwargs.get('background', "#ffffff")
        self._forecolor = kwargs.get('foreground', '#005157')
        self._border = kwargs.get('border', 1)

    def show(self, msg: str) -> None:
        """
        Shows a popup message on mouseover
        """
        if self._tip_win or not msg:
            return

        x, y, _, cy = self._widget.bbox('insert')
        x = x + self._widget.winfo_rootx() + 25
        y = y + cy + self._widget.winfo_rooty() + 25
        self._tip_win = tw = tk.Toplevel(self._widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(tw, text=msg, justify=tk.LEFT,
                 background=self._bgcolor, foreground=self._forecolor,
                 relief=tk.SOLID,
                 borderwidth=self._border).grid()

    def hide(self):
        """Hide popup when widget losees focus"""
        tw = self._tip_win
        self._tip_win = None
        if tw:
            tw.destroy()


def show_tooltip(widget, msg: str, **kwargs):
    """
    Shows a tooltip message on `widget`

    allowed key parameters:

    - background = background color hex code (default #ffffff)
    - color = foreground color hex code (default #005157)
    - border = popup border thickness (default 1)

    :param widget: widget to apply tooltip
    :param msg: tooltip message
    :return:
    """
    tooltip = Tooltip(widget, **kwargs)

    def enter(event):
        """show tooltip on mouseover"""
        tooltip.show(msg)

    def leave(event):
        """hide tooltip when focus is losed"""
        tooltip.hide()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


__doc__ = "tk_tooltips"

if __name__ == '__main__':
    pass
