using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ChatbotLibrary
{
    public class MovieLine
    {
        private int lineID;
        private string line;

        public int LineID
        {
            get { return lineID; }
            set { lineID = value; }
        }

        public string Line
        {
            get { return line; }
            set { line = value; }
        }
    }
}
