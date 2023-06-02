import pandas as pd
import pdb 
import plotly.express as px


def main():
    df = pd.read_csv('long-col.csv')
    # pdb.set_trace()
    # df["Date"]=pd.to_datetime(df["Date"])
    
    # only 'UXR; USA' jobs
    title = 'UXR; USA'
    df2 = df[df['Job type'].astype(str).str.contains(title)]
    graph(df2, title)
    
    # only 'UXR; Seattle, WA, USA' jobs
    title = 'UXR; Seattle, WA, USA'
    df2 = df[df['Job type'].astype(str).str.contains(title)]
    graph(df2, title)
    
    # only 'Seattle, WA, USA' jobs
    title = 'Seattle, WA, USA'
    df2 = df[df['Job type'].astype(str).str.match(title)]
    graph(df2, title)
    
def graph(df, title):
    fig = px.line(df, x='Date', y='Openings', color='Job type', markers=True, title=title)
    fig.show()
    
    
main()
