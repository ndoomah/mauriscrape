import json
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener

from geopy.geocoders import Nominatim
from analysis import text_analyse
import string
geolocator = Nominatim(user_agent="my-application")
from mongodb_atlas import connect_db
##



#This is the listener, resposible for receiving data
class StdOutListener(StreamListener):

    def on_connect(self):
        print('Stream starting...')


    def on_status(self, status):

        #keywords to search in tweets
        keyword = ["flu", "influenza", "fever", "fièvre", "toux", "gastro", "gastroenteritis", "conjunctivitis", "diarrhea", "pinkeye", "coughing", "cough", "dizziness", "vomiting", "cramps", \
                 "sneezing", "diarrhée", "conjonctivite", "grippe", "gastro-entérite", "vertiges", "vomissement", "crampes", "éternuements", "respiratoire", "respiratory infection", "infection respiratoire"]

        #keyword = "flu", "influenza", "fever", "fièvre", "toux", "gastro", "gastroenteritis", "conjunctivitis", "diarrhea", "pinkeye", "coughing", "cough", "dizziness", "vomiting", "cramps", \
         #         "sneezing", "diarrhée", "conjonctivite", "grippe", "gastro-entérite", "vertiges", "vomissement", "crampes", "éternuements", "respiratoire", "respiratory infection"
        #print decoded
        random_user = ''
        #Check for presence of coordinates
        if status.geo is None: #coordinates not found for tweets

              for word in keyword: #search for word in keyword
                if word in status.text.lower():
                    random_text = status.text
                    location_result = text_analyse.extract_location(status.text.lower(), 80)
                    dis = text_analyse.extract_disease(status.text.lower(), 60)
                    # replacing punctuations with whitespace for location_result and tweet
                    for char in string.punctuation:
                        s = location_result.replace(char, ' ')
                        s1 = dis.replace(char, ' ')
                    # removing numbers from location_result and tweet
                    locresult = ''.join([i for i in s if not i.isdigit()])
                    disresult = ''.join([i for i in s1 if not i.isdigit()])

                    ######################################
                    # location mentionned in tweet
                    if locresult != "":
                        values = dis.split(',')
                        disease = values[-1]
                        # get latitude and longitude of mentionned location in tweet using Nominatim
                        location = geolocator.geocode(locresult + ", Mauritius")
                        lat = location.latitude
                        long = location.longitude
                        date = str(status.created_at.date())
                        # inserting in MongoDB Cloud
                        mylist = {"diseasetype": (disease), "date": (date), "Tweet": (status.text),
                                  "latitude": (location.latitude), "longitude": (location.longitude)}
                        connect_db.save_tweet(mylist)

                    if locresult == "":
                        print("Location not found in tweet!!!")
                        print("location")
                        print(location_result)
                        print("disease")
                        print(dis)
                        values = dis.split(',')
                        disease = values[-1]
                        date = str(status.created_at.date())
                        print(date)
                        latitude = "not found"
                        longitude = "not found"
                        mylist = {"diseasetype": (disease), "date": (date), "Tweet": (status.text),
                                  "latitude": (latitude), "longitude": (longitude)}
                        connect_db.save_tweet(mylist)

                    ######################################

        #return True
        #coordinates available for tweets
        else:
            for word in keyword:
                if word in status.text.lower():
                    print("coordinates available")
                    print(status.text)

                    ######################
                    dis = text_analyse.extract_disease(status.text.lower(), 60)
                    # print(dis)
                    # replacing punctuations with whitespace for location_result
                    for char in string.punctuation:
                        s1 = dis.replace(char, ' ')
                        # removing numbers from s
                        disresult = ''.join([i for i in s1 if not i.isdigit()])

                    # example output: return value('dizziness', 100),influenza
                    # a, b, c = dis.split(',', 3)
                    values = dis.split(',')
                    disease = values[-1]
                    geo = status.geo.get("coordinates")
                    lat = geo[0]
                    long = geo[1]
                    coordinates = lat, long
                    ##print(coordinates)
                    location = geolocator.reverse(coordinates)
                    ##print(location)

                    date = str(status.created_at.date())
                    ##reverse
                    location = geolocator.reverse(coordinates)

                    # LOCATION COORDINATES ARE AVAILABLE
                    print("DISEASE:")
                    print(disease)
                    print("TWEET:")
                    print(status.text)
                    print("DATE:")
                    print(date)
                    print("COORDINATES:")
                    print(geo)

                    mylist = {"diseasetype": (disease), "date": (date), "Tweet": (status.text),
                              "latitude": (lat), "longitude": (long)}
                    connect_db.save_tweet(mylist)
                    ######################


    def on_error(self, status):
        print(status)

if __name__ == '__main__':
    listener = StdOutListener()
    auth = OAuthHandler("lYtWk9zDUTG5iohmJnAhGaLBz", "RChpOgv4lUwxryUtflUgWZgzedoL3uv5ezK6CJx6ZfSkyPDTj5")
    auth.set_access_token("1041265000659054592-L00DvaSD5EDWdQsEv8pSgg3ha1YOEs",
                          "sM1SIyHRMs1IrqksMT6IOB8eSE4ApA7BNcBoK7DZWm2dk")
    stream = Stream(auth, listener)
    print("Showing all new tweets:")
    stream.filter(locations=[56.567, -20.522, 73.567, 10.4])



