using BigFileTools;
using System;
using System.IO;
using System.IO.Compression;
using System.Reflection;

namespace BigFileTools
{
public static class BigFileCompression
{
    public static void Main(string[] arglist)
    {
        var arguments = new ArgumentListParser(arglist);
        if (arguments.Help.Exist || !arguments.IsValid)
        {
            if (!arguments.IsValid)
            {
                Console.WriteLine("Invalid arguments.");
            }
            PrintHelp();
            return;
        }

        var input_path = arguments.Input.Parameters.First();
        if (!File.Exists(input_path))
        {
            Console.WriteLine($"{input_path} does not exist; please provide a valid target.");
            return;
        }

        var output_path = arguments.Output.Parameters.First();
        if (File.Exists(output_path) && !arguments.ForceReplace.Exist)
        {
            Console.WriteLine($"{output_path} already exist; confirm overwrite? (y/n)");
            var decision = Console.ReadLine();
            switch (decision)
            {
                default:
                    Console.WriteLine($"Task aborted; {output_path} already exist.");
                    return;

                case "y":
                    break;
            }
        }

        var task = arguments.Task.Parameters.First();
        switch (task)
        {
            default:
                Console.WriteLine("Invalid task was provided.");
                Console.WriteLine("  Valid tasks are: c for compression, d for decompression");
                return;

            case "c":
                CompressFile(input_path, output_path);
                Console.WriteLine($"Created compressed file '{output_path}'.");
                break;

            case "d":
                DecompressFile(input_path, output_path);
                Console.WriteLine($"Decompressed file '{output_path}'.");
                break;
        }
    }

    private static void CompressFile(string inputPath, string outputPath)
    {
        using FileStream modFileStream = File.Open(inputPath, FileMode.Open);
        using FileStream compressedFileStream = File.Create(outputPath);
        using var compressor = new DeflateStream(compressedFileStream, CompressionMode.Compress);
        modFileStream.CopyTo(compressor);
    }

    private static void DecompressFile(string inputPath, string outputPath)
    {
        using FileStream compressedFileStream = File.Open(inputPath, FileMode.Open);
        using FileStream outputFileStream = File.Create(outputPath);
        using var decompressor = new DeflateStream(compressedFileStream, CompressionMode.Decompress);
        decompressor.CopyTo(outputFileStream);
    }

    private static void PrintHelp()
    {
        Console.WriteLine("The following commands exist:");
        Console.WriteLine("  -h, --help\t\tShows this help message.");
        Console.WriteLine("  -t, --task\t\tThe task to execute on the input file.");
        Console.WriteLine("    Valid tasks are: c for compression, d for decompression");
        Console.WriteLine("  -i, --input\t\tThe path to the input file.");
        Console.WriteLine("  -o, --output\t\tThe path to the output file.");
        Console.WriteLine("  -f, --force-replace\tForce the output file to be replaced even if it already exist.");
        Console.WriteLine();
        Console.WriteLine("Examples:");
        Console.WriteLine($"Decompress a bigfile: -t d -i \"bigfile\" -o \"bigfile.decomp\"");
        Console.WriteLine($"Compress a bigfile: -t c -i \"bigfile.decomp\" -o \"bigfile.recomp\"");
    }
}
}
