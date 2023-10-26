using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using ChatbotLibrary;

namespace ChatbotLibrary
{
    public class RawDataSet
    {
        private List<MovieLine> movieLineList;
        public RawDataSet()
        {
            movieLineList = new List<MovieLine>();
        }

        public List<MovieLine> MovieLineList
        {
            get { return movieLineList; }
        }

        public void SortOnID()
        {
            movieLineList = movieLineList.OrderByDescending(n => n.LineID).ToList();
            movieLineList.Reverse();
        }
    }
}
