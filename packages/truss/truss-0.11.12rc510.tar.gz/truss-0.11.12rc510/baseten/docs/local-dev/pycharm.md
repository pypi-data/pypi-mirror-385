# Pycharm

To make sure this document is up to date refer to the official black/pycharm doc: https://black.readthedocs.io/en/stable/integrations/editors.html#pycharm-intellij-idea


## Setup Black auto code formatter

Path to black: `$PyInterpreterDirectory$/black`. Black is installed into our virtual env and managed by poetry.

1. Open external tools `PyCharm -> Preferences -> Tools -> External Tools`
2. Click the + icon to add a new external tool with the following values:
  - Name: Black
  - Description: Black is the uncompromising Python code formatter.
  - Program: `$PyInterpreterDirectory$/black`
  - Arguments: `"$FilePath$"`
3. Format the currently opened file by selecting Tools -> External Tools -> black.
  - Alternatively, you can set a keyboard shortcut by navigating to Preferences or Settings -> Keymap -> External Tools -> External Tools - Black.
4. Run Black on every file save:
  1. Make sure you have the [File Watchers](https://plugins.jetbrains.com/plugin/7177-file-watchers) plugin installed.
  2. Go to Preferences or Settings -> Tools -> File Watchers and click + to add a new watcher:
    - Name: Black
    - File type: Python
    - Scope: Project Files
    - Program: `$PyInterpreterDirectory$/black`
    - Arguments: `$FilePath$`
    - Output paths to refresh: `$FilePath$`
    - Working directory: `$ProjectFileDir$`
    - In Advanced Options
      - Uncheck “Auto-save edited files to trigger the watcher”
      - Uncheck “Trigger the watcher on external changes”
