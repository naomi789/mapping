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
        # df.loc["staff-ux-researcher-at-patreon-3586532759"]["location"]
        # print("jobURL", jobURL)
        loc = gn.geocode(df.loc[jobURL]["location"])
        print(loc)
        if loc is not None:
            lats.append(round(loc.latitude, 2))
            longs.append(round(loc.longitude, 2))
        else:
            lats.append(None)
            longs.append(None)
            
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
    commaFile = 'uxr-jobs.csv'
    df = pd.read_csv(commaFile)
    # analyzeJobDescription(df)
    # df = cleanMapData(df, commaFile)
    df = pd.read_csv('lat-long-uxr-jobs.csv')
    visualize(df, "linkedinmap")
    pdb.set_trace()
    
main()
