## LanguageTool API REST wrapper - 0.1

Simple python wrapper to the api, useful if you need some spell check.
The JSON data returned by the api are managed by classes.

### Library Usage

- `check(text, lang_code)` will return a list of `Error` objects 
- `get_languages()` will get the languages supported by [LanguageTool](https://languagetool.org/)

### Interfaces

There is a simple Tkinter GUI implementation in the `gui` folder
