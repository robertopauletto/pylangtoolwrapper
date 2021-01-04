# gui.py


from configparser import ConfigParser
import codecs
import os
import sys
sys.path.append('..')
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename, asksaveasfilename
from tkinter.messagebox import askyesno, askquestion
from tkinter.messagebox import showinfo, showerror, showwarning
import tkinter.ttk as ttk
from typing import Tuple, List

import pylangtoolwrapper as pylt
import entities
from tk_tooltips import show_tooltip


__version__ = '0.2'
DEV_MODE = False
ini = ConfigParser()
gui_folder = os.path.dirname(os.path.abspath(__file__))
ini.read(os.path.join(gui_folder, 'config.ini'))
section = 'windows' if os.name == 'nt' else 'unix'
geometry = ini.get(section, 'geometry')
statusbar_len = ini.get(section, 'statusbar')


def get_languages() -> list:
    """
    Retrieve available languages from LangToolWrapper
    If operation fails, append the default language to the return list
    :return: list of `pylt.Languages`
    """
    try:
        languages = pylt.get_languages()
    except:
        languages = list()
    else:
        lng = ini.get('language', 'default')
        languages.append(pylt.Language(lng, lng, lng))
        return languages


def get_whitelist() -> list:
    """
    Load a list of words. If an error matches a word in this list it will be
    marked as whitelisted, which can then be ignored if the user activate the
    corresponding option
    :return:
    """
    fn = ini.get('paths', 'whitelist')
    if "\\" not in fn or "/" not in fn:  # file in the same directory of gui
        fn = os.path.join(gui_folder, fn)
    with open(fn) as fh:
        return [word.lower() for word in fh.read().split('\n') if word]


def save_whitelist(words: list, outfile: str, overwrite: bool = True):
    """
    Saves `words` to `outfile`
    :param words: list of words whitelisted
    :param outfile: target storage file
    :param overwrite: if `outfile`, if exists, will be overwritten
    :return:
    """
    mode = "w" if overwrite else "a"
    if "\\" not in outfile or "/" not in outfile:
        fn = os.path.join(gui_folder, outfile)
    with open(outfile, mode=mode) as fh:
        fh.write('\n'.join(word.lower().strip() for word in words))


def set_style():
    """Set a tkinter gui style"""
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


