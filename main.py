# NBA Stat Finder
# Stats used from basketball-reference
# Author: Winston Chieng
"""Scrape basketball-reference website for info on a given NBA player"""

import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd

NAME = input("Enter the name of a basketball player in the following format -> Jamal Murray\n")


special_inputs = {'shaq': 'Shaquille O\'Neal', 'steph': 'Stephen Curry', 'the goat': 'Jamal Murray'}
if NAME in special_inputs:
    NAME = special_inputs[NAME]

# Convert input to retrieve Basketball-Reference Link
temp = NAME.replace("'", "").lower().split()
last_name = ''

if len(temp[1]) < 5:
    last_name = temp[1]
else:
    last_name = temp[1][:5]

link = 'http://www.basketball-reference.com/players/' + temp[1][0] + '/' + \
       last_name + temp[0][:2] + '01.html'

# Get HTML text to parse
html_text = requests.get(link).text
soup = BeautifulSoup(html_text, 'lxml')


def check_valid() -> bool:
    """Check if user input is a valid basketball player"""

    return str(soup.find('h1').get_text()) != "Page Not Found (404 error)"


def intro_paragraph() -> None:
    """Create and print the introduction paragraph for the input player"""
    intro = ''
    FAQ = soup.find('div', id='div_faq')
    faq_answers = FAQ.find_all('p')

    intro += str(faq_answers[0]).strip('<p>/.')

    birth = str(faq_answers[1]).strip('<p>/.')
    birth = birth[birth.index('born') + 4:]
    intro += birth

    height = ''
    weight = ''
    draft = ''
    rings = NAME + ' has won 0 championships. LOL'

    for ans in faq_answers:
        if "tall" in str(ans):
            height = str(ans).strip("<p>/.")
            height = height[height.index("is") + 2:]
        elif "lbs" in str(ans):
            weight = str(ans).strip("<p>/.")
            weight = weight.split()
            weight = weight[3] + " " + weight[4]
        elif "drafted" in str(ans.get_text()):
            draft_data = str(ans).strip("<p>/.")
            draft_team_begin = draft_data.index('.html">')
            draft_team_end = draft_data.index("</a>")
            draft_team = draft_data[draft_team_begin + 7: draft_team_end]

            draft_year_begin = draft_data.rfind('.html">')
            draft_year_end = draft_data.rfind("</a")
            draft_year = draft_data[draft_year_begin + 7: draft_year_end]

            draft_data = draft_data.split(',')
            draft_round = draft_data[1].strip(" ") + draft_data[2]

            draft = NAME + " was drafted by the " + draft_team + " as a " + draft_round + \
                " in the " + draft_year + "."
        elif "championships" in str(ans):
            rings = str(ans).strip("<p>/.")
            if '0' in rings:
                rings += '. LOL'
            else:
                rings += '!'

    # Pull data from the player info at top of site
    fact_box = soup.find('div', id='info')
    fact_box = fact_box.find_all('p')

    pos = ''

    for x in range(len(fact_box)):
        if 'Position:' in str(fact_box[x]):
            pos = fact_box[x].get_text()
            pos = str(pos).split('\n')[4].strip(" ")

    # The 8th faq question will include 'last played' if the player is retired
    retired = str(faq_answers[7]).strip('<p>/.')

    if 'last' not in retired:
        contract = soup.find('div', id='all_contract')

        # content in html comments
        comments = contract.find_all(string=lambda text: isinstance(text, Comment))
        comment = str(comments[0])

        team_begin = comment.index(".html'>")
        team_end = comment.index("</a>")
        team = comment[team_begin + 7: team_end]

        intro = intro + " and plays " + pos + ", currently he is on the " + team + ".\n"
    else:
        contract = soup.find('div', id='all_all_salaries')
        comments = contract.find_all(string=lambda text: isinstance(text, Comment))
        comment = str(comments[0])

        team_begin = comment.rfind(".html\">", 0, comment.rfind(".html\">"))
        team_end = comment.rfind("</a>", 0, comment.rfind("</a>"))
        team = comment[team_begin + 7: team_end]

        intro = intro + ", and played " + pos + \
            ' during his career, his last game being with the ' + team + ".\n"

    intro = intro + "Standing at" + height + " and weighing " + weight + ", " + draft + '\n'

    intro = intro + rings

    print(intro)


def player_stats() -> None:
    """Print the stats of the player in a table"""
    # all data in html comments
    all_comments = soup.find_all(string=lambda text: isinstance(text, Comment))

    tables = []
    for comment in all_comments:
        if 'table' in str(comment):
            try:
                tables.append(pd.read_html(comment, header=0)[0])
            except:
                continue

    print(tables[0].to_string())


# Execute functions
if check_valid():
    intro_paragraph()
    print("=============== CAREER STATS ===============")
    player_stats()
else:
    print("Input invalid, try again :(")
