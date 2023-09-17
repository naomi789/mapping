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
from geopy import geocoders
import plotly.express as px
import plotly
import string
import os



def cleanMapData(df):
    gn = geocoders.GeoNames("naomi789")
    
    lats = []
    longs = []
    oldDF = df
    jobURLS = df["miniJobURL"]
    df.set_index("miniJobURL", inplace=True)
    
    for jobURL in jobURLS:
        loc = gn.geocode(df.loc[jobURL]["location"])
        try:
            if (loc is not None) and (loc != "United States"):
                time.sleep(1)
                lats.append(round(loc.latitude, 2))
                time.sleep(1)
                longs.append(round(loc.longitude, 2))
                # print(loc, " ;", loc.latitude, "; ", loc.longitude, "/n")
                
            else:
                lats.append(None)
                longs.append(None)
        except: 
            print("cleanMapData(...) failed to gn.geocode(...) for jobURL: ", jobURL, " in location: ", loc)
            time.sleep(90)
            
            
    # print(lats, longs)
    
    df["latitude"] = lats
    df["longitude"] = longs
    
    return df


    
def visualize(df, title):
    fig = px.scatter_mapbox(
        df, 
        lat="latitude", 
        lon="longitude", 
#        color="Offense", 
        hover_data=["miniJobURL", "jobTitle", "companyName"]
        ).update_layout(
        mapbox={
            "style": "carto-positron",
            "zoom": 3,
            # center on middle of the US
            "center": dict(
            lat=39,
            lon=-98
        ),
        },
    )
    # fig.show()
    print('now plotting at time: ', time.ctime())
    plotly.offline.plot(fig, filename=title)
    

def scrapeWeb(fileName):
    global timeSinceLastGetHTML
    timeSinceLastGetHTML = datetime.datetime.now()
    getInfo(fileName)
    df = readInfo(fileName)
    saveInfo(df, commaFile)
    return commaFile

  
def processText(df):
    df['jobDetails'] = df['jobDetails'].str.lower()
    df['jobDetails'] = df['jobDetails'].astype(str)

    df['tokens'] = df['jobDetails'].apply(word_tokenize) 
    
    # df['tokens'] = df.apply(lambda row: word_tokenize(row['jobDetails']), axis=1)
    
    df['sentences'] = df.apply(lambda row: sent_tokenize(row['jobDetails']), axis=1)
    
    # list of tokens
    df['tokens'] = df.apply(lambda row: word_tokenize(row['jobDetails']), axis=1)
    # tokenized string
    df['tokenized'] = df['jobDetails'].map(lambda x: x.translate(str.maketrans('', '',string.punctuation)))

    stops = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    listNoStops = []
    for words in df['tokens']:
        noStopwords = [lemmatizer.lemmatize(w.lower()) for w in words if ((w not in stops) and w.isalpha())]
        
        listNoStops.append(noStopwords)
        
    df['noStopsLemmatize'] = listNoStops
    
    return df


def frequencyDistribution(df): 
    allData = []
    for listWords in df['noStopsLemmatize']:
        allData += listWords   
    fd = FreqDist(allData)
    return fd

def articleLength(df):
    df['articleLength'] = df['noStopsLemmatize'].apply(lambda x: len(x))
    fig = px.histogram(df, x="articleLength")
    print('now plotting at time: ', time.ctime())
    plotly.offline.plot(fig, filename='articleLength.html')

    
def uniqueWords(df):
    df['uniqueWords'] = df['tokenized'].str.split().apply(lambda x: len(set(x)))
    fig = px.histogram(df, x="uniqueWords")
    print('now plotting at time: ', time.ctime())
    plotly.offline.plot(fig, filename='uniqueWords.html')

    
def wordsRelatedTo(df):
    # https://www.dataquest.io/blog/tutorial-text-analysis-python-test-hypothesis/
    return


    
def analyzeJobDescription(df):
    # fd = frequency distribution
    # articleLength(df)
    # uniqueWords(df)
    wordsRelatedTo(df)

    
#    text = Text(allData)
#    text.concordance("quantitative", lines=20)

    
#def makeNewDF(df):
#    filtered_sentence = []
#    words = word_tokenize(words)
#    for w in words:
#        filtered_sentence.append(w)
#    return filtered_sentence

def readAllData():
    # https://stackoverflow.com/questions/13131497/os-walk-to-crawl-through-folder-structure
    # https://stackoverflow.com/questions/68291894/read-all-csv-files-within-the-folder-without-having-a-fixed-name
    # allDfs = []
    df = pd.read_csv("uxr-jobs.csv")
    some = df
    for root, dirs, _ in os.walk("."):
        for d in dirs:
            files = [os.path.join(root, d, f) for f in os.listdir(os.path.join(root, d)) if f.endswith(".csv")]
            if len(files)>0:
                for f in files:
                    some = pd.read_csv(f)
                    df = pd.concat([df, some]).reset_index(drop=True)
    
    df.to_csv('pre-processing-all-data.csv')

    df = processText(df)
    df.to_csv('post-processing-all-data.csv') 
    
    # to create data/lat-long-uxr-jobs.csv:
    df = cleanMapData(df)
    df.to_csv('lat-long-all-data.csv')

    return df


def main():
    # for just 25 jobs & their details: 
    # miniDf = pd.read_csv('data/uxr-jobs.csv')
    
    # to read all CSVs here: 
    # df = readAllData()
    
    # read-old-data
    df = pd.read_csv('lat-long-all-data.csv')
    
    # make map in US
    visualize(df, "linkedinmap.html")
    
    # run analysis of job decriptions
    analyzeJobDescription(df)

    
main()
