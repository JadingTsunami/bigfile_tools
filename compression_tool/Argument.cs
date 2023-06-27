using System;
using System.Collections.Generic;

namespace BigFileTools
{
    class Argument
    {
        static public Argument Null = new Argument(false); 

        public bool Exist { get; }
        public List<string> Parameters { get; } = new List<string>();
          
        public Argument(bool exist)
        {
            Exist = exist;
        }
        public Argument(List<string> parameters) : this(parameters.Count > 0)
        {
            Parameters = parameters;
        }
    }
}
