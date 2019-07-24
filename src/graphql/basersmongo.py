import pymongo
import os


# Environment variables
mongodb_url = os.environ['MONGODB_URL']

client = pymongo.MongoClient(mongodb_url)
db = client["experiencetrail"]
col = db["basersplaces"]


def insert_to_basers_mongodb(_id, timestamp, data):
    # Check if _id already exists, if so update.
    query = {"_id": _id}
    doc = col.find_one(query)

    if doc is None:
        insert_dict = {"_id": _id, "timestamp": timestamp,
                       "google_place_details": data}
        result = col.insert_one(insert_dict)

        if result.inserted_id != _id:
            print(f"Error! Insert to MongoDB failed for {_id}")  # noqa: E999
            return False

        return True

    updatevalues = {"$set": {"timestamp": timestamp,
                             "google_place_details": data}}

    result = col.update_one(query, updatevalues)

    if (result.matched_count != 1):
        print(f"Error! Update on MongoDB failed for {_id}")
        return False

    return True


def find_in_basers_mongodb(_id):
    query = {"_id": _id}
    return col.find_one(query)


def findall_in_basers_mongodb():
    all_records = col.find({})
    all_ids = []
    for record in all_records:
        all_ids.append(record["_id"])

    return all_ids


def delete_from_basers_mongodb(_id):
    query = {"_id": _id}
    result = col.delete_one(query)

    if result.deleted_count != 1:
        print(f"Error! Delete on MongoDB failed for {_id}")
        return False

    return True
