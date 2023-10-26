using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ChatbotLibrary
{
    public class MovieLineComparer : IComparer<MovieLine>
    {
        public int Compare(MovieLine item1, MovieLine item2)
        {
            return item1.LineID.CompareTo(item2.LineID);
        }
    }
}
