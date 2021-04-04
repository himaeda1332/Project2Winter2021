#################################
##### Name: Hisamitsu Maeda
##### Uniqname: himaeda
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key

BASE_URL = 'https://www.nps.gov'
INDEX_URL = '/index.htm'
CACHE_FILE_NAME = 'cache.json'
CACHE_DICT = {}

class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.

    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, name='no name', category='no category',
                    address='no address', zipcode='no zipcode',
                    phone='no phone'):
        self.category=category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone

    def info(self):
        '''
        Parameters
        ----------
        None

        Returns
        ----------
        string
            <name> (<category>): <address> <zip>
        '''
        return f'{self.name} ({self.category}): {self.address} {self.zipcode}'


def load_cache():
    ''' opens the cache file if it exists and loads the JSON into
    a dictionary, which it then returns.
    if the cache file doesn't exist, creates a new cache dictionary
    Parameters
    ----------
    None

    Returns
    -------
    The opened cache
    '''
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache


def save_cache(cache):
    ''' saves the current state of the cache to disk
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save

    Returns
    -------
    None
    '''
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    main_page_url = BASE_URL + INDEX_URL
    if main_page_url not in CACHE_DICT.keys():
        print("Fetching")
        response = requests.get(main_page_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        states_listing_parent = soup.find('div',
                class_="SearchBar-keywordSearch input-group input-group-lg")
        states_info = states_listing_parent.find_all('a')
        output = {}
        for state in states_info:
            output[state.text.lower()] = BASE_URL + state.attrs['href']
        CACHE_DICT[main_page_url] = output
        return output
    else:
        print("Using cache")
        return CACHE_DICT[main_page_url]


def get_site_instance(site_url):
    '''Make an instances from a national site URL.

    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov

    Returns
    -------
    instance
        a national site instance
    '''
    if site_url not in CACHE_DICT.keys():
        print("Fetching")
        response = requests.get(site_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        site_listing_parent = soup.find('div',
                class_="Hero-titleContainer clearfix")
        park_name_info = site_listing_parent.find('a').get_text().strip()
        category_info = site_listing_parent.find('span',
                                class_="Hero-designation").get_text().strip()
        category_info = category_info if category_info != '' \
                            else 'no category'
        info_listing_parent = soup.find('div', class_='vcard')
        address_info = info_listing_parent.find('span',
                            itemprop='addressLocality').get_text().strip()
        address_info = address_info if address_info != '' else 'no address'
        state_info = info_listing_parent.find('span',
                                itemprop='addressRegion').get_text().strip()
        state_info = state_info if state_info != '' else 'no state'
        address = address_info + ", " + state_info
        postal_info = info_listing_parent.find('span',
                                itemprop='postalCode').get_text().strip()
        postal_info = postal_info if postal_info != '' else 'no zipcode'
        phone_info = info_listing_parent.find('span',
                                itemprop='telephone').get_text().strip()
        phone_info = phone_info if phone_info != '' else 'no phone'
        CACHE_DICT[site_url] = {'name': park_name_info,
                                'category': category_info,
                                'address': address,
                                'zipcode': postal_info,
                                'phone': phone_info}
    else:
        print("Using cache")

    return NationalSite(name=CACHE_DICT[site_url]['name'],
                        category=CACHE_DICT[site_url]['category'],
                        address=CACHE_DICT[site_url]['address'],
                        zipcode=CACHE_DICT[site_url]['zipcode'],
                        phone=CACHE_DICT[site_url]['phone'])


def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.

    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov

    Returns
    -------
    list
        a list of national site instances
    '''
    if state_url not in CACHE_DICT.keys():
        print("Fetching")
        response = requests.get(state_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        site_listing_parent = soup.find('div',
                                id="parkListResultsArea")
        parks_info = site_listing_parent.find_all('h3')
        parks_list = []
        for park_info in parks_info:
            park_site = park_info.find('a')
            site_url = BASE_URL + park_site.attrs['href'] + INDEX_URL[1:]
            parks_list.append(site_url)
        CACHE_DICT[state_url] = parks_list
    else:
        print("Using cache")
        parks_list = CACHE_DICT[state_url]

    return [get_site_instance(site_url) for site_url in parks_list]


def print_national_sites(national_sites_list, state_name):
    '''Print list of national site instances.

    Parameters
    ----------
    national_sites_list: list
        A list of national site instances
    state_name: string
        State name

    Returns
    -------
    None
    '''
    print('-' * 34)
    print(f'List of national sites in {state_name}')
    print('-' * 34)
    for idx, national_site in enumerate(national_sites_list):
        print(f'[{idx+1}]', national_site.info())
    print()


def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.

    Parameters
    ----------
    site_object: object
        an instance of a national site

    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    zipcode = site_object.zipcode
    url = 'http://www.mapquestapi.com/search/v2/radius'
    params = {'key': secrets.API_KEY, 'origin': zipcode, 'radius': 10,
            'maxMatches': 10, 'ambiguities': 'ignore', 'outFormat': 'json'}

    if zipcode not in CACHE_DICT.keys():
        print("Fetching")
        response = requests.get(url, params=params).json()
        CACHE_DICT[zipcode] = response
    else:
        print("Using cache")

    return CACHE_DICT[zipcode]


def print_nearby_places(nearby_places, park_name):
    '''print nearby places from MapQuest API.

    Parameters
    ----------
    nearby_places: dict
        result from MapQuest API
    park_name: string
        park name of NationalSite object

    Returns
    -------
    None
    '''
    places = nearby_places['searchResults']
    print('-' * 34)
    print(f'Places near {park_name}')
    print('-' * 34)
    for place in places:
        category = place['fields']['group_sic_code_name'] if\
            place['fields']['group_sic_code_name'] != '' else 'no category'
        address = place['fields']['address'] if\
            place['fields']['address'] != '' else 'no address'
        city = place['fields']['city'] if\
            place['fields']['city'] != '' else 'no city'
        print('-', place['name'], f'({category}): {address}, {city}')
    print()


if __name__ == "__main__":

    CACHE_DICT = load_cache()
    states_dict = build_state_url_dict()
    program_flag = True

    while program_flag:
        message1 = 'Enter a state name (e.g. Michigan, michigan) or "exit": '
        message2 = 'Choose the number for detail search or "exit" or "back": '
        state_name = input(message1).lower()
        if state_name == 'exit':
            print('Bye!')
            break
        elif state_name not in states_dict.keys():
            print("[ERROR] Enter proper state name")
            print()
        else:
            state_url = states_dict[state_name]
            nationalsite_list = get_sites_for_state(state_url)
            print_national_sites(nationalsite_list, state_name)

            while True:
                number = input(message2)
                if number.isdecimal() and \
                    (1 <= int(number) <= len(nationalsite_list)):
                    national_site = nationalsite_list[int(number)-1]
                    nearby_places = get_nearby_places(national_site)
                    print_nearby_places(nearby_places, national_site.name)
                elif number == 'exit':
                    program_flag = False
                    print('Bye!')
                    break
                elif number == 'back':
                    print()
                    break
                else:
                    print("[ERROR] Invalid input")
                    print()
                    print('-' * 34)

    save_cache(CACHE_DICT)