using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.Serialization;
using System.Text;
using System.Threading.Tasks;

namespace ChatbotLibrary
{
    [DataContract]
    public class DialogueCorpusItem
    {
        private int queryID;
        private int responseID;
        private string query; // = S_1 in the assignment (used for computing cosine similarity)
        private string response; // = S_2 in the assignment
        private double cosineSimularity;
        private List<double> tfIdfVector;
        private WordDataComparer wordDataComparer;
        private List<string> tokenList;
        private List<int> indexTokenList;

        public string AsString()
        {
            string itemAsString = query + " \t " + response;
            return itemAsString;
        }

        public DialogueCorpusItem()
        {
            tokenList = new List<string>();
            indexTokenList = new List<int>();
        }

        public void Clean()
        {
            query = query.ToLower();

            query = query.Replace("\t", " ");
            if (response != null)
            {
                response = response.Replace("\t", " ");
            }

            // Removes some special characters that appear in the data set. Then replaces for example tripple dots with a space.
            string[] charsToRemove = new string[] { ")", "(", "{", "}", "[", "]", "<", ">", " '", "' ", "~", "¨","´", "`", "\"", "/", "\\", "\u0097"
            , "\u0094", "\u0093", "\u0096", "\u0092", "\u0091", "="};
            foreach (string specialCharacter in charsToRemove)
            {
                query = query.Replace(specialCharacter, string.Empty);
            }

            query = query.Replace("...", " ");
            query = query.Replace("..", " ");
            query = query.Replace("  ", " ");
            query = query.Replace("---", " ");
            query = query.Replace("--", " ");
        }

        public void Tokenize()
        {
            char[] charsToTrimStart = { ',', '.', ' ', '?', '!', ':', '*', ';', '&', '\'', '-','_'};
            char[] charsToTrimEnd = { ',', '.', ' ', '?', '!', ':', '*', ';', '&', '-', '_'};
            string[] tokens = query.Split(' ');
            foreach (string token in tokens)
            {
                tokenList.Add(token.TrimEnd(charsToTrimEnd).TrimStart(charsToTrimStart).Trim());
            }
            tokenList.RemoveAll(s => string.IsNullOrEmpty(s));
        }

        public void GenerateIndexTokenList(Vocabulary dictionary)
        {
            wordDataComparer = new WordDataComparer();
            foreach (string token in tokenList)
            {
                WordData corpusToken = new WordData();
                corpusToken.Word = token;
                int index = dictionary.ItemList.BinarySearch(corpusToken, wordDataComparer);
                if (index >= 0)
                {
                    indexTokenList.Add(index);
                }
                else
                {
                    indexTokenList.Add(-1);
                }
            }
        }

        public void ComputeTFIDFVector(Vocabulary dictionary)
        {
            // Computes the nonzero elements of the TFIDF vector. Note if index < 0, the token does not exist in the vocabulary
            // which is important for user input tokens. The index of every non-zero TFIDF element is stored in indexTokenList.
            double normalization = 0;
            foreach (int index in indexTokenList)
            {
                if (index >= 0)
                {
                    double idf = dictionary.ItemList[index].IDF;
                    normalization += Math.Pow(idf, 2);
                }
            }
            normalization = Math.Sqrt(normalization);

            tfIdfVector = new List<double>();
            foreach (int index in IndexTokenList)
            {
                if (index >= 0)
                {
                    double idf = dictionary.ItemList[index].IDF;
                    tfIdfVector.Add(idf / normalization);
                }
            }
        }

        public void ComputeCosineSimularity(DialogueCorpusItem inputItem)
        {
            // Hadamard product computed by matching the index of input TF-IDF elements with corpus TF-IDF elements.
            cosineSimularity = 0;
            foreach (int inputIndex in inputItem.IndexTokenList)
            {
                int i = 0;
                foreach (int sentenceIndex in indexTokenList)
                {
                    int j = 0;
                    if (inputIndex == sentenceIndex)
                    {
                        cosineSimularity += tfIdfVector[j] * inputItem.TFIDFVector[i];
                    }
                }
            }
        }

        public List<double> TFIDFVector
        {
            get { return tfIdfVector; }
            set { tfIdfVector = value; }
        }

        [DataMember]
        public string Query
        {
            get { return query; }
            set { query = value; }
        }

        [DataMember]
        public int QueryID
        {
            get { return queryID; }
            set { queryID = value; }
        }

        [DataMember]
        public string Response
        {
            get { return response; }
            set { response = value; }
        }

        [DataMember]
        public int ResponseID
        {
            get { return responseID; }
            set { responseID = value; }
        }

        [DataMember]
        public double CosineSimularity
        {
            get { return cosineSimularity; }
            set { cosineSimularity = value; }
        }

        [DataMember]
        public List<string> TokenList
        {
            get { return tokenList; }
            set { tokenList = value; }
        }

        [DataMember]
        public List<int> IndexTokenList
        {
            get { return indexTokenList; }
            set { indexTokenList = value; }
        }
    }
}
