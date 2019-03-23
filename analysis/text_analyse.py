import nltk
from nltk import sent_tokenize
from fuzzywuzzy import process
#nltk.download('punkt')
import string
from nltk.corpus import stopwords
from nltk.tokenize.toktok import ToktokTokenizer
import re

tokenizer = ToktokTokenizer()
stopword_en_list = nltk.corpus.stopwords.words('english')
stopword_fr_list = nltk.corpus.stopwords.words('french')

stopword_list = stopword_en_list + stopword_fr_list

# DISEASE TERMS FOR FUZZY STRING MATCHING
diseaseterms = ['influenza', 'gastroenteritis', 'conjunctivitis', 'respiratory infection',
                'infectious disease',
                'diarrhea', 'pink eye', 'got gastro', 'got flu', 'disease virus', 'coughing', 'cough',
                'caught cold',
                'high fever', 'fever', 'headache', 'aches and pains', 'sore throat', 'dizziness',
                'vomiting',
                'stomach pain', 'cramps', 'nausea', 'dehydration', 'eye redness', 'itching of eye',
                'eye swelling',
                'eye tearing', 'sneezing', 'nasal congestion', 'runny nose', 'nasal breathing', 'diarrhée',
                'conjonctivite', 'grippe', 'gastro-entérite', 'infection respiratoire',
                'maladie infectieuse',
                'gastro', 'virus', 'toux', 'pris froid',
                'forte fièvre', 'fièvre', 'maux tête', 'douleurs', 'maux gorge', 'vertiges',
                'vomissement', 'symptômes',
                'douleurs estomac', 'crampes', 'nausées', 'déshydratation', 'rougeur yeux',
                'démangeaisons oculaires',
                'gonflement yeux',
                'larmoiement yeux', 'éternuements', 'congestion nasale', 'nez qui coule', 'respiration nasale', 'h1n1']
influenza = ['influenza', 'got flu','coughing', 'cough','caught cold','high fever', 'fever', 'headache', 'aches and pains', 'sore throat',
             'sneezing','grippe', 'toux','forte fièvre', 'fièvre', 'maux tête', 'douleurs', 'maux gorge',
             'éternuements', 'h1n1']
gastroenteritis = ['gastroenteritis', 'got gastro', 'diarrhea','dizziness',
                'vomiting','stomach pain', 'cramps', 'nausea', 'dehydration', 'diarrhée','gastro-entérite','gastro', 'virus', 'vertiges',
                'vomissement', 'symptômes',
                'douleurs estomac', 'crampes', 'nausées', 'déshydratation']
conjunctivitis = ['conjunctivitis','pink eye','eye redness', 'itching of eye',
                'eye swelling', 'eye tearing','conjonctivite','rougeur yeux',
                'démangeaisons oculaires',
                'gonflement yeux','larmoiement yeux']
respiratory_infection = ['respiratory infection', 'congestion nasale', 'nez qui coule', 'respiration nasale', 'h1n1','nasal congestion', 'runny nose', 'nasal breathing', 'infection respiratoire' ]

disease_list = [];
disease_list.insert(0, influenza)
disease_list.insert(1, gastroenteritis)
disease_list.insert(2, conjunctivitis)
disease_list.insert(3, respiratory_infection)

# LOCATION TERMS FOR FUZZY STRING MATCHING
places_terms = ['port louis', 'beau bassin', 'rose hill', 'moka', 'curepipe', 'quatre bornes', 'vacoas', 'phoenix',
                    'plaines wilhems', 'reduit', 'rivière noire', 'albion', 	'rivière du rempart',
                    'flacq', 'arsenal', 'baie du cap', 'pamplemousses', 'baie du tombeau', 'bambous',
                    'savanne', 'grand port', 'beau vallon', 'bel air rivière seche', 'bel ombre', 'benares',
                    'bois cheri',
                    'bon accueil', 'brisee verdiere', 'britannia', 'calebasses', 'camp carol',
                    'camp de masque', 'camp diable', 'camp ithier', 'camp thorel', 'cap malheureux', 'cascavelle',
                    'case noyale', 'chamarel', 'chamouny', 'chemin grenier', 'flic en flac', 'goodlands', 'grand baie',
                    'grand bel air', 'grand bois', 'grand gaube', 'grande riviere noire', 'la flora', 'lalmatie',
                    'mahebourg', 'mapou', 'midlands', 'pailles', 'plaine magnien', 'riviere des anguilles',
                    'rose belle', 'pereybere'
                    'saint pierre', 'souillac', 'surinam', 'tamarin', 'terre rouge', 'triolet', 'verdun', 'choisy', 'plaisance', 'belle mare']

def remove_stopwords(text, is_lower_case=False):
    tokens = tokenizer.tokenize(text)
    tokens = [token.strip() for token in tokens]
    if is_lower_case:
        filtered_tokens = [token for token in tokens if token not in stopword_list]
    else:
        filtered_tokens = [token for token in tokens if token.lower() not in stopword_list]
    filtered_text = ' '.join(filtered_tokens)
    return filtered_text

def remove_special_characters(text, remove_digits=False):
    pattern = r'[^a-zA-z0-9\s]' if not remove_digits else r'[^a-zA-z\s]'
    text = re.sub(pattern, '', text)
    return text

#---- FUNCTIONS extract_location AND extract_disease IMPLEMENTS TEXT ANALYSIS---#

def extract_location(content, score):
    sentences = sent_tokenize(content)
    # convert to lower case
    tokens = [w.lower() for w in sentences]

    location = ""

    for token in tokens:
        #print(token)

        tok = remove_stopwords(token)

        x = process.extractOne(tok, places_terms, score_cutoff=score)

        if x is not None:
            location = location + str(x)
            break;
    result = remove_special_characters(location, True)

    return result

def extract_disease(content, score):
    sentences = sent_tokenize(content)
    # convert to lower case
    tokens = [w.lower() for w in sentences]
    disease = ""
    sent = ""

    for token in tokens:
        #print(token)

        tok = remove_stopwords(token)

        print(tok)
        x = process.extractOne(tok, diseaseterms, score_cutoff=score)

        if x is not None:
            disease = disease + str(x)
            sent = sent + token
    return disease, sent

def ext_disease(content, score):
    sentences = sent_tokenize(content)
    # convert to lower case
    tokens = [w.lower() for w in sentences]
    word = ""
    sent = ""

    for token in tokens:
        print(token)

        tok = remove_stopwords(token)

        print(tok)
        for disease in disease_list:
            x = process.extractOne(tok, disease, score_cutoff=score)
            if x is not None:
                word = word + disease[0]
                sent = sent + token

    return word, sent