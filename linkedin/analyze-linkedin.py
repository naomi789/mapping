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


def cleanMapData(df, commaFile):
    gn = geocoders.GeoNames("naomi789")
    
    lats = []
    longs = []
    oldDF = df
    jobURLS = df["miniJobURL"]
    df.set_index("miniJobURL", inplace=True)
    
    for jobURL in jobURLS:
        loc = gn.geocode(df.loc[jobURL]["location"])
        try:
            if loc is not None:
                lats.append(round(loc.latitude, 2))
                longs.append(round(loc.longitude, 2))
                print(loc, " ;", loc.latitude, "; ", loc.longitude, "/n")
                time.sleep(5)
            else:
                lats.append(None)
                longs.append(None)
        except: 
            print("cleanMapData(...) failed to gn.geocode(...) for jobURL: ", jobURL, " in location: ", loc)
            time.sleep(90)
            
            
    print(lats, longs)
    
    df["latitude"] = lats
    df["longitude"] = longs
    
    return saveDF(df, "lat-long-" + commaFile)

def saveDF(df, fileName):
    df.to_csv(fileName)
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
    df['jobDetails'].str.lower()
    df['tokens'] = df.apply(lambda row: word_tokenize(row['jobDetails']), axis=1)
    
    df['sentences'] = df.apply(lambda row: sent_tokenize(row['jobDetails']), axis=1)
    df['tokens'] = df.apply(lambda row: word_tokenize(row['jobDetails']), axis=1)

    stops = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    listNoStops = []
    for words in df['tokens']:
        noStopwords = [lemmatizer.lemmatize(w.lower()) for w in words if ((w not in stops) and w.isalpha())]
        
        listNoStops.append(noStopwords)
        
    df['noStopsLemmatize'] = listNoStops
    return df

# 
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
    pdb.set_trace()
    
    
def analyzeJobDescription(df):
    # fd = frequency distribution
    # articleLength(df)
    uniqueWords(df)
    

    
#    text = Text(allData)
#    text.concordance("quantitative", lines=20)

    
#def makeNewDF(df):
#    filtered_sentence = []
#    words = word_tokenize(words)
#    for w in words:
#        filtered_sentence.append(w)
#    return filtered_sentence


def main():
#    commaFile = 'uxr-jobs.csv'
#    df = pd.read_csv(commaFile)
#     analyzeJobDescription(df)
    
    # to create lat-long-uxr-jobs.csv:
    # df = cleanMapData(df, commaFile)
    df = processText(pd.read_csv('lat-long-uxr-jobs.csv'))
    # visualize(df, "linkedinmap")
    analyzeJobDescription(df)

    
main()
