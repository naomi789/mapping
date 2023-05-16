from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import pdb 
import pandas as pd
import datetime
from datetime import date, timedelta
import time
import errno
import os


def getInfo(fileName):
    global timeSinceLastGetHTML
    global numGetHTMLCalls
    numGetHTMLCalls = 0
    startViewingJobNum = 1
    shortURL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=ux%20researcher&location=United%20States&refresh=true&sortBy=N"
    # "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?currentJobId=3590113942&f_T=14292&f_WT=2&geoId=103644278&keywords=ux%20researcher&location=United%20States&refresh=true&sortBy=R&start="
    cont = True
    
    # continue doing this until we run out of jobs to look at 
    while (cont): 
        url = shortURL + str(startViewingJobNum)
        startViewingJobNum +=25
        try: 
            if ((timeSinceLastGetHTML + datetime.timedelta(0,5)) < datetime.datetime.now()):
                time.sleep(10)
            else: 
                timeSinceLastGetHTML = datetime.datetime.now()
            page = urlopen(url)
            print("numGetHTMLCalls: ", numGetHTMLCalls)
            numGetHTMLCalls += 1
            html_bytes = page.read()
            html = html_bytes.decode("utf-8")
            startNumFileName = str(startViewingJobNum) + fileName
            with open(startNumFileName, 'w') as file:
                file.write(html)
        except HTTPError as err:
            print("\nALERT WE GOT ERR.CODE:\n", err.code, "\n", err, "\n")
            # time.sleep(100)
            continue
        # TO DO WE SHOULD FIX THIS LATER
        cont = False
    
    
def readInfo(fileName):
    with open(fileName) as fp:
        soup = BeautifulSoup(fp, "html.parser")    
    
    myBaseCard = soup.find_all("div", ["base-card"])
    
    df = None
    counter = 0
    for eachCard in myBaseCard:
        try:
            df2 = getJobInfo(eachCard)
        except: 
            continue
        
        counter+=1
        if counter == 1:
            df = df2
        else:
            df = pd.concat([df2, df])
    
    return df

def getJobInfo(eachCard): 
        # job title
        jobTitle = eachCard.find_all("h3", ["base-search-card__title"])
        assert(len(jobTitle)==1)
        jobTitle = jobTitle[0].getText().strip()
        
        # location
        location = eachCard.find_all("span", ["job-search-card__location"])        
        location = location[0].getText().strip()
        
        # company name
        company = eachCard.find_all("h4", ["base-search-card__subtitle"])
        assert(len(company)==1)
        companyName = company[0].getText().strip()
        
        # link to job description
        jobURL = eachCard.find_all("a", ["base-card__full-link"])
        assert(len(jobURL)==1)
        jobURL = jobURL[0]["href"].partition("?")[0]
        miniJobURL = jobURL.split("/")[-1]
        fileName = miniJobURL + '.html'
        
        try:
            numApplicants, allCriteria, jobDetails, allCriteriaTitles, allCriteriaDetails  = saveJobDetails(jobURL, fileName)
        except:
            return pd.DataFrame([[miniJobURL, jobTitle, companyName, location, numApplicants, [], [], [], ""]], columns=["miniJobURL", "jobTitle", "companyName", "location", "numApplicants", "active", "listDateListed", "allCriteria", "jobDetails"])
              
        # actively hiring? 
        active = eachCard.find_all("span", ["result-benefits__text"])
        # I think if it's not active, then they just don't have anything??
        if len(active) > 0:
            active = active[0].getText().strip()
        
        # when posted? 
        listDateListed = eachCard.find_all("time", ["job-search-card__listdate"])
           
        # to save in dataframe: 
        # note that allCriteria is a list of tuples!!
        return pd.DataFrame([[miniJobURL, jobTitle, companyName, location, numApplicants, active, listDateListed, allCriteria, jobDetails]], columns=["miniJobURL", "jobTitle", "companyName", "location", "numApplicants", "active", "listDateListed", "allCriteria", "jobDetails"])
        
        
def saveJobDetails(jobURL, fileName):
    global timeSinceLastGetHTML
    global numGetHTMLCalls
    try:
        print("numGetHTMLCalls: ", numGetHTMLCalls)
        numGetHTMLCalls += 1
        
        if ((timeSinceLastGetHTML + datetime.timedelta(0,5)) < datetime.datetime.now()):
            time.sleep(10)
        else: 
            timeSinceLastGetHTML = datetime.datetime.now()
        
        page = urlopen(jobURL)
        
        html_bytes = page.read()
        html = html_bytes.decode("utf-8")
        with open(fileName, 'w') as file:
            file.write(html)
        print("PRINTING fileName: ", fileName)
        return getJobDetails(fileName)
    except HTTPError as err:
        print("\n\nsaveJobDetails(jobURL, fileName)", jobURL, fileName, "\n\n")
        print("\nexcept HTTPError as err\n", err, "\n")
        return err
            

def getJobDetails(fileName):    
    with open(fileName) as fp:
        soup = BeautifulSoup(fp, "html.parser")
    
    # number of applicants
    htmlApplicants = soup.find("figcaption", "num-applicants__caption")
    if htmlApplicants != None:
        numApplicants = htmlApplicants.getText().strip()
    else: 
        numApplicants = None
    
    # full job description
    htmlJobDetails = soup.find("div", "show-more-less-html__markup show-more-less-html__markup--clamp-after-5")
    jobDetails = htmlJobDetails.getText().strip()
    
    htmlCriterias = soup.find_all("li", ["description__job-criteria-item"])
    allCriteria = []
    allCriteriaTitles = []
    allCriteriaDetails = []
    for oneCriteria in htmlCriterias:
        title = oneCriteria.find("h3", "description__job-criteria-subheader")
        title = title.getText().strip()
        details = oneCriteria.find("span","description__job-criteria-text")
        details = details.getText().strip()
        allCriteria.append([title,details])
        allCriteriaDetails.append(details)
        allCriteriaTitles.append(title)
        
    return numApplicants, allCriteria, jobDetails, allCriteriaTitles, allCriteriaDetails

def saveInfo(df, fileName):
    print("PRINTING fileName: ", fileName)
    df.to_csv(fileName)


def scrapeWeb(fileName, commaFile):
    global timeSinceLastGetHTML
    timeSinceLastGetHTML = datetime.datetime.now()
    getInfo(fileName)
    df = readInfo(fileName)
    saveInfo(df, commaFile)
    return commaFile



def main():
    todaysDate = str(datetime.datetime.now().strftime("%Y-%m-%d"))
    fileName = todaysDate + '-uxr-jobs.html' # 2023-05-16-uxr-jobs.html
    commaFile = fileName.partition(".")[0]+'.csv'
    scrapeWeb(fileName, commaFile)
    
    
main()
