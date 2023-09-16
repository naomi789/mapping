import pandas as pd
import pdb
import plotly.express as px


def main():
    df = pd.read_csv("data/long-col.csv")
    #    pdb.set_trace()
    df["Date"] = pd.to_datetime(df["Date"])

    # only 'UXR; USA' jobs
    title = "UXR; USA"
    df2 = df[df["Job type"].astype(str).str.contains(title)]
    graph(df2, title)

    # only 'UXR; Seattle, WA, USA' jobs
    title = "UXR; Seattle, WA, USA"
    df2 = df[df["Job type"].astype(str).str.contains(title)]
    graph(df2, title)

    # only 'Seattle, WA, USA' jobs
    title = "Seattle, WA, USA"
    df2 = df[df["Job type"].astype(str).str.match(title)]
    graph(df2, title)


def graph(df, title):
    fig = px.line(
        df, x="Date", y="Openings", color="Job type", markers=True, title=title
    )
    fig.update_xaxes(
        dtick="M1",
        tickformat="%b\n%Y",
        minor=dict(
            ticklen=4,
            dtick=7 * 24 * 60 * 60 * 1000,
            tick0="2023-05-15",
            griddash="dot",
            gridcolor="white",
        ),
    )
    fig.show()


main()
