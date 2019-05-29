import nltk
from nltk import sent_tokenize
from fuzzywuzzy import process
nltk.download('punkt')

# DISEASE TERMS FROM TWITTER FOR FUZZY STRING MATCHING
disease_influenza = ['influenza', 'flu', 'fever', 'fièvre','toux','grippe','dizziness','coughing','cough','vertiges']
disease_conjunctivitis = ['conjunctivitis','conjonctivite','pinkEye']
disease_gastroenteritis = ['gastroenteritis', 'gastro', 'gastro-entérite', 'vomissement','vomiting','vomit','cramps','crampes','diarrhea','diarrhée']
disease_respiratoryInfection = ['respiratory Infection', 'Infection Respiratoire']

# LOCATION TERMS FOR FUZZY STRING MATCHING
places_terms = ['port louis', 'beau bassin', 'rose hill', 'curepipe', 'quatre bornes', 'vacoas', 'phoenix',
                    'plaines wilhems', 'moka', 'reduit', 'rivière noire', 'albion', 'amaury', '	rivière du rempart',
                    'flacq', 'anse la raie', 'arsenal', 'baie du cap', 'pamplemousses', 'baie du tombeau', 'bambous',
                    'savanne', 'grand port', 'beau vallon', 'bel air rivière sèche', 'bel ombre', 'benares',
                    'bois cheri',
                    'bois des amourettes', 'bon accueil', 'brisee verdiere', 'britannia', 'calebasses', 'camp carol',
                    'camp de masque', 'camp diable', 'camp ithier', 'camp thorel', 'cap malheureux', 'cascavelle',
                    'case noyale', 'chamarel', 'chamouny', 'chemin grenier', 'flic en flac', 'goodlands', 'grand baie',
                    'grand bel air', 'grand bois', 'grand gaube', 'grande riviere noire', 'la flora', 'lalmatie',
                    'mahebourg', 'mapou', 'midlands', 'pailles', 'plaine magnien', 'riviere des anguilles',
                    'rose belle',
                    'saint pierre', 'souillac', 'surinam', 'tamarin', 'terre rouge', 'triolet', 'tyack', 'verdun']


#---- FUNCTIONS extract_location AND extract_disease IMPLEMENTS TEXT ANALYSIS---#

def extract_location(content, score):
    sentences = sent_tokenize(content)
    # convert to lower case
    tokens = [w.lower() for w in sentences]

    location = ""

    for token in tokens:
        print(token)
        x = process.extractOne(token, places_terms, score_cutoff=score)

        if x is not None:
            location = location + str(x)

    return location

def extract_disease(content, score):
    sentences = sent_tokenize(content)
    # convert to lower case
    tokens = [w.lower() for w in sentences]
    disease = ""

    for token in tokens:
        print(token)
        influenza = process.extractOne(token, disease_influenza, score_cutoff=score)
        conjunctivitis = process.extractOne(token, disease_conjunctivitis, score_cutoff=score)
        gastroenteritis = process.extractOne(token, disease_gastroenteritis, score_cutoff=score)
        respiratoryInfection = process.extractOne(token, disease_respiratoryInfection, score_cutoff=score)

        if influenza is not None:
            disease = disease + str(influenza) + ",influenza"
        elif conjunctivitis is not None:
            disease = disease + str(conjunctivitis) + ",conjunctivitis"
        elif gastroenteritis is not None:
            disease = disease + str(gastroenteritis) + ",gastroenteritis"
        elif respiratoryInfection is not None:
            disease = disease + str(respiratoryInfection) + ",respiratoryInfection"
        else:
            disease = disease
    return disease

