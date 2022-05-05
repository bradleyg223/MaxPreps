# import packages for Beautiful Soup and requests
from bs4 import BeautifulSoup
import requests
import pandas as pd


class WebScraper:
    def __init__(self, sport = 'football', gender = 'boys', start_date = '01-01-2021', end_date = '12-31-2021', state = 'ma'):
        '''
        This class is used to scrape MaxPreps
        User can select from
        '''
        
        self.sport = sport
        self.gender = gender
        self.start_date = start_date
        self.end_date = end_date
        self.state = state

        self.date_range = self._get_date_range()
        self.game_list = []

    def _get_date_range(self):
        # create a list, and for each day use string formatting to format the date as DD/MM/YYYY
        date_range = pd.date_range(start=self.start_date, end=self.end_date)
        date_list = []
        for date in date_range:
            date_list.append(date.strftime('%m/%d/%Y'))
        return date_list

    def _error_check(self):
        # check if the sport is valid
        if self.sport not in ['football', 'basketball', 'baseball', 'hockey']:
            raise ValueError(f'{self.sport} is not a valid sport')
        
        # check dates are valid
        if self.start_date > self.end_date:
            raise ValueError('Start date must be before end date')

    def web_scrape(self):
        for date in self._get_date_range():
            url = f'https://www.maxpreps.com/list/schedules_scores.aspx?date={date}&gendersport={self.gender},{self.sport}&state={self.state}'
            
            try:
                page = requests.get(url)
                soup = BeautifulSoup(page.content, 'html.parser')
                data = soup.find_all("ul", {"class": "teams"})

                for i in range(len(data)):
                    try:
                        away_team = data[i].find_all("li")[0].find("div", {"class" : "name"}).text
                        home_team = data[i].find_all("li")[1].find("div", {"class" : "name"}).text

                        away_score = data[i].find_all("li")[0].find("div", {"class" : "score"}).text
                        home_score = data[i].find_all("li")[1].find("div", {"class" : "score"}).text

                        self.game_list.append({'away_name': away_team, 'home_name': home_team, 'away_score': away_score, 'home_score': home_score, "date" : date})

                    except:
                        pass
            except:
                pass


    def games_to_df(self):
        # putting games into a DF
        games = pd.DataFrame(self.game_list)

        # drop any game where home or away name contains '(#'. These teams do not play in Massachusetts
        games = games[~games['away_name'].str.contains('\(#')]
        games = games[~games['home_name'].str.contains('\(#')]
        games.drop_duplicates(subset=['away_name', 'home_name', 'date'], keep='last', inplace=True)

        # show gmes where home or away name contains a letter
        games = games[(~games['home_score'].str.contains('\D')) & (~games['away_score'].str.contains('\D'))]

        # convert scores to ints
        games['away_score'] = games['away_score'].astype(int)
        games['home_score'] = games['home_score'].astype(int)

        # return df to csv, with the filename formatted to include the sport, state, and date
        return games.reset_index(drop=True)
