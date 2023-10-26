using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.Serialization;
using System.Text;
using System.Threading.Tasks;

namespace ChatbotLibrary
{
    [DataContract]
    public class Vocabulary
    {
        private List<WordData> itemList;
        private WordDataComparer comparer;
        public Vocabulary()
        {
            itemList = new List<WordData>();
            comparer = new WordDataComparer();
        }

        public void Build(List<DialogueCorpusItem> corpusItemList)
        {
            foreach (DialogueCorpusItem corpusItem in corpusItemList)
            {
                bool firstAppearenceInSentence = true;
                foreach (string token in corpusItem.TokenList)
                {
                    WordData item = new WordData();
                    item.Word = token;
                    int index = itemList.BinarySearch(item, comparer);
                    if (index < 0)
                    {
                        item.NumberOfSentences = 1;
                        itemList.Insert(~index, item);
                    }
                    else if (firstAppearenceInSentence)
                    {
                        itemList[index].NumberOfSentences += 1;
                        firstAppearenceInSentence = false;
                    }
                }
            }
        }

        public List<WordData> ItemList
        {
            get { return itemList; }
            set { itemList = value; }
        }
    }
}
