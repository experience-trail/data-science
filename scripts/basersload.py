import googlemaps
import os

# Environment variables
GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']

# Initializing client
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)


def find_place(user_input):
    my_fields = ['name', 'photos', 'place_id', 'types', 'formatted_address']
    place_results = gmaps.places(query=user_input)
    return place_results


def fetch_place_details(place_id):
    return gmaps.place(place_id)


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

        place_details_result = place_details_response['result']

        print(place_details_result)
