# bigfile_tools

Various tools for dealing with the SoR4 bigfile

## !! WARNING !!

**This program does not provide guardrails! You can easily break your game's data and cause it to crash on start-up. Always back up all files and ALL GAME DATA before editing or replacing any files. Use at your own risk!**

 **BACK UP ALL YOUR DATA BEFORE MAKING ANY CHANGES!!**

## SETUP INSTRUCTIONS

**!! IMPORTANT !!**

**Do NOT** run `pip install blackboxprotobuf`!
**Do NOT** run `pip install bbpb`!

Instead, install the wheel [here](https://github.com/JadingTsunami/blackboxprotobuf/releases/tag/initial_release) which is built for bigfile editing.

1. Download the wheel file (`*.whl`)
1. Open a terminal and cd into the folder where you downloaded the wheel
1. Run `pip install name-of-the-file.whl`
    * Example: `pip install bbpb-1.0.0-py2.py3-none-any.whl`


## BASIC INSTRUCTIONS

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

## level_editor

Enables swapping out each enemy, pickup, and/or breakable spawn point in each level.

This is *not* the existing swapper: each spawn point is edited individually.

The stage progression can be modified using the [Swapper](https://sourceforge.net/projects/sor4-character-swapper/) or bigfile editor to create fully custom stages. Just import the modified bigfile into the level editor and perform additional swaps. Note you need to know the internal game name for the enemies you replace using this method. But, most of them are self-explanatory.

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
