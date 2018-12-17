# gui.py

from configparser import ConfigParser
import codecs
import os
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename
from tkinter.messagebox import askyesno, askquestion
from tkinter.messagebox import showinfo, showerror, showwarning
import tkinter.ttk as ttk
import pylangtoolwrapper as pylt
import entities


DEV_MODE = True
ini = ConfigParser()
ini.read('gui/config.ini')
section = 'windows' if os.name == 'nt' else 'unix'
geometry = ini.get(section, 'geometry')
statusbar_len = ini.get(section, 'statusbar')
languages = pylt.get_languages()


def set_style():
    style = ttk.Style()
    style.configure('TEntry', disabledforeground='#FFF9D8')


class StatusBar(tk.Frame):
    """Represents a status bar"""
    def __init__(self, master, msg, width=None):
        """

        :param master: parent widget
        :param msg: messaggio to show at instance creation
        :param width:
        """
        tk.Frame.__init__(self, master)
        self._msg = tk.StringVar(value=msg)
        self._lbl = tk.Label(self, bd=1, relief=tk.SUNKEN, padx=5, pady=5,
                             textvariable=self._msg)
        if width:
            self._lbl.configure(width=width)
        self._lbl.grid(sticky=tk.EW)

    @property
    def message(self):
        """Gets the message"""
        return self._msg

    @message.setter
    def message(self, msg):
        """Sets the message """
        self._msg.set(msg)


