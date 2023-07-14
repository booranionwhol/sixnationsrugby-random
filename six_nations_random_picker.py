import random
from time import sleep

import requests

headers = {
    "Authorization": "Token eyJ0...",
    "x-access-key": "600@1@",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36",
    "content-type": "application/json",
    "dnt": "1",
    "origin": "https://fantasy.sixnationsrugby.com",
    "pragma": "no-cache",
    "referer": "https://fantasy.sixnationsrugby.com/",
    "authority": "fantasy.sixnationsrugby.com",
    "accept": "application/json",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,en-GB;q=0.8",
    "cache-control": "no-cache",
}


pos_map = {
    '5': 'Fullback',
    '6': 'Wing',
    '7': 'Centres',
    "8": "Flyhalf",
    "9": "Scrumhalf",
    "10": "Looseforward",
    "11": "Lock",
    "12": "Prop",
    "13": "Hooker",

}
positions_to_fill = ['5', '6', '7', '7', '6', '8', '9',
                     '10', '10', '10', '11', '11', '12', '13', '12']


class Player():
    def __init__(self, data):
        image = data['imageclub']
        self.country = image.replace('m_rugby_', '').replace('.png', '')
        self.country = data['club']
        self.fullname = data['nomcomplet']
        self.value = data['valeur']
        self.occupied = data['occupe']  # maybe?
        self.id = int(data['id'])


# prep = requests.Request('POST',url,headers=headers,data=payload)
# pretty_print_POST(prep)
def get_player_list(position):
    payload = {
        "filters": {
            "nom": "",
            "club": "",
            "position": str(position),
            "budget_ok": False,
            "idj": "1",
            "pageIndex": 0,
            "pageSize": 50,
            "loadSelect": 0
        }
    }
    url = 'https://fantasy.sixnationsrugby.com/v1/private/searchjoueurs?lg=en'
    r = requests.post(url, json=payload, headers=headers)
    return r.json()


def get_squad_info():
    url = 'https://fantasy.sixnationsrugby.com/v1/private/feuillematch/1/166575?lg=en'
    r = requests.get(url, headers=headers)
    data = r.json()
    return data


def set_captain(player_id):
    url = 'https://fantasy.sixnationsrugby.com/v1/private/setrolejoueur?lg=en'
    payload = {
        'credentials': {
            "idj": "1",
            "idf": player_id,
            "action": "selectcap"
        }
    }
    r = requests.post(url, json=payload, headers=headers)
    if r.status_code == 200:
        return True
    else:
        return False


def pick_captain():
    squad = get_squad_info()
    players = squad['feuille']['postes']
    player = Player(random.choice(players))
    print(f'Setting player {player.fullname} as Captain ... ', end='')
    if set_captain(player.id):
        print('Success!')
    else:
        print('Fail!')


def assign_player(player_id):
    url = 'https://fantasy.sixnationsrugby.com/v1/private/actionsurjoueur?lg=en'
    payload = {
        'credentials': {
            "idj": "1",
            "idf": player_id,
            "action": "acheter",  # assign ?
            "numpostecible": ""  # auto-pick slot
        }

    }
    r = requests.post(url, json=payload, headers=headers)
    if r.status_code == 200:
        return True
    else:
        return False


def fill_all_positions():
    for position in positions_to_fill:
        data = get_player_list(position)
        players = data['joueurs']
        print(
            f'Found {len(players)} for position {pos_map[position]}. Shuffling')
        random.shuffle(players)
        for player in players:
            p = Player(player)
            if p.occupied:
                continue
            print(
                f'Trying to assign player {p.fullname}, country: {p.country}, value: {p.value} to position {position} ... ', end='')
            if assign_player(p.id):
                print(f'Success!')
                break
            else:
                print(f'Failed :(')
                # Try the next player in the loop
                sleep(2)
        sleep(2)
