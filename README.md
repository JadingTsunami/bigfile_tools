# bigfile_tools

Various tools for dealing with the SoR4 bigfile

## !! WARNING !!

**This program does not provide guardrails! You can easily break your game's data and cause it to crash on start-up. Always back up all files before replacing them. Use at your own risk!**

## BASIC INSTRUCTIONS

1. Copy your `bigfile` to a subfolder named `bigdata`.
2. In a terminal, run the compression tool from within the `bigdata` subfolder:
    - `dotnet run --project ../compression_tool`
    - This will decompress your `bigfile` to `bigfile.decomp`
3. Edit the bigfile and save as `bigfile.mod`
4. In a terminal, re-run the compression tool from within the `bigdata` subfolder:
    - `dotnet run --project ../compression_tool`
    - This will recompress your `bigfile.mod` to `bigfile.recomp`
5. **BACK UP YOUR GAME'S ORIGINAL BIGFILE**
6. Replace your game bigfile with `bigfile.recomp`


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
