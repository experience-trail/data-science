import datetime
import googlemaps
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import json
import os
import pytz

# Environment variables
GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']
GRAPHQL_URL = os.environ['GRAPHQL_URL']

# Initializing google client
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

# Initializing graphql client
expected_retries = 3
gql_client = Client(retries=expected_retries,
                    transport=RequestsHTTPTransport(url=GRAPHQL_URL))


def get_utc_time():
    """
    Returns UTC time in ISO format

    Output format.
    'YYYY-mm-ddTHH:MM:SS+HH:MM'

    '2019-08-01T10:43:30+00:00'
    """
    date = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    date = datetime.datetime(date.year, date.month, date.day,
                             date.hour, date.minute, int(date.second),
                             int(date.second * 1000000 % 1000000),
                             tzinfo=date.tzinfo)

    return date.isoformat()


def find_place(user_input):
    """
    Find the place using Google Place API.
    To get more accurate or specific place information, provide more details
    as part of input.

    Input: User provided place name
    Output: 0 or more locations matching the given name.
    """
    my_fields = ['name', 'photos', 'place_id', 'types', 'formatted_address']
    place_results = gmaps.places(query=user_input)
    return place_results


def fetch_place_details(place_id):
    """
    Fetch place details using Google Place API.

    Input: Place ID, unique identifier obtained as part of Google Place API
    based on user input.
    Output: Detailed information about the place as provided by Google Place
    API.
    """
    return gmaps.place(place_id)


def add_to_basers_db(place_id, place_details):
    """
    Add Place details obtained from Google Place API into local DB.
    This is done using GraphQL API for storing Base Recommendation System
    information.

    Input:
    1. Place ID
    2. Google Place Details
    """
    place_details_str = json.dumps(place_details)

    # Below clean up is needed to ensure the json data is in correct format
    # to be stored using GraphQL API.
    temp_str = place_details_str.replace('\\\"', "'")
    temp_str = temp_str.replace('"', '\\"')
    temp_str = temp_str.replace('\\n', '\\\\n')

    # GraphQL API for adding Place inforamation to be used for Base
    # Recommendation System.
    createBaseRSPlace = gql('''
    mutation createBaseRSPlace($place_id: String!,
                               $place_details: JSONString!,
                               $timestamp: CustomGrapheneDateTime!) {
      create_basers_place(place_data: {place_id: $place_id,
                                       google_place_details: $place_details,
                                       timestamp: $timestamp}) {
        place_id
        ok
        message
      }
    }
    ''')

    place_details = temp_str
    timestamp = get_utc_time()

    # Creating dynamic parameter list
    place_id_str = f'    "place_id": "{place_id}",\n'  # noqa: E999
    place_details_str = f'    "place_details": "{place_details}",\n'
    timestamp_str = f'    "timestamp": "{timestamp}"\n'
    params = "{\n"+place_id_str+place_details_str+timestamp_str+"}"

    return gql_client.execute(createBaseRSPlace, variable_values=params)


class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


if __name__ == "__main__":
    init_msg = "This script is used to find the place of interest and store "\
               "it for building \nbase recommedation system used in "\
               "Experience trail.\n"\
               "This is an interactive script and would require user inputs "\
               "as prompted."
    print(init_msg)

    while True:
        user_input = input("\nEnter the name of the place or q to exit: ")
        if user_input == 'q' or user_input == 'Q':
            print("Exiting...")
            break

        print(f"You entered {color.RED}{user_input}{color.END}")  # noqa: E999
        confirm = input("Enter y to confirm: ")

        if confirm != 'y' and confirm != 'Y':
            continue

        print(f"\nSearching for place {user_input}...")
        places = find_place(user_input)['results'][:10]
        places_count = len(places)
        print(f"Search result count: {places_count}")

        selected_place = None

        if places_count == 0:
            print("No matching place found for {user_input}.")
            continue

        elif places_count == 1:
            print(f"\n{places[0]['name']}")
            print(f"{places[0]['formatted_address']}\n")
            selected_place = places[0]

        else:
            for index, place in enumerate(places):
                print(f"\n{index}. {place['name']}")
                print(f"{place['formatted_address']}\n")

            while True:
                prompt1 = f"Select the index between 0 to {places_count-1} "
                prompt2 = "or q to exit: "

                prompt = prompt1+prompt2
                user_input = input(prompt)

                if user_input == 'q' or user_input == 'Q':
                    break

                try:
                    selected_index = int(user_input)

                    if selected_index < 0 or selected_index > (places_count-1):
                        raise ValueError

                    break

                except ValueError:
                    print("Not a valid input. Retry...\n")
                    continue

            # Special handling needed to go back to initial user prompt
            if user_input == 'q' or user_input == 'Q':
                print("Going back to initial prompt...")
                continue

            selected_place = places[selected_index]

        name = selected_place['name']
        address = selected_place['formatted_address']
        place_id = selected_place['place_id']

        print(f"You have selected {color.RED}{name}{color.END}")
        print(f"{color.RED}{address}{color.END}")
        confirm = input("Enter y to confirm: ")

        if confirm != 'y' and confirm != 'Y':
            continue

        print(f"\nFetching place details for {name}...")
        place_details_response = fetch_place_details(place_id)

        if place_details_response['status'] != 'OK':
            print(f"Failed to fetch details for {name}.")
            continue

        place_details = place_details_response['result']

        try:
            result = add_to_basers_db(place_id, place_details)
            if result['create_basers_place']['ok']:
                print(f"\n{name} is successfully added")
        except Exception:
            print("Failed to add place details into local DB")
