## LanguageTool API REST wrapper - 0.1

Simple python wrapper to the api, useful if you need some spell check.
The JSON data returned by the api are managed by classes.

### Usage

- `check(text, lang_code)` will return a list of `Error` objects 
- `get_languages()` will get the languages supported by [LanguageTool](https://languagetool.org/)

