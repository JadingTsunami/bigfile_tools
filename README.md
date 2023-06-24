# bigfile_tools

Various tools for dealing with the SoR4 bigfile

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

## analysis_tool

Analyzes the content of a bigfile. Very WIP.

Expects you have generated `bigdata/bigfile.decomp` already.
