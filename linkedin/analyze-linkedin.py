import pdb 
import pandas as pd
from datetime import date, timedelta
import datetime
import time
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import FreqDist, Text


def analyzeInfo(commaFile):
    df = pd.read_csv(commaFile)
    analyzeJobDescription(df)
    

def scrapeWeb(fileName):
    global timeSinceLastGetHTML
    timeSinceLastGetHTML = datetime.datetime.now()
    getInfo(fileName)
    df = readInfo(fileName)
    saveInfo(df, commaFile)
    return commaFile

  
def cleanData(df):
    df['jobDetails'].str.lower()
    df['tokenized'] = df.apply(lambda row: word_tokenize(row['jobDetails']), axis=1)
    
    df['sentences'] = df.apply(lambda row: sent_tokenize(row['jobDetails']), axis=1)
    df['tokenized'] = df.apply(lambda row: word_tokenize(row['jobDetails']), axis=1)

    stops = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    listNoStops = []
    for words in df['tokenized']:
        noStopwords = [lemmatizer.lemmatize(w.lower()) for w in words if ((w not in stops) and w.isalpha())]
        
        listNoStops.append(noStopwords)
        
    df['noStopsLemmatize'] = listNoStops
        
    return df

    
def analyzeJobDescription(df):
    df = cleanData(df)

    # frequency distribution
    allData = []
    for listWords in df['noStopsLemmatize']:
        allData += listWords   
    fd = FreqDist(allData)
    
    pdb.set_trace()
    
#    text = Text(allData)
#    text.concordance("quantitative", lines=20)
#
#    pdb.set_trace()
    
    
def makeNewDF(df):
    filtered_sentence = []
    words = word_tokenize(words)
    for w in words:
        filtered_sentence.append(w)
    return filtered_sentence


def main():
    # if I'm running this the same day I pulled new data, then: 
    todaysDate = str(datetime.datetime.now().strftime("%Y-%m-%d"))
    # else:
    # dataDate = 2023-05-16
    fileName = todaysDate + '-uxr-jobs.html'
    commaFile = fileName.partition(".")[0]+'.csv'
    analyzeInfo(commaFile)
    
    
main()
