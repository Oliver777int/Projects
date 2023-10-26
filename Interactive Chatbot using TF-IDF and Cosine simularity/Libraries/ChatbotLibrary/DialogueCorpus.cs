using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ChatbotLibrary
{
    public class DialogueCorpus
    {
        private const int MAX_WORDS = 15;
        private MovieLineComparer comparer;
        private List<DialogueCorpusItem> itemList;
        private Vocabulary vocabulary;

        public DialogueCorpus()
        {
            itemList = new List<DialogueCorpusItem>();
            comparer = new MovieLineComparer();
            vocabulary = new Vocabulary();
        }

        public void GetConversations(List<string> conversationsDataList)
        {
            // Converts the string of conversation IDs to integers in a list.
            char[] charsToTrim = { '"', 'L' , '[', ']', '\''};
            foreach (string conversationData in conversationsDataList)
            {
                string[] stringIDs = conversationData.Split(' ');
                List<int> conversationIDs = new List<int>();
                foreach (string stringID in stringIDs)
                {
                    conversationIDs.Add(Int32.Parse(stringID.Trim(charsToTrim)));
                }

                // Makes sure to remove the last utterance, since it has no response.
                int count = conversationIDs.Count();
                if (count%2 != 0)
                {
                    count = count - 1;
                }

                // Adds 2 consecutive conversation utterances to each dialogue corpus item (Query + Respone).
                for (int ii = 0; ii < count; ii = ii + 2)
                {
                    DialogueCorpusItem item = new DialogueCorpusItem();
                    item.QueryID = conversationIDs[ii];
                    item.ResponseID = conversationIDs[ii + 1];
                    itemList.Add(item);
                }
            }
        }

        public void Process(RawDataSet rawData)
        {
            // Matches the line-ID to the actual movie line using binary search.
            foreach (DialogueCorpusItem item in itemList)
            {
                MovieLine queryLine = new MovieLine();
                queryLine.LineID = item.QueryID;
                int queryIndex = rawData.MovieLineList.BinarySearch(queryLine, comparer);
                if (queryIndex > 0)
                {
                    item.Query = rawData.MovieLineList[queryIndex].Line;
                }
                else
                {
                    item.Query = string.Empty;   //Zero word Querys.
                }
                MovieLine responseLine = new MovieLine();
                responseLine.LineID = item.ResponseID;
                int responseIndex = rawData.MovieLineList.BinarySearch(responseLine, comparer);
                if (responseIndex > 0)
                {
                    item.Response = rawData.MovieLineList[responseIndex].Line;
                }
                else
                {
                    item.Response = string.Empty;   //Zero word responses.
                }
            }

            // Remove long queries and responses
            int numberOfItems = itemList.Count();
            for (int ii = 0; ii<numberOfItems; ii++)
            {
                if ((itemList[ii].Query.Split(' ').Count() > MAX_WORDS) || (itemList[ii].Response.Split(' ').Count() > MAX_WORDS))
                {
                    itemList.RemoveAt(ii);
                    numberOfItems--;
                }
            }

            Preprocess();
            Tokenize();
            GenerateVocabulary();
            GenerateIndexTokenList();
            ComputeIDFs();
            ComputeTFIDFVectors();
        }

        public void Preprocess()
        {
            foreach (DialogueCorpusItem corpusItem in itemList)
            {
                corpusItem.Clean();
            }
        }

        public void Tokenize()
        {
            foreach (DialogueCorpusItem corpusItem in itemList)
            {
                corpusItem.Tokenize();
            }
        }

        public void GenerateVocabulary()
        {
            vocabulary.Build(itemList);
        }

        public void GenerateIndexTokenList()
        {
            foreach (DialogueCorpusItem item in itemList)
            {
                item.GenerateIndexTokenList(vocabulary);
            }
        }
        
        public void ComputeIDFs()
        {
            int numberOfDistinctWords = vocabulary.ItemList.Count();
            foreach (WordData vocabularyItem in vocabulary.ItemList)
            {
                vocabularyItem.IDF = - Math.Log10((double)vocabularyItem.NumberOfSentences / numberOfDistinctWords);
            }
        }

        public void ComputeTFIDFVectors()
        {
            foreach (DialogueCorpusItem item in itemList)
            {
                item.ComputeTFIDFVector(vocabulary);
            }
        }

        public void SortOnCosineSimularity()
        {
            itemList = itemList.OrderByDescending(n => n.CosineSimularity).ToList();
        }

        public List<DialogueCorpusItem> ItemList
        {
            get { return itemList; }
            set { itemList = value; }
        }

        public Vocabulary Vocabulary
        {
            get { return vocabulary; }
            set { vocabulary = value; }
        }
    }
}
