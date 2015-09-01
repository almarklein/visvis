## Configuring visvis ##

Since version 1.5, visvis can be configured via its `vv.settings` object. All settings can be set from the interpreter using this object, although some settings might require a restart of the interpreter.

The settings are stored in an ssdf file called `.visvis/config.ssdf` in the user directory (The first dot is omitted on Windows). Changing a setting via the `vv.settings` object immediately changes this config file.

Here's a list with the current settings. Note that more settings may be added in the future:
  * preferredBackend - The preferred backend GUI toolkit to use ('qt4', 'wx', 'gtk', 'fltk').
  * preferAlreadyLoadedBackend - Whether visvis should prefer an already imported backend (even if it's not the preferredBackend).
  * volshowPreference - Whether the volshow() function prefers the volshow2() or volshow3() function.
  * figureSize - The initial size for figure windows.
  * defaultFontName - The default font to use. Can be 'mono', 'sans' or 'serif', with 'sans' being the default.
  * defaultRelativeFontSize - The default relativeFontSize of new figures. The relativeFontSize property can be used to scale all text simultenously, as well as increase/decrease the margins available for the text. The default is 1.0.