# bigfile_tools

Various tools for dealing with the SoR4 bigfile

## !! WARNING !!

**This program does not provide guardrails! You can easily break your game's data and cause it to crash on start-up. Always back up all files before replacing them. Use at your own risk!**

## BASIC INSTRUCTIONS

1. Clone this repo.
2. Copy your `bigfile` to a subfolder named `bigdata`.
3. In a terminal, run the compression tool from within the `bigdata` subfolder:
    - `dotnet run --project ../compression_tool`
    - This will decompress your `bigfile` to `bigfile.decomp`
4. Edit the bigfile and save as `bigfile.mod`
    - The bigfile editor tool will do this for you when you click "save"
    - See **important notes** in the editor section.
5. In a terminal, re-run the compression tool from within the `bigdata` subfolder:
    - `dotnet run --project ../compression_tool`
    - This will recompress your `bigfile.mod` to `bigfile.recomp`
6. **BACK UP YOUR GAME'S ORIGINAL BIGFILE**
7. Replace your game bigfile with `bigfile.recomp`
8. Try out your changes in-game!
    - To make additional edits, repeat these steps starting at step 2.

# Tool Summary

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

## bigfile_editor

Edits the content of a bigfile. Very WIP.

Expects you have generated `bigdata/bigfile.decomp` already.

**Important note**: The editor **reads** from `bigfile.decomp` and **writes** to `bigfile.mod` so you can keep your edits and your decompressed bigfile separate. This means if you make some edits, save, exit, then re-launch the editor, it will look like your previous session's changes have disappeared, but they haven't: they are stored in `bigfile.mod`. You can optionally replace your `bigfile.decomp` with your edited `bigfile.mod`. But the expected use model is the step-by-step "loop" at the beginning of this readme where you test your changes in-game in between editing sessions. This would also help you determine if a specific change broke the game, and allow you to more easily "rewind" back and try a different change instead.

