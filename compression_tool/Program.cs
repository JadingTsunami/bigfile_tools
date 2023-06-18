using System;
using System.IO;
using System.IO.Compression;

public static class BigFileCompression
{
    private const string CompressedFileName = "bigfile";
    private const string ReCompressedFileName = "bigfile.recomp";
    private const string ModFileName = "bigfile.mod";
    private const string DecompressedFileName = "bigfile.decomp";

    public static void Main()
    {
        if (File.Exists(ModFileName)) {
            CompressFile();
            Console.WriteLine($"Created compressed file '{ReCompressedFileName}'.");
        }
        if (!File.Exists(DecompressedFileName)) {
            DecompressFile();
            Console.WriteLine($"Decompressed file '{DecompressedFileName}'.");
        }
    }

    private static void CompressFile()
    {
        using FileStream modFileStream = File.Open(ModFileName, FileMode.Open);
        using FileStream compressedFileStream = File.Create(ReCompressedFileName);
        using var compressor = new DeflateStream(compressedFileStream, CompressionMode.Compress);
        modFileStream.CopyTo(compressor);
    }

    private static void DecompressFile()
    {
        using FileStream compressedFileStream = File.Open(CompressedFileName, FileMode.Open);
        using FileStream outputFileStream = File.Create(DecompressedFileName);
        using var decompressor = new DeflateStream(compressedFileStream, CompressionMode.Decompress);
        decompressor.CopyTo(outputFileStream);
    }
}