class Gui:
    """User Interface"""
    def __init__(self, root: tk.Tk, title: str,
                 geometry: str, resizable: Tuple[bool, bool] = (False, False)):
        self._current_tag = {"start": -1, 'end': -1, 'name': None}
        self._last_opened_file = None
        self.errors = list()
        self._errors_original = list()
        self._navpos = 0
        self._goto = 0
        self._language = tk.StringVar()
        self._ignore_whitelisted = tk.IntVar(
            value=ini.getint('userpref', 'ignore_whitelisted')
        )
        self._wlauto = tk.IntVar(
            value=ini.getint('userpref', 'autosave_whitelisted')
        )
        self._missplells_only = tk.IntVar(
            value=ini.getint('userpref', 'misspells_only')
        )
        self.root = root
        isinstance(self.root, tk.Tk)
        self.root.title(title)
        self.root.geometry(geometry)
        self.root.resizable(*resizable)
        self._draw()
        if len(languages) <= 1:
            self._warn_languages()
        self._whitelist = get_whitelist()

    def _warn_languages(self):
        prompt = "Unable to retrieve available languages from source\n"
        "You may want to check the Internet connection or "
        "maybe retry later."
        if len(languages) == 1:
            prompt += '\nThe default language from configuration has been set'
        showwarning(message=prompt, title='Languages')

    def _draw(self):
        """Draws the user interface"""
        self._mf = tk.Frame(self.root)
        self._draw_parse()
        self._draw_commands()
        self._draw_errors()
        self._draw_whitelist()
        self._draw_navbuttons()
        self._sb = StatusBar(self._mf, 'Ready ...', statusbar_len)
        self._sb.grid(
            row=99, column=0, padx=5, pady=5, sticky=tk.EW, columnspan=3
        )

        self._mf.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)

    def _draw_parse(self):
        """Draws the frame where goes the text to check and the command"""
        fm = ttk.LabelFrame(self._mf, text=' Spellcheck Text ')
        # Text container and scrollbar
        self._text = tk.Text(fm, width=80, height=20)

        # Tag settings for error text highlighting
        self._text.tag_configure("error", background="yellow")
        self._text.tag_configure("warn", background="#FFA97E")
        self._text.tag_configure("whitelisted", background="#1BFCDA")

        # Scrollbar for the text to check part
        self._text.grid(row=0, column=0, padx=5, pady=5, rowspan=7)
        scrollbar = tk.Scrollbar(fm)
        scrollbar.grid(row=0, column=1, sticky=tk.NS, rowspan=7)
        scrollbar.config(command=self._text.yview)
        self._text.configure(yscrollcommand=scrollbar.set)
        fm.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)

    def _draw_commands(self):
        # Commands
        fmcmd = ttk.LabelFrame(self._mf, text=' Commands ')
        tk.Label(
            fmcmd, text='Languages'
        ).grid(row=0, column=0, padx=5, pady=0, ipady=0)
        cmb_lang = ttk.Combobox(fmcmd, textvariable=self._language, width=10)
        cmb_lang['values'] = [lang.name for lang in languages]
        lng = ini.get('language', 'default')
        tmplng = [item.code for item in languages]
        default_lang = tmplng.index(lng) if lng else -1
        cmb_lang.current(default_lang)
        cmb_lang.grid(row=1, column=0, padx=0, pady=5, ipady=0)

        bt1 = tk.Button(
           fmcmd, text='Paste text', width=10, command=self._paste
        )
        bt1.grid(row=2, column=0, padx=5, pady=5)

        bt2 = tk.Button(
            fmcmd, text='Load from file', width=10, command=self._load
        )
        bt2.grid(row=3, column=0, padx=5, pady=5)

        bt3 = tk.Button(
            fmcmd, text='Parse', width=10, command=self._parse
        )
        bt3.grid(row=4, column=0, padx=5, pady=5)

        bt4 = tk.Button(
            fmcmd, text='Clear', width=10,
            command=lambda: self._empty_text(self._text)
        )
        bt4.grid(row=5, column=0, padx=5, pady=5)

        bt5 = tk.Button(
            fmcmd, text='Copy text', width=10, command=self._parse
        )
        bt5.grid(row=6, column=0, padx=5, pady=5)

        bt6 = tk.Button(
            fmcmd, text='Save to file', width=10, command=self._save
        )
        bt6.grid(row=7, column=0, padx=5, pady=5)
        fmcmd.grid(row=0, column=1, padx=5, pady=5, sticky=tk.NSEW)

        self._setup_tooltips(
            [
                (bt1, "Paste text from the current clipboard"),
                (bt2, "Load the contents of a file"),
                (bt3, "Perform check spelling with text area contents"),
                (bt4, "Clear text area"),
                (bt5, "Copy text area content to clipboard"),
                (bt6, 'Save text area content to file')
            ]
        )

    def _setup_tooltips(self, items: List[tuple]):
        for widget, message in items:
            show_tooltip(widget, message)

    def _draw_whitelist(self):
        fm = ttk.LabelFrame(self._mf, text=' Whitelist ')
        bt1 = tk.Button(
            fm, text='Add', width=10, command=self._addword
        )
        bt1.grid(row=0, column=0, padx=5, pady=5)

        ck1 = tk.Checkbutton(
            fm, text='Autosave', variable=self._wlauto
        )
        ck1.grid(row=1, column=0, padx=5, pady=5)

        bt2 = tk.Button(
            fm, text='Save', width=10, command=self._parse
        )
        bt2.grid(row=2, column=0, padx=5, pady=5)

        bt3 = tk.Button(
            fm, text='Edit', width=10,
            command=lambda: showinfo("Unavailable feature", "Not implemented")
        )
        bt3.grid(row=3, column=0, padx=5, pady=5)
        fm.grid(row=1, column=1, padx=5, pady=5, sticky=tk.NSEW)

        self._setup_tooltips([
            (bt1, 'Add selected word to whitelist'),
            (ck1, 'If selected save the words added to the whitelist on exit'),
            (bt2, 'Save the whitelist'),
            (bt3, 'Edit the whitelist')
        ])

    def _draw_errors(self):
        fm = ttk.LabelFrame(self._mf, text=' Error details ')

        # Error container
        self._errors = tk.Text(fm, width=80, height=8)
        self._errors.grid(row=0, column=0, padx=5, pady=5,
                          rowspan=4, columnspan=2)

        fm.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NSEW)

    def _draw_navbuttons(self):
        fm = tk.LabelFrame(self._mf, text='')
        bt1 = tk.Button(
            fm, text='<<', width=3,
            command=lambda: self._error_nav(self.errors, 'f', self._show_error)
        )
        bt1.grid(row=0, column=0, padx=5, pady=5)

        bt2 = tk.Button(
            fm, text='<', width=3,
            command=lambda: self._error_nav(self.errors, 'p', self._show_error)
        )
        bt2.grid(row=0, column=1, padx=5, pady=5)

        txt1 = tk.Entry(
            fm, textvariable=self._goto, width=4
        )
        txt1.grid(row=0, column=2, padx=5, pady=5)

        bt3 = tk.Button(
            fm, text='>', width=3,
            command=lambda: self._error_nav(self.errors, 'n', self._show_error)
        )
        bt3.grid(row=0, column=3, padx=5, pady=5)

        bt4 = tk.Button(
            fm, text='>>', width=3,
            command=lambda: self._error_nav(self.errors, 'l', self._show_error)
        )
        bt4.grid(row=0, column=4, padx=5, pady=5)

        ck1 = tk.Checkbutton(
            fm, text='Ignore whitelisted', variable=self._ignore_whitelisted,
        )
        ck1.grid(row=0, column=5, padx=5, pady=5, ipadx=30)

        ck2 = tk.Checkbutton(
            fm, text='Missplelling only', variable=self._missplells_only
        )
        ck2.grid(row=0, column=6, padx=5, pady=5, ipadx=30)

        fm.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        self._setup_tooltips([
            (bt1, 'Go to first error'),
            (bt2, 'Go to previous error'),
            (txt1, 'Go to nth error'),
            (bt3, 'Go to next error'),
            (bt4, 'Go to last error'),
            (ck1, 'If checked ignore whitelisted words on spellchecking'),
            (ck2, 'If checked does not show grammar errors')
        ])

    def _error_nav(self, items: list, action: str, callback):
        """
        Buttons for error list navigation
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

    def _error_goto(self, items, pos, callback):
        if pos < 1 or pos > len(items):
            showinfo(message=f'{pos} invalid')
            return
        self._navpos = pos-1
        callback(items[self._navpos])

    def _show_error(self, error):
        """
        Show selected error
        :param error:
        """
        assert isinstance(error, entities.Error)
        self._empty_text(self._errors)
        prompt = list()
        prompt.append(f'Message: {error.message}')
        prompt.append(f'Word: {error.text_error}')
        prompt.append(f'In text: {error.context.proximity}')
        if error.suggestions:
            prompt.append(f"Suggestions: {'/'.join(error.suggestions)}")
        self._errors.insert(tk.END, '\n'.join(prompt))
        self._sb.message = f'Error {self._navpos+1} of {len(self.errors)}'\
                           f' ({error.rule.category_name}) '
        start = self._hl(error)
        # let's move the cursor to the error position
        self._text.mark_set("insert", f'1.0 + {start + 1}c')
        self._text.see("insert")

    def _empty_text(self, widget):
        """Empties the text frame"""
        widget.delete(1.0, tk.END)

    def _paste(self):
        """Paste clipboard text into the text to check frame"""
        if not askyesno(parent=self._text,
                        message="This will clear existing text, continue?",
                        title="Confirmation"):
            return
        self._empty_text(self._text)
        self._text.insert(1.0, self.root.clipboard_get())

    def _parse(self):
        """Parse the text for errors in spelling and grammar"""
        if not self._language.get():
            showwarning("Language selection",
                        "You need to select a language first")
            return
        lang = [lng.code for lng in languages
                if lng.name == self._language.get()][0]
        if self._text.get(1.0, tk.END) == '\n':
            return
        self._spellcheck(self._text.get(1.0, tk.END), lang, self._whitelist)
        if not self.errors:
            self._sb.message = 'All good!'
        if self._ignore_whitelisted.get() == 1:
            self.errors = pylt.Error.whitelist_filtered(self.errors)
        if self._missplells_only.get() == 1:
            self.errors = pylt.Error.spell_errors(self.errors)
        self._error_nav(self.errors, 'f', self._show_error)

    def _ask_to_empty_text_buffer(self) -> bool:
        """
        If the text buffer is not empty asks for confirmation to clear buffer
        """
        buffer = self._text.get('1.0', tk.END).strip()
        if buffer:
            return askyesno(parent=self._text,
                            message="This will clear existing text, continue?",
                            title="Empty text widget")
        return True

    def _ask_to_overwrite(self, save_file: str) -> True:
        if not os.path.exists(save_file):
            return True
        prompt = f'{save_file}\nalready exists, are you sure to overwrite?'
        return askyesno('Overwrite file', prompt)

    def _save(self):
        """Save parsed text to file"""
        # get the folder of the previous opened file
        initdir = (os.path.dirname(self._last_opened_file)
                   if self._last_opened_file else '.')
        save_file = askopenfilename(
            initialdir=initdir,
            title='Select the file name for the parsed text'
        )
        if not save_file:
            return
        try:
            if not self._ask_to_overwrite(save_file):
                return
            with open(save_file, mode='w') as fh:
                fh.write(self._text.get('1.0', tk.END))
            showinfo('Save to file', f'Buffer saved to\n{save_file}')
        except IOError as ioerrex:
            prompt = f"An error occurred while saving to {save_file}\n{ioerrex}"
            showerror("Save file", prompt)
        finally:
            return

    def _ask_to_parse(self):
        prompt = ("Do you want to parse the loaded file?\n"
                  "Otherwise you will have to do it manually with the"
                  "'Parse' button")
        return askyesno("Parse opened file", prompt)

    def _load(self):
        """Load text to parse from file"""
        if not self._ask_to_empty_text_buffer():
            return
        self._empty_text(self._text)
        if DEV_MODE:
            self._text.insert(
                1.0,
                codecs.open(
                    os.path.join(gui_folder, 'test.txt'),
                    encoding='utf-8'
                ).read())
        else:
            fn = askopenfilename(parent=self.root)
            if not fn:
                return
            # Save last opened file, will be useful if the user want to
            # save back the parsed text, by default will be offered the folder
            # of the opened file
            # self._last_opened_file = fn
            with codecs.open(fn, encoding='utf-8') as fh:
                self._text.insert(1.0, fh.read())
            if self._ask_to_parse():
                self._parse()

    def _hl(self, error) -> int:
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
        ruletype = self._get_tag(error)
        self._text.tag_add(
            ruletype, f'1.0 + {start}c', f'1.0 + {end}c'
        )
        self._current_tag['name'] = ruletype
        self._current_tag['start'] = start
        self._current_tag['end'] = end
        if DEV_MODE:
            print(w)
        return start

    def _get_tag(self, error):
        """
        Get the error type category for display purposes
        :param error:
        :return:
        """
        if error.is_whitelisted:
            return "whitelisted"
        if error.rule.type == "misspelling":
            return "error"
        else:
            return "warn"

    def _addword(self):
        word = self.errors[self._navpos].text_error.strip().lower()
        if word in self._whitelist:
            showinfo(title="Manage whitelist",
                     message=f'{word} already whitelisted')
        self._whitelist.append(word)
        prev_pos = self._navpos
        self.errors = pylt.Error.update_whitelisted(
            self.errors, self._whitelist
        )
        if self._ignore_whitelisted.get() == 1:
            self.errors = pylt.Error.whitelist_filtered(self.errors)
        if self._wlauto.get() == 1:
            save_whitelist(self._whitelist, ini.get('paths', 'whitelist'))
        self._errors_original = self.errors[:]

    def _save_wl(self):
        save_whitelist(self._whitelist, ini.get('paths', 'whitelist'))
        showinfo(message=f'{len(self._whitelist)} words in whitelist')

    def _spellcheck(self, text, lang, whitelist):
        """Call the spellcheck api and populate a list of `pylt.Error`
        objects
        :param text: text to parse
        :param lang: language code
        :param whitelist: list of whitelisted words
        """
        self.errors = pylt.check(
            self._text.get(1.0, tk.END), lang, whitelist
        )
        self._errors_original = self.errors[:]


if __name__ == '__main__':
    languages = get_languages()
    root = tk.Tk()
    set_style()
    gui = Gui(root, f'Spell Checker - version {__version__}', geometry)
    root.update_idletasks()
    root.mainloop()
