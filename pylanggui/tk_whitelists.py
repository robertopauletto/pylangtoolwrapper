# tk_whitelists.py

import os
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename, asksaveasfilename
from tkinter.messagebox import askyesno, askquestion
from tkinter.messagebox import showinfo, showerror, showwarning
import tkinter.ttk as ttk
from typing import Tuple, List

from tk_tooltips import show_tooltip
from pylanggui.__init__ import get_whitelist, save_whitelist

__doc__ = "Manage whitelist"


class WhiteListManager(tk.Toplevel):

    def __init__(self, master, title: str, geom: str, whitelist_file: str,
                 resizable: Tuple[bool, bool] = (False, False)):
        super().__init__(master=master)
        self.title(title)
        self.geometry(geom)
        self.resizable(*resizable)
        self._wlfile = whitelist_file
        self._draw()

    def _draw(self):
        self.lb_sx: tk.Listbox = self._draw_listbox(self, 0,
                                                    "Whitelist content")
        self.lb_sx.bind(
            '<<ListboxSelect>>',
            lambda x: self._move_selected(self.lb_sx, self.lb_dx))

        for item in self._get_whitelist():
            self.lb_sx.insert(tk.END, item)

        self._draw_commands()

        self.lb_dx: tk.Listbox = self._draw_listbox(self, 2, "Removed words")
        self.lb_dx.bind(
            '<<ListboxSelect>>',
            lambda x: self._move_selected(self.lb_dx, self.lb_sx))

    def _move_selected(self, lb_from: tk.Listbox, lb_to: tk.Listbox):
        for item in lb_from.curselection():
            lb_to.insert(tk.END, lb_from.get(item))
            lb_from.delete(item)

    def _del_selected(self, event):
        pass

    def _draw_commands(self):
        fm = tk.Frame(self)
        bt1 = tk.Button(fm, text=' Save ', command=self._save)
        bt1.grid(row=0, column=0, padx=5, pady=5, sticky=tk.EW)
        show_tooltip(bt1, 'Save current word list')

        fm.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

    def _draw_listbox(self, parent, column: int, title: str,
                      dimensions: tuple = (22, 40)) -> tk.Listbox:
        fm = ttk.LabelFrame(parent, text=f" {title} ")
        width, height = dimensions
        lb = tk.Listbox(fm, width=width, height=height)
        lb.grid(padx=5, pady=5, sticky=tk.NSEW)
        fm.grid(row=0, column=column, padx=5, pady=5, sticky=tk.NSEW)
        return lb

    def _save(self):
        items = self.lb_sx.get(0, tk.END)
        print(items)

    def _get_whitelist(self) -> list:
        with open(self._wlfile) as fh:
            return sorted(word.strip() for word in fh.readlines())
