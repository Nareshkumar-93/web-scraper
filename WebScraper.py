import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

headers = {"Accept-Language": "en-US,en;q=0.5"}
url = "https://www.imdb.com/search/title/?groups=top_1000&ref_=adv_prv"  # URL for top 1000 movies for example
results = requests.get(url, headers=headers)

if results.status_code != 200:
    print("Error: Unable to fetch data from IMDb")
else:
    soup = BeautifulSoup(results.text, "html.parser")

    titles = []
    years = []
    time = []
    imdb_ratings = []
    metascores = []
    votes = []
    us_gross = []

    movie_div = soup.find_all('div', class_='lister-item mode-advanced')
    print(soup)

    for container in movie_div:

        # Name
        name = container.h3.a.text if container.h3 and container.h3.a else 'N/A'
        titles.append(name)

        # Year
        year = container.h3.find('span', class_='lister-item-year').text if container.h3 and container.h3.find('span', class_='lister-item-year') else 'N/A'
        years.append(year)

        # Runtime
        runtime = container.p.find('span', class_='runtime')
        runtime = runtime.text if runtime else 'N/A'
        time.append(runtime)

        # IMDB rating
        imdb = float(container.strong.text) if container.strong else np.nan
        imdb_ratings.append(imdb)

        # Metascore
        m_score = container.find('span', class_='metascore')
        m_score = int(m_score.text.strip()) if m_score else np.nan
        metascores.append(m_score)

        # NV containers (votes and grosses)
        nv = container.find_all('span', attrs={'name': 'nv'})

        # Votes
        vote = nv[0].text if len(nv) > 0 else 'N/A'
        votes.append(vote)

        # Gross
        grosses = nv[1].text if len(nv) > 1 else 'N/A'
        us_gross.append(grosses)

    # Building our Pandas DataFrame
    movies = pd.DataFrame({
        'movie': titles,
        'year': years,
        'timeMin': time,
        'imdb': imdb_ratings,
        'metascore': metascores,
        'votes': votes,
        'us_grossMillions': us_gross
    })

    # Cleaning data with Pandas
    movies['year'] = movies['year'].str.extract('(\d+)').astype(int, errors='ignore')
    movies['timeMin'] = movies['timeMin'].str.extract('(\d+)').astype(int, errors='ignore')
    movies['votes'] = movies['votes'].str.replace(',', '').astype(int, errors='ignore')
    movies['us_grossMillions'] = movies['us_grossMillions'].map(lambda x: x.lstrip('$').rstrip('M') if x != 'N/A' else np.nan)
    movies['us_grossMillions'] = pd.to_numeric(movies['us_grossMillions'], errors='coerce')

    print(movies.head())  # Print the first few rows of the DataFrame for inspection