class GUI:
    """User Interface"""
    def __init__(self, root, title, geometry, resizable=(False, False)):
        self._current_tag = {"start": -1, 'end': -1, 'name': None}
        self.errors = list()
        self._navpos = 0
        self._language = tk.StringVar()
        self.root = root
        isinstance(self.root, tk.Tk)
        self.root.title(title)
        self.root.geometry(geometry)
        self.root.resizable(*resizable)
        self._draw()

    def _draw(self):
        """Draws the user interface"""
        self._mf = tk.Frame(self.root)
        self._draw_parse()
        self._draw_errors()
        self._draw_navbuttons()
        self._sb = StatusBar(self._mf, 'Ready ...', statusbar_len)
        self._sb.grid(
            row=99, column=0, padx=5, pady=5, sticky=tk.EW, columnspan=3
        )

        self._mf.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)

    def _draw_parse(self):
        fm = ttk.LabelFrame(self._mf, text=' Text to parse ')

        # Text container and scrollbar
        self._text = tk.Text(fm, width=80, height=20)

        # Tag settings for error text highlighting
        self._text.tag_configure("error", background="yellow")
        self._text.tag_configure("warn", background="#FFA97E")

        self._text.grid(row=0, column=0, padx=5, pady=5, rowspan=7)
        scrollbar = tk.Scrollbar(fm)
        scrollbar.grid(row=0, column=1, sticky=tk.NS, rowspan=7, padx=5)
        scrollbar.config(command=self._text.yview)
        self._text.configure(yscrollcommand=scrollbar.set)

        # Buttons
        tk.Label(
            fm, text='Languages'
        ).grid(row=0, column=2, padx=5, pady=0, ipady=0)
        cmb_lang = ttk.Combobox(fm, textvariable=self._language, width=10)
        cmb_lang['values'] = [lang.name for lang in languages]
        cmb_lang.grid(row=1, column=2, padx=0, pady=5, ipady=0)

        tk.Button(
           fm, text='Paste text', width=10, command=self._paste
        ).grid(row=2, column=2, padx=5, pady=5)
        tk.Button(
            fm, text='Load from file', width=10, command=self._load
        ).grid(row=3, column=2, padx=5, pady=5)
        tk.Button(
            fm, text='Parse', width=10, command=self._parse
        ).grid(row=4, column=2, padx=5, pady=5)
        tk.Button(
            fm, text='Clean', width=10,
            command=lambda: self._empty_text(self._text)
        ).grid(row=5, column=2, padx=5, pady=5)
        tk.Button(
            fm, text='Copy text', width=10, command=self._parse
        ).grid(row=6, column=2, padx=5, pady=5)

        fm.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)

    def _draw_errors(self):
        fm = ttk.LabelFrame(self._mf, text=' Error details ')

        # Error container
        self._errors = tk.Text(fm, width=80, height=8)
        self._errors.grid(row=0, column=0, padx=5, pady=5,
                          rowspan=4, columnspan=2)

        fm.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NSEW)

    def _draw_navbuttons(self):
        fm = tk.LabelFrame(self._mf, text='')
        tk.Button(
            fm, text='<<', width=3,
            command=lambda: self._error_nav(self.errors, 'f', self._show_error)
        ).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(
            fm, text='<', width=3,
            command=lambda: self._error_nav(self.errors, 'p', self._show_error)
        ).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(
            fm, text='>', width=3,
            command=lambda: self._error_nav(self.errors, 'n', self._show_error)
        ).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(
            fm, text='>>', width=3,
            command=lambda: self._error_nav(self.errors, 'l', self._show_error)
        ).grid(row=0, column=3, padx=5, pady=5)
        fm.grid(row=2, column=0, padx=5, pady=5, sticky=tk.EW)

    def _error_nav(self, items: list, action: str, callback):
        """

        :param items:
        :param action: **f**irst/**l**ast/**n**ext/**p**revious
        :return: the list item requested
        """
        if action not in 'flnp':
            return
        if not items:
            return
        if action == 'n':
            if self._navpos+1 == len(items):
                self._navpos = 0
            else:
                self._navpos += 1
        elif action == 'p':
            if self._navpos-1 < 0:
                self._navpos = len(items)-1
            else:
                self._navpos -= 1
        elif action == 'f':
            self._navpos = 0
        elif action == 'l':
            self._navpos = len(items) - 1
        callback(items[self._navpos])

    def _show_error(self, item):
        assert isinstance(item, entities.Error)
        self._empty_text(self._errors)
        prompt = list()
        prompt.append(f'Message: {item.message}')
        prompt.append(f'Word: {item.text_error}')
        prompt.append(f'In text: {item.context.proximity}')
        if item.suggestions:
            prompt.append(f"Suggestions: {'/'.join(item.suggestions)}")
        self._errors.insert(tk.END, '\n'.join(prompt))
        self._sb.message = f'Error {self._navpos+1} of {len(self.errors)}'\
                           f' ({item.rule.category_name}) '
        self._hl(item)

    def _empty_text(self, widget):
        """Empty the text frame"""
        widget.delete(1.0, tk.END)

    def _paste(self):
        if not askyesno(parent=self._text,
                        message="This will clear existing text, continue?",
                        title="Confirmation"):
            return
        self._empty_text(self._text)
        self._text.insert(1.0, self.root.clipboard_get())

    def _parse(self):
        if self._text.get(1.0, tk.END) == '\n':
            return
        self.errors = pylt.check(self._text.get(1.0, tk.END), 'it')
        if not self.errors:
            self._sb.message = 'All good!'
        self._error_nav(self.errors, 'f', self._show_error)

    def _load(self):
        """Load text to parse from file"""
        if not askyesno(parent=self._text,
                        message="This will clear existing text, continue?",
                        title="Confirmation"):
            return
        self._empty_text(self._text)
        if DEV_MODE:
            self._text.insert(
                1.0, codecs.open('test.txt', encoding='utf-8').read())
        else:
            fn = askopenfilename(parent=self.root)
            if not fn:
                return
            with codecs.open(fn, encoding='utf-8') as fh:
                self._text.insert(1.0, fh.read())

    def _hl(self, error):
        """
        Highlight the current error
        :param error: `Error`
        :return:
        """
        text = self._text.get(1.0, tk.END)
        word = error.text_error
        start, end, length = error.absolute_position()
        w = text[start:end]
        if self._current_tag['name'] is not None:
            self._text.tag_remove(
                self._current_tag['name'],
                f"1.0 + {self._current_tag['start']}c",
                f"1.0 + {self._current_tag['end']}c"
            )
        ruletype = self._set_tag(error)
        self._text.tag_add(
            ruletype, f'1.0 + {start}c', f'1.0 + {end}c'
        )
        self._current_tag['name'] = ruletype
        self._current_tag['start'] = start
        self._current_tag['end'] = end
        if DEV_MODE:
            print(w)

    def _get_tag(self, error):
        if error.rule.type == "misspelling":
            return "error"
        else:
            return "warn"


if __name__ == '__main__':
    root = tk.Tk()
    set_style()
    gui = GUI(root, 'Spell Checker', geometry)
    root.update_idletasks()
    root.mainloop()
