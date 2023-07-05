# bigfile_tools

Various tools for dealing with the SoR4 bigfile

## !! WARNING !!

**This program does not provide guardrails! You can easily break your game's data and cause it to crash on start-up. Always back up all files and ALL GAME DATA before editing or replacing any files. Use at your own risk!**

 **BACK UP ALL YOUR DATA BEFORE MAKING ANY CHANGES!!**

## BASIC INSTRUCTIONS

**!! IMPORTANT !!**

Run `pip install bbpb` to install the python3 `blackboxprotobuf` module. **Do NOT** run pip install blackboxprotobuf! This will install an incorrect version and you will need to uninstall that version in order for the library to function correctly.

1. Clone this repo.
2. Copy your game `bigfile` to a working area of your choice.
    * Make a backup of your game's `bigfile` just in case!
3. Load your `bigfile` into the editor and edit.

# Tool Summary

## bigfile_editor

Edits the content of a bigfile. Very WIP.

* Imports and exports game-ready **compressed** bigfiles.
* Imports and exports **uncompressed** bigfiles which load/save faster and can be manually edited in a hex editor.

After import, the game data tables appear on the left side of the GUI. Expand the tree and select a table to show its data as a tree structure on the right side panels. Double-click entries to edit them.

Only a small amount of game data is annotated at this time, but if the data in a table is believed to be understood, a description will show in the "Meaning" column. More can be added, so if you discover the purpose of a field, feel free to suggest updates.

* **WARNING!!** Editing game data can be unpredictable. The tool uses a "best guess" about the game data, which may or may not result in game crashes, data corruption or loss, and so on. **BACK UP ALL YOUR DATA BEFORE MAKING ANY CHANGES!!**

## compression_tool

`dotnet run --project compression_tool`

Compresses/decompresses a `bigfile`.

If `bigfile.decomp` does not exist in the current working directory, `bigfile` is decompressed into `bigfile.decomp`.

If `bigfile.mod` exists, it is re-compressed as `bigfile.recomp`.

The basic workflow is:

1. Decompress your bigfile (bigfile &rarr; bigfile.decomp)
2. Copy it to bigfile.mod and modify it as needed.
3. Recompress your bigfile (bigfile.mod &rarr; bigfile.recomp)
4. Replace your game bigfile with bigfile.recomp.
    * Make sure to back up your original bigfile first.

# License

SoR4 Bigfile Tools

Copyright (C) 2023 JadingTsunami

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; If not, see <http://www.gnu.org/licenses/>.
