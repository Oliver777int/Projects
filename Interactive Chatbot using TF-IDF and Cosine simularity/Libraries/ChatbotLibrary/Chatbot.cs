using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using ChatbotLibrary;

namespace ChatbotLibrary
{
    public class Chatbot
    {
        protected const int DEFAULT_NUMBER_OF_MATCHES = 5;

        protected DialogueCorpus dialogueCorpus;
        protected Random randomNumberGenerator;
        protected int numberOfMatches = DEFAULT_NUMBER_OF_MATCHES;

        public virtual void Initialize()
        {
            randomNumberGenerator = new Random();
        }

        public void SetDialogueCorpus(DialogueCorpus dialogueCorpus)
        {
            this.dialogueCorpus = dialogueCorpus;
        }
        
        public virtual string GenerateResponse(string inputSentence)
        {
            DialogueCorpusItem inputItem = new DialogueCorpusItem();
            inputItem.Query = inputSentence;
            inputItem.Clean();
            inputItem.Tokenize();
            inputItem.GenerateIndexTokenList(dialogueCorpus.Vocabulary);
            inputItem.ComputeTFIDFVector(dialogueCorpus.Vocabulary);
            
            ComputeCosineSimularity(inputItem);
            dialogueCorpus.SortOnCosineSimularity();
            int randomIndex = randomNumberGenerator.Next(numberOfMatches);
            string output = dialogueCorpus.ItemList[randomIndex].Response;
            return output;
        }

        public void ComputeCosineSimularity(DialogueCorpusItem inputItem)
        {
            foreach (DialogueCorpusItem corpusItem in dialogueCorpus.ItemList)
            {
                corpusItem.ComputeCosineSimularity(inputItem);
            }
        }
    }
}
