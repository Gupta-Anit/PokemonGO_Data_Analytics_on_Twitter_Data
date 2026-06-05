# Pokémon GO Twitter Analytics with Apache Spark

A big-data analytics project that mines Twitter data from 2016 to study the
popularity, sentiment, geographic spread, and topics of conversation around the
mobile game **Pokémon GO**, using Apache Spark (PySpark) for distributed
processing and a range of NLP and time-series techniques.

## Overview

In 2016 Pokémon GO became one of the year's biggest cultural phenomena. This
project ingests raw Twitter stream archives, filters them down to game- and
app-related tweets, and runs several analyses on top of the cleaned corpus:

- **Comparative popularity** — how often Pokémon GO was tweeted about relative to
  other popular apps and mobile games of 2016 (Twitter, Facebook, Snapchat,
  Tinder, Amazon, Clash of Clans, Mario, etc.).
- **Geographic analysis** — extracting tweet coordinates and plotting global
  Pokémon GO activity on a world map.
- **Sentiment analysis** — scoring tweet polarity (positive / neutral / negative)
  with NLTK's VADER analyzer.
- **Topic modeling** — Latent Dirichlet Allocation (LDA) over the tweet corpus to
  surface the contexts in which the game was discussed, visualized with pyLDAvis.
- **Pokémon character frequency** — joining tweets against a list of Pokémon
  names to find the most- and least-mentioned characters.
- **Time-series forecasting** — resampling hourly tweet volume and fitting a
  SARIMAX model to forecast tweet activity, with standard forecast-accuracy
  metrics (MAPE, MAE, RMSE, etc.).

## Data

- **Source:** Archived Twitter stream files (bzip2-compressed line-delimited
  JSON, `*.bz2`) covering October 2016. These raw archives are **not** included in
  this repository and must be supplied by the user.
- **Reference list:** `PokemonCharacters.csv` — a list of Pokémon names used to
  detect and count character mentions in tweets.
- **Intermediate artifacts:** The extraction scripts produce CSV files
  (`SparkAllTweets.csv`, `SparkAllRetweets.csv`, translated variants, etc.) that
  the analysis notebook consumes. These are generated locally and are not checked
  in.
- Non-English tweets are optionally translated to English via `googletrans`.

## Approach

The pipeline runs in roughly the following stages:

1. **Extraction / filtering** — Parse the raw bz2 Twitter archives, keep only a
   subset of relevant fields, and filter to tweets mentioning Pokémon GO or other
   tracked apps/games. Implemented both as standalone multiprocessing scripts
   (`parallel_pokemon.py`, `parallel_all_words.py`) and as Spark logic
   (`SparkAllWords.ipynb`), writing results to CSV.
2. **Translation** — Translate non-English tweets to English
   (`pokemon_translator.ipynb`, plus translation helpers in the scripts).
3. **Analysis** — Load the cleaned CSVs into Spark and run the popularity, geo,
   sentiment, LDA, character-frequency, and time-series analyses
   (`PokemonGo_OnTwitter.ipynb`).

## Repository structure

| File | Purpose |
| --- | --- |
| `PokemonGo_OnTwitter.ipynb` | Main analysis notebook: popularity comparison, geo mapping, VADER sentiment, LDA topic modeling, character frequency, and SARIMAX time-series forecasting in PySpark. |
| `SparkAllWords.ipynb` | Spark-based extraction of relevant tweets/retweets from raw archives into CSV (designed to run on Azure HDInsight). |
| `parallel_pokemon.py` | Multiprocessing script that extracts Pokémon GO tweets from bz2 archives and writes CSVs (filters on `pokemongo`). |
| `parallel_all_words.py` | Variant of the extraction script that filters on a broader keyword list (many apps/games). |
| `pokemon_translator.ipynb` | Filters the extracted tweet CSVs to Pokémon GO tweets and translates non-English text to English. |
| `Preprocess_all_words.ipynb` | Exploratory preprocessing / filtering helpers for the tweet corpus. |
| `PokemonCharacters.csv` | Reference list of Pokémon character names used for mention counting. |
| `bash.sh` | Helper script to install pinned Python dependencies in the Azure cluster environment. |
| `Instructions.pdf` | Original project / cluster setup instructions. |

## Tech stack

- **Python 3**
- **Apache Spark / PySpark** (Spark SQL, RDDs, Spark MLlib: `CountVectorizer`,
  `IDF`, `LDA`, `RegexTokenizer`, `StopWordsRemover`)
- **NLTK** (stopwords, WordNet lemmatizer, VADER sentiment)
- **pandas**, **NumPy**
- **statsmodels** (SARIMAX time-series modeling)
- **pyLDAvis** for LDA topic visualization
- **pygal**, **Plotly**, **matplotlib**, **seaborn** for charts and maps
- **geopy** for geocoding
- **googletrans** for tweet translation
- **Azure HDInsight** / `azure-storage-blob` for running Spark extraction at scale

## Setup & usage

> Tested with Python 3 and Java 8 (required by the bundled Spark version).

```bash
# Java 8 is required for Spark
export JAVA_HOME=$(/usr/libexec/java_home -v 1.8)

# On macOS, disable fork-safety before running the multiprocessing extractors
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# Install dependencies
pip install -r requirements.txt

# Download required NLTK corpora
python -c "import nltk; [nltk.download(p) for p in ['stopwords','wordnet','averaged_perceptron_tagger','vader_lexicon']]"
```

Suggested run order:

1. `SparkAllWords.ipynb` — extract relevant tweets from raw archives to CSV.
2. `parallel_pokemon.py` / `parallel_all_words.py` — alternative local extraction.
3. `pokemon_translator.ipynb` — translate non-English tweets.
4. `Preprocess_all_words.ipynb` — additional preprocessing.
5. `PokemonGo_OnTwitter.ipynb` — run the full analysis suite.

The extraction scripts prompt for the dataset path (a directory of `.bz2`
archives) and a core count, then write `*Tweets*.csv` / `*Retweets*.csv` outputs.

For running the Spark extraction on an Azure HDInsight cluster, see
`Instructions.pdf`.

## Notes / caveats

- **Raw data is not included.** You must supply your own Twitter archive files;
  the repository only ships the Pokémon character reference list.
- The analyses target an **October 2016** snapshot; results are specific to that
  period and dataset.
- `googletrans` relies on an unofficial Google Translate endpoint and may be
  rate-limited or break over time. Translation is optional and is commented out in
  parts of the extraction scripts.
- `SparkAllWords.ipynb` was written to run against Azure Blob Storage. **Do not
  commit live cloud credentials** — supply storage account names/keys via
  environment variables or a secrets manager rather than inline in code.
- This is an academic / portfolio project; the code favors analysis clarity over
  production hardening.

## License

Released under the [MIT License](LICENSE).
