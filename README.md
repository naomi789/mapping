# mapping

## LinkedIn
### Graphing the number of open jobs (manually collected)
#### Data set up of `long-col.csv`
1. Columns: `Job type,	Date,	Openings`
2. Rows:
`UXR; USA; Remote
UXR; USA; Entry level
UXR; USA; Associate
UXR; USA; Mid-senior level
UXR; USA; Director
UXR; USA; Executive
Seattle, WA, USA
UXR; Seattle, WA, USA
UXR; Seattle, WA, USA; Entry level
UXR; USA`

#### Terminal set up for `manual-linkedin.py`
1. Add `long-col.csv` within `quant/linkedin/` 
2. Set up Python3 and pip
3. `pip3 install pandas` (or pip)
4. `pip3 install plotly`
5. You should be good to go with `python3 manual-linkedin.py`

#### Terminal set up for `scrape-linkedin.py`
1. `pip3 install bs4`
2. You should be good to go for `scrape-linkedin.py`

#### Terminal set up for `analyze-linkedin.py`
1. `pip3 install nltk`
2. `pip install geopy`
3. Make sure you run `df = cleanMapData(df, commaFile)` (in main()) to create `lat-long-uxr-jobs.csv`
4. `pip3 install --user -U nltk`
5. `pip3 install --user -U numpy`
6. `pip3 install matplotlib`
7. Run `python3`, then `import nltk`, `nltk.download('punkt')`, `nltk.download('stopwords')`, `nltk.download('wordnet')`, and then you should be good!!
