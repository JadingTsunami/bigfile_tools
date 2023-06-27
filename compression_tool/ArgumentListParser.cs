using System;
using System.Collections.Generic;

namespace BigFileTools
{
    class ArgumentListParser
    {
        public Argument Help { get; } = Argument.Null;
        public Argument Task { get; } = Argument.Null;
        public Argument Input { get; } = Argument.Null;
        public Argument Output { get; } = Argument.Null;
        public Argument ForceReplace { get; } = Argument.Null;
        public bool IsValid => Task.Exist && Input.Exist && Output.Exist;

        public ArgumentListParser(string[] arglist)
        {
            for (var i = 0; i < arglist.Length; ++i)
            {
                var arg = arglist[i];
                if (!IsOption(arg))
                {
                    throw new ArgumentException($"{arg} is not an option. Type -h or --help to see what options are available.");
                }

                var parameters = FetchParameterList(arglist, i + 1);
                i += parameters.Count;

                switch (arg)
                {
                    case "-h":
                    case "--help":
                        Help = new Argument(true);
                        break;

                    case "-t":
                    case "--task":
                        Task = new Argument(parameters);
                        break;

                    case "-i":
                    case "--input":
                        Input = new Argument(parameters);
                        break;

                    case "-o":
                    case "--output":
                        Output = new Argument(parameters);
                        break;

                    case "-f":
                    case "--force-replace":
                        ForceReplace = new Argument(true);
                        break;
                }
            }
        }

        private static bool IsOption(string arg)
        {
            return arg.StartsWith("--") ||arg.StartsWith("-");
        }

        private static List<string> FetchParameterList(string[] arglist, int start)
        {
            var parameter_list = new List<string>();

            for (var i = start; i < arglist.Length; ++i)
            {
                var arg = arglist[i];

                if (IsOption(arg))
                {
                    break;
                }

                parameter_list.Add(arg);
            }

            return parameter_list;
        }
    }
}
