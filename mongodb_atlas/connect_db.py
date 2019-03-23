import pymongo

#MONGODB ATLAS URL
DB_URI = 'mongodb+srv://fyp_admin:fyp_pwd@cluster0-oov30.mongodb.net/test?retryWrites=true'

def save_data(json_array, collection_name):
    client = pymongo.MongoClient(DB_URI)
    db = client.test
    collections = {
        'facebook': db.facebook,
        'articles_map': db.articles_map,
        'articles_web': db.articles_web,
        'twitter': db.twitter
    }
    collection = collections.get(collection_name)
    #db.collection.create_index( {"diseasetype": 1, "date": 1, "location": 1}, {unique:True})

    for data in json_array:
        try:
            #collection.insert_one(data).inserted_id
            collection.update(data, data, upsert=True) #Upsert parameter used to avoid duplicate data entries
        except:
            print("Failed to insert data to database")
        finally:
            client.close()

def save_trends(json_array):
    client = pymongo.MongoClient(DB_URI)
    db = client.test
    collection = db.googletrends
    try:
        collection.insert_one(json_array).inserted_id
    except:
        print("Failed to insert data to database")
    finally:
        client.close()

def retrieve_all():
    client = pymongo.MongoClient(DB_URI)
    db = client.test
    collections = {
        'facebook': db.facebook,
        'maurihealth': db.maurihealth,
        'twitter': db.twitter
    }
    result = []

    for collection in collections.values():

        input = collection.find({})
        for data in input:
            id = str(data['_id'])
            disease = data['diseasetype']
            date = data['date']

            result.append({"id": id, "disease": disease, "date": date})

    return result


def retrieve_info(query):
    client = pymongo.MongoClient(DB_URI)
    db = client.test
    collections = {
        'facebook': db.facebook,
        'maurihealth': db.maurihealth
    }
    result = []

    for collection in collections.values():

        input = collection.find({"diseasetype":query})
        for data in input:
            id = str(data['_id'])
            disease = data['diseasetype']
            date = data['date']

            result.append({"id":id, "disease":disease, "date":date})

    return result



