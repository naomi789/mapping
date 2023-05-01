import pandas as pd
import plotly
import plotly.express as px
import datetime as dt
import time

def main():
    df = readCleanData()
    df = timeRange(df)
    crimeType = 'LARCENY-THEFT'
    df = filterBy(df, 'Offense Parent Group', crimeType)
    plotData(df)

def readCleanData():
    # read in crime data from 2008-2023 April : https://data.seattle.gov/Public-Safety/SPD-Crime-Data-2008-Present/tazs-3rd5
    full = pd.read_csv('./data/seattle-crime.csv')

    # remove nan times
    full = full.dropna(subset=['Offense Start DateTime'])

    # remove values where no know lat/long
    # full = full[full.Latitude != 0]
    # full = full[full.Longitude != 0]

    # remove values outside king county
    king = full[full.Latitude > 45]
    king = full[full.Latitude < 50]
    king = full[full.Longitude > -125]
    king = full[full.Longitude < -120]

    # convert string time to datetime
    king['Offense Start DateTime'] = pd.to_datetime(king['Offense Start DateTime'])
    print('now limited lat/long range, so len(king.index): ', len(king.index))
    return king


def timeRange(df):
    # only grab data where report was filled inbetween
    startDate = pd.to_datetime("1/1/2022",format='%m/%d/%Y')
    endDate = pd.to_datetime("1/1/2023",format='%m/%d/%Y')
    
    subset = df[(df['Offense Start DateTime'] > startDate) & (df['Offense Start DateTime'] < endDate)]
    print('now limited to a time range, so len(df.index) is: ', len(subset.index))
    return subset


def filterBy(df, var, crimeType):
    subset = df.loc[df[var] == crimeType]
    print('now filtering by', var, '=', crimeType, 'so len(df.index)) is: ', len(df.index), '.')
    return subset


def plotData(df):
    # https://plotly.com/python/mapbox-layers/
    fig = px.scatter_mapbox(
        df, 
        lat="Latitude", 
        lon="Longitude", 
        color="Offense", 
        hover_data=["Offense Start DateTime", "Report DateTime"]
        ).update_layout(
        mapbox={
            "style": "carto-positron",
        },
    )
    # fig.show()
    print('now plotting at time: ', time.ctime())
    plotly.offline.plot(fig, filename='./output/seattle-crime.html')

main()
