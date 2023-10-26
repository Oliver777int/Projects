using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using ChatbotLibrary;

namespace IRChatbotApplication
{
    public partial class MainForm : Form
    {
        const int MAX_CORPUS_ITEMS_SHOWN = 1000;
        private RawDataSet rawData;
        private List<string> conversationsDataList;
        private DialogueCorpus corpus = null; // The dialogue corpus, consisting of sentence pairs.
        private Chatbot chatbot;
        private List<string> analysisList;
        private Thread dialogueCorpusThread;

        public MainForm()
        {
            InitializeComponent();
            if (!DesignMode)
            {
                inputTextBox.InputReceived += new EventHandler<StringEventArgs>(HandleInputReceived);
            }
        }

        private void ImportRawData(string fileName)
        {
            char[] charsToTrim = { '"', 'L'};
            rawData = new RawDataSet();
            using (StreamReader dataReader = new StreamReader(fileName))
            {
                while (!dataReader.EndOfStream)
                {
                    string line = dataReader.ReadLine();
                    List<string> lineSplit = line.Split(new char[] { '\t' }, StringSplitOptions.RemoveEmptyEntries).ToList();
                    if (lineSplit.Count > 4)
                    {
                        MovieLine movieLine = new MovieLine();
                        movieLine.LineID = Int32.Parse(lineSplit[0].Trim(charsToTrim));
                        movieLine.Line = lineSplit[4];
                        rawData.MovieLineList.Add(movieLine);
                    }
                }
                rawData.SortOnID();
                dataReader.Close();
            }
        }

        private void loadRawDataToolStripMenuItem_Click(object sender, EventArgs e)
        {
            using (OpenFileDialog openFileDialog = new OpenFileDialog())
            {
                openFileDialog.RestoreDirectory = true;
                if (openFileDialog.ShowDialog() == DialogResult.OK)
                {
                    ImportRawData(openFileDialog.FileName);
                }
            }
        }

        private void ImportConversationData(string fileName)
        {
            conversationsDataList = new List<string>();
            using (StreamReader dataReader = new StreamReader(fileName))
            {
                while (!dataReader.EndOfStream)
                {
                    string line = dataReader.ReadLine();
                    List<string> lineSplit = line.Split(new char[] { '\t' }, StringSplitOptions.RemoveEmptyEntries).ToList();
                    if (lineSplit.Count > 3)
                    {
                        string conversationData = lineSplit[3];
                        conversationsDataList.Add(conversationData);
                    }
                }
                dataReader.Close();
            }
        }

        private void loadConversationDataToolStripMenuItem_Click(object sender, EventArgs e)
        {
            using (OpenFileDialog openFileDialog = new OpenFileDialog())
            {
                openFileDialog.RestoreDirectory = true;
                if (openFileDialog.ShowDialog() == DialogResult.OK)
                {
                    ImportConversationData(openFileDialog.FileName);
                }
            }
            generateDialogueCorpusButton.Enabled = true;
        }

        private void exitToolStripMenuItem_Click(object sender, EventArgs e)
        {
            Application.Exit();
        }

        private void generateChatBotButton_Click(object sender, EventArgs e)
        {
            // Not threadsafe because it computes almost instantly.
            generateChatBotButton.Enabled = false;
            chatbot = new Chatbot();
            chatbot.SetDialogueCorpus(corpus);
            chatbot.Initialize();
            inputTextBox.Enabled = true;
            mainTabControl.SelectedTab = chatTabPage;
        }

        private void HandleInputReceived(object sender, StringEventArgs e)
        {
            string inputSentence = e.Information;
            string outputSentence = chatbot.GenerateResponse(inputSentence);
            inputSentence = "User: " + inputSentence;
            outputSentence = "Chatbot: " + outputSentence;
            dialogueListBox.Items.Add(inputSentence);
            dialogueListBox.Items.Add(outputSentence);
            int visibleItems = dialogueListBox.ClientSize.Height / dialogueListBox.ItemHeight;
            dialogueListBox.TopIndex = Math.Max(dialogueListBox.Items.Count - visibleItems + 1, 0);


        }

        private void ThreadSafeShowAnalysis()
        {
            if (InvokeRequired) { this.Invoke(new MethodInvoker(() => ShowAnalysis())); }
            else { ShowAnalysis(); }
        }

        private void ShowAnalysis()
        {
            for (int ii = 0; ii<MAX_CORPUS_ITEMS_SHOWN; ii++)
            {
                dialogueCorpusListBox.Items.Add(analysisList[ii]);
            }
        }

        private void saveDialogueCorpusToolStripMenuItem_Click(object sender, EventArgs e)
        {
            using (SaveFileDialog saveFileDialog = new SaveFileDialog())
            {
                saveFileDialog.Filter = "text files (*.txt)|*.txt";
                if (saveFileDialog.ShowDialog() == DialogResult.OK)
                {
                    using (StreamWriter analysisWriter = new StreamWriter(saveFileDialog.FileName))
                    {
                        for (int ii = 0; ii < dialogueListBox.Items.Count; ii++)
                        {
                            string information = dialogueListBox.Items[ii].ToString();
                            analysisWriter.WriteLine(information);
                        }
                        analysisWriter.Close();
                    }
                }
            }
        }

        private void ThreadSafeToggleButtonEnabled(ToolStripButton button, Boolean enabled)
        {
            if (InvokeRequired) { this.Invoke(new MethodInvoker(() => button.Enabled = enabled)); }
            else { button.Enabled = enabled; }
        }

        private void ThreadSafeToggleMenuItemEnabled(ToolStripMenuItem menuItem, Boolean enabled)
        {
            if (InvokeRequired) { this.Invoke(new MethodInvoker(() => menuItem.Enabled = enabled)); }
            else { menuItem.Enabled = enabled; }
        }

        private void DialogueCorpusLoop()
        {
            analysisList = new List<string>();
            corpus = new DialogueCorpus();
            corpus.GetConversations(conversationsDataList);
            corpus.Process(rawData);
            analysisList.Add("Corpus Size: " + corpus.ItemList.Count().ToString() + " where " + MAX_CORPUS_ITEMS_SHOWN.ToString() + " items are shown below.");
            foreach (DialogueCorpusItem corpusItem in corpus.ItemList)
            {
                analysisList.Add(corpusItem.AsString());
            }
            ThreadSafeShowAnalysis();
            ThreadSafeToggleButtonEnabled(generateChatBotButton, true);
            ThreadSafeToggleMenuItemEnabled(saveDialogueCorpusToolStripMenuItem, true);
        }

        private void generateDialogueCorpusButton_Click(object sender, EventArgs e)
        {
            generateDialogueCorpusButton.Enabled = false;
            dialogueCorpusThread = new Thread(new ThreadStart(() => DialogueCorpusLoop()));
            dialogueCorpusThread.Start();
        }
    }
}
