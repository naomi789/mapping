import pdb # pdb.set_trace()
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
# from matplotlib import pyplot
import string
import os
import re
import ast


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
                
    df["latitude"] = lats
    df["longitude"] = longs
    
    return df


    
def visualize(df, title):
    fig = px.scatter_mapbox(
        df, 
        lat="latitude", 
        lon="longitude", 
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
    print('now plotting at time: ', time.ctime())
    plotly.offline.plot(fig, filename=title)
    

def scrapeWeb(fileName):
    global timeSinceLastGetHTML
    timeSinceLastGetHTML = datetime.datetime.now()
    getInfo(fileName)
    df = readInfo(fileName)
    saveInfo(df, commaFile)
    return commaFile

  
def processJobDetails(df):
    df['jobDetails'] = df['jobDetails'].astype(str)
    df['jobDetails'] = df['jobDetails'].str.lower()

    df['tokens'] = df['jobDetails'].apply(word_tokenize) 
    
    df['sentences'] = df.apply(lambda row: sent_tokenize(row['jobDetails']), axis=1)
    
    # list of tokens
    df['tokens'] = df.apply(lambda row: word_tokenize(row['jobDetails']), axis=1)
    # tokenized string
    df['tokenized'] = df['jobDetails'].map(lambda x: x.translate(str.maketrans('', '',string.punctuation)))

    stops = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    listNoStops = []
    allNoStopWords = []
    for words in df['tokens']:
        noStopWords = [lemmatizer.lemmatize(w.lower()) for w in words if ((w not in stops) and w.isalpha())]
        # yes, putting lists in lists here!!
        listNoStops.append(noStopWords)
        # if I wanted one big list, it would be: 
        # listNoStops += noStopWords
        allNoStopWords += noStopWords

    # save to df
    df['noStopsLemmatize'] = listNoStops
    
    # TODO STUCK HERE NEXT
    # trying to save `allNoStopWord` (a list) to a csv/txt file:
    
    # open file in write mode
    #with open(r'E:/demos/files_demos/account/sales.txt', 'w') as fp:
    #    for item in names:
    #        # write each item on a new line
    #        fp.write("%s\n" % item)
    #    print('Done')

    
    return df

def cleanAdjectives(df):
    # 'Seniority level'
    # 'Employment type'
    # 'Job function'
    # 'Industries'
    df['allCriteria'] = df['allCriteria'].apply(lambda x: ast.literal_eval(x))
    
    sen = None
    emp = None
    job = None
    ind = None
    
    seniority = []
    employmentType = []
    jobFunction = []
    industries = []

    # os._exit(0)
    
    for criterias in df['allCriteria']:
        sen = None
        emp = None
        job = None
        ind = None
        for criteria in criterias: 
            if criteria[0] == 'Seniority level':
                sen = criteria[1]
            elif criteria[0] == 'Employment type':
                emp = criteria[1]
            elif criteria[0] == 'Job function':
                job = criteria[1]
            elif criteria[0] == 'Industries':
                ind = criteria[1]
            else:
                print("\n/n\n/n CRITERIA", allCriteria)
                assert True, "error"
        seniority.append(sen)
        employmentType.append(emp)
        jobFunction.append(job)
        industries.append(ind)
            
    #todo now I need to set values in the df to this
    df['seniorityLevel'] = seniority
    df['employmentType'] = employmentType
    df['jobFunction'] = jobFunction
    df['industries'] = industries
    return df


def frequencyDistribution(df): 
#    col = df['noStopsLemmatize']
    
    for words in df['noStopsLemmatize']:
        pdb.set_trace()
        words = list(words)
        for word in words: 
            print(word)
        
#    pdb.set_trace()

#        
#        if allData != listWords:
#            allData += listWords 
    
#    pdb.set_trace()

#    fd = FreqDist(allData)
    # fd.most_common(100)
    
    fig = px.histogram(df, x='noStopsLemmatize')
    plotly.offline.plot(fig, filename='freqDistr.html')
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
    # calculate frequency
    fd = frequencyDistribution(df)
    
    # fd = frequency distribution
    # articleLength(df)
    # uniqueWords(df)
    # wordsRelatedTo(df)

    
#    text = Text(allData)
#    text.concordance("quantitative", lines=20)

def openAllFiles():
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
    return df


def readAllData():
    # either read files or: 
    # df = openAllFiles()
    # or instead read existing: 
    df = pd.read_csv('pre-processing-all-data.csv')
    
    # then clean & process: 
    # df = cleanJobTitles(df)
    df = processJobDetails(df)
    df.to_csv('post-processing-all-data.csv') 
    
    # to create data/lat-long-uxr-jobs.csv:
    df = cleanMapData(df)
    df.to_csv('lat-long-all-data.csv')

    return df

def vizCompanyName(df): 
    fig = px.histogram(df, x='companyName').update_xaxes(categoryorder='total descending')
    plotly.offline.plot(fig, filename='companyName.html')
    

def cleanJobTitles(df):
    # remove parts of job title in parenthesis
    df['jobTitle'] =  df['jobTitle'].apply(lambda x: re.sub(r"\(.*\)","", x))
    # remove parts of job title in brackets
    df['jobTitle'] =  df['jobTitle'].apply(lambda x: re.sub(r"\[.*\]","", x))
    # remove anything after a bar | 
    df['jobTitle'] =  df['jobTitle'].apply(lambda x: re.sub(r"\|*","", x))
    # remove anything after a dash
    df['jobTitle'] =  df['jobTitle'].apply(lambda x: re.sub(r"\-*","", x))
    # remove anything after comma
    df['jobTitle'] =  df['jobTitle'].apply(lambda x: re.sub(r"\,*","", x))
    # todo: would be nice to keep numbers under 5, eg, level 1
    # remove all numbers (including levels)
    df['jobTitle'] = df['jobTitle'].apply(lambda x: re.sub('\d+', '', x))
            
    messyJobTitles = df['jobTitle'].str.findall(r'\([^()]*\)').sum()
    
    assert len(messyJobTitles)==0, "unable to remove brackets and/or parenthesis"
    
    return df
    
    
def visJobTitle(df):
    fig = px.histogram(df, x='jobTitle').update_xaxes(categoryorder='total descending')
    plotly.offline.plot(fig, filename='jobTitle.html')



def main():
    # for just 25 jobs & their details: 
    # miniDf = pd.read_csv('data/uxr-jobs.csv')
    
    # to read all CSVs here: 
    # df = readAllData()
    
    # read-old-data
    df = pd.read_csv('lat-long-all-data.csv')
    
    # testing
#    df = cleanAdjectives(df)
#    df.to_csv('with-criteria-all-data.csv')
#    df = cleanJobTitles(df)
#    df.to_csv('2023-09-16-saturday.csv')
    # make map in US
    # visualize(df, "linkedinmap.html")
    
    # companies with job listings
    # vizCompanyName(df)
    # job titles from job listings
    # visJobTitle(df)
    
    # run analysis of job decriptions
    # analyzeJobDescription(df)

    
main()
