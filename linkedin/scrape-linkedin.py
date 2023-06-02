from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import pdb 
import pandas as pd
import datetime
from datetime import date, timedelta
import time
import errno
import os.path, time # os

# NOTES: 
# os._exit(0)
# pdb.set_trace()

def getInfo(dataDate, fileName):
    global timeSinceLastGetHTML
    global numGetHTMLCalls
    startViewingJobNum = 1
    shortURL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=ux%20researcher&location=United%20States&refresh=true&sortBy=N"
    # Seattle only entry-level and associate
    
    # Seattle only
    # https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=ux%20researcher&location=Seattle&refresh=true&sortBy=N
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
            
            
            
            # save local
            # ensure the local directory exists
            # os.makedirs(os.path.dirname(fileName), exist_ok=True)
            print(fileName)
            with open(fileName, 'w') as file:
                file.write(html)
            # print("locally saved all the jobs we pulled: ", fileName)
            fileName = dataDate + "-" + fileName
    
            # save backup copy
            fileName = dataDate + "/" + fileName
            # ensure the directory exists
            os.makedirs(os.path.dirname(fileName), exist_ok=True)
            # save backup
            with open(fileName, 'w') as file:
                file.write(html)
            # print("backedup all the jobs we pulled: ", fileName)
    
        except HTTPError as err:
            print("\nALERT WE GOT ERR.CODE:\n", err.code, "\n", err, "\n")
            # time.sleep(100)
            continue
        # TO DO WE SHOULD FIX THIS LATER
        cont = False
    
    
def readInfo(dataDate, fileName):
    fileName = dataDate + "/" + dataDate + "-" + fileName
    with open(fileName) as fp:
        soup = BeautifulSoup(fp, "html.parser")
    
    myBaseCard = soup.find_all("div", ["base-card"])
    
    df = None
    counter = 0
    for eachCard in myBaseCard:
        try:
            df2 = getJobInfo(dataDate, eachCard)
        except: 
            print("readInfo(...) failed to getJobInfo(...) for a card")
            # TODO so what should I set df2 = ???
            
        counter+=1
        if counter == 1:
            df = df2
        else:
            df = pd.concat([df2, df])
        
    return df

def getJobInfo(dataDate, eachCard): 
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
    fileName = dataDate + "/" + miniJobURL + '.html'

    try:
        numApplicants, allCriteria, jobDetails, allCriteriaTitles, allCriteriaDetails  = saveJobDetails(jobURL, fileName)
    except:
        print("mising some details (numApplicants, active, listDateListed, allCriteria, jobDetails) but returning partial jobInfo: ")
        df = pd.DataFrame([[miniJobURL, jobTitle, companyName, location, "", [], [], [], ""]], columns=["miniJobURL", "jobTitle", "companyName", "location", "numApplicants", "active", "listDateListed", "allCriteria", "jobDetails"])
        return df

    
    # actively hiring? 
    active = eachCard.find_all("span", ["result-benefits__text"])
    # I think if it's not active, then they just don't have anything??
    if len(active) > 0:
        active = active[0].getText().strip()

    # when posted? 
    listDateListed = eachCard.find("time", ["job-search-card__listdate"])
    if listDateListed.has_attr('datetime'):
        listDateListed = listDateListed['datetime']
    else:
        listDateListed = ''
    
    # to save in dataframe: 
    # note that allCriteria is a list of tuples!!
    df = pd.DataFrame([[miniJobURL, jobTitle, companyName, location, numApplicants, active, listDateListed, allCriteria, jobDetails]], columns=["miniJobURL", "jobTitle", "companyName", "location", "numApplicants", "active", "listDateListed", "allCriteria", "jobDetails"])
    return df
        
        
def saveJobDetails(jobURL, fileName):
    global timeSinceLastGetHTML
    global numGetHTMLCalls
    try:
        # print("numGetHTMLCalls: ", numGetHTMLCalls)
        numGetHTMLCalls += 1
        
        if ((timeSinceLastGetHTML + datetime.timedelta(0,5)) < datetime.datetime.now()):
            time.sleep(10)
        else: 
            timeSinceLastGetHTML = datetime.datetime.now()
            
        
        page = urlopen(jobURL)
        
        html_bytes = page.read()
        html = html_bytes.decode("utf-8")
        # TODO: confirm that I want these files without dates in their names. Will I regret this later? 
        os.makedirs(os.path.dirname(fileName), exist_ok=True)
        
        with open(fileName, 'w') as file:
            file.write(html)
        # print("PRINTING from saveJobDetails(...): ", fileName)
        numApplicants, allCriteria, jobDetails, allCriteriaTitles, allCriteriaDetails = getJobDetails(fileName)

        return numApplicants, allCriteria, jobDetails, allCriteriaTitles, allCriteriaDetails
    except HTTPError as err:
        print("saveJobDetails(...) failed due to err:", err)
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
    # htmlJobDetails = soup.find("div", "show-more-less-html__markup show-more-less-html__markup--clamp-after-5")
    htmlJobDetails = soup.find("div", "show-more-less-html__markup show-more-less-html__markup--clamp-after-5 relative overflow-hidden")
    if htmlJobDetails != None:
        jobDetails = htmlJobDetails.getText().strip()
    else: 
        jobDetails = None
        print("unable to get job details for: ", fileName)
    
    
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


def saveInfo(df, dataDate, fileName):
    # print("PRINTING LOCAL fileName: ", fileName)
    df.to_csv(fileName)
    fileName = dataDate + "/" + dataDate + "-" + fileName
    # print("PRINTING BACKUP fileName: ", fileName)
    df.to_csv(fileName)


def scrapeWeb(dataDate, fileName):
    global timeSinceLastGetHTML
    global numGetHTMLCalls
    numGetHTMLCalls = 0
    timeSinceLastGetHTML = datetime.datetime.now()
    # TODO PAUSE ONCE RUN ONCE PER DAY
    # time.ctime(os.path.getmtime(file))
    getInfo(dataDate, fileName)
    df = readInfo(dataDate, fileName)
    saveInfo(df, dataDate, fileName.partition(".")[0] + '.csv')


def main():
    dataDate = str(datetime.datetime.now().strftime("%Y-%m-%d"))
    # if I'm re-running the script
    # dataDate = '2023-05-17'
    # 2023-05-17-uxr-jobs.html
    fileName = 'uxr-jobs.html'
    commaFile = fileName.partition(".")[0]+'.csv'
    scrapeWeb(dataDate, fileName)
    
    
main()
