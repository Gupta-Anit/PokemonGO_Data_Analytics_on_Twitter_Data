# FinalPokemonGO

PokemonGO Analysis on Twitter Data

1. USE `python3`.
2. Set your java version to 8 (`export JAVA_HOME=$(/usr/libexec/java_home -v 1.8)`)
3. Before running multiprocess, desable fork safety (`export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES`)

# REQUIREMENTS

1. Conda
2. jupyter notebook
3. pandas
4. progressbar (`pip3 install progressbar2`)
5. Google Translator (`pip3 install googletrans`)
6. For Spark clustering in Azure HDInsights, find the detailed instructions in `Cluster Instructions.pdf`
7. Pygal(`pip install pygal`)
8. pyLDAvis(`pip install pyldavis`)
9. Geopy(`pip install geopy`)
10. Plotly(`pip install plotly`)
11. NLTK(`pip install nltk`)
  `nltk.download('stopwords')`
  `nltk.download('wordnet')`
12. Time Series Packages
  `pip install statsmodels`
  `pip install datetime`
  `pip install ipython`
  `pip install ipywidgets`
  `pip install strings`
  `pip install seaborn`

# SEQUENCE(`Preferably`)

1. SparkAllWords.ipynb
2. pokemon_translator.ipynb
3. PokemonGo_OnTwitter.ipynb
4. parallel_all_words.py
5. parallel_pokemon.py
6. Preprocess_all_words.ipynb
