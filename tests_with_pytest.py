import requests, json
import bs4 as bs

test_request = 'http://antoniusblock.pythonanywhere.com/game/23'
def test_request_wrong_id_form():
    add_response = requests.get(test_request.replace('23', 'gid23'))
    assert bs.BeautifulSoup(add_response.text, 'lxml').text == \
           'requested game_id should be integer'

def test_request_no_creds():
    add_response = requests.get(test_request)
    assert bs.BeautifulSoup(add_response.text, 'lxml').text == \
           'requested game 23 but no authentication attempted'

def test_request_wrong_data():
    data = {'lname':'Koukos', 'fname':'Niko'}
    add_response = requests.post(test_request, json=data)
    assert bs.BeautifulSoup(add_response.text, 'lxml').text == \
           'missing credentials'

def test_request_no_such_un():
    data = {'username':'Koukos', 'password':'Niko'}
    add_response = requests.post(test_request, json=data)
    assert bs.BeautifulSoup(add_response.text, 'lxml').text == \
           'incorrect username or password (u)'

def test_request_no_wrong_pw():
    data = {'username':'bob', 'password':'Niko'}
    add_response = requests.post(test_request, json=data)
    assert bs.BeautifulSoup(add_response.text, 'lxml').text == \
           'incorrect username or password (p)'

def test_request_no_such_game():
    data = {'username':'bob', 'password':'bob_pw'}
    add_response = requests.post(test_request.replace('23','24'), json=data)
    assert bs.BeautifulSoup(add_response.text, 'lxml').text == \
           'requested game_id missing'

def test_good_request():
    data = {'username':'bob', 'password':'bob_pw'}
    add_response = requests.post(test_request.replace('23','123'), json=data)
    assert bs.BeautifulSoup(add_response.text, 'lxml').text == \
           '{\n  "data": "a", \n  "game_id": 123\n}\n'

