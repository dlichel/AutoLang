
#dmichel
#All sentence/semantic related functions.

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from nltk import word_tokenize          
from nltk.stem import WordNetLemmatizer
import nltk
from nltk.corpus import stopwords
import dataModify
#modify when done, disabled right now just to stop circular import.
#import data_cleaner
import time
import math
import random
import string

#deprecated.
hsk = 'sentences_HSK1.tsv'

#counts lines by counted every line. I feel like theres a better way to do this.

def count_lines(path, file):
    with open(path+file, 'r', encoding='utf-8') as fp:
        for count, line in enumerate(fp):
            pass
    return count+1

#Sentence class. I should probably name this better. But this is to help
#not restart everything every time a function is called.

class Sentence:
    def __init__(self, json):
        self.loaded = False
        self.status = 'Unloaded'
        self.json = json
        #self.cleaner = data_cleaner.Cleaner()
        self.hashFJ = {}
        self.hashJF = {}
        self.hsk = 1
        self.dat = None
        self.count = 0
        self.dataStruct = None
        #clean(self)
    
    #helps me determine if the hashes are loaded.
    def __bool__(self):
        if self.loaded:
            return True
        return False
    
    def __repr__(self):
        return self.status
    
    #This is temporarily disabled because the data does not need to be cleaned
    #though in future this will change.
    def clean(self):
        if bool(self.cleaner):
            return
        self.cleaner.clean()
        
    #If this is not done, the functions don't know how to relate the functions
    #to a central file.
    def setFile(self, file):
        if self.dataStruct.filename != file:
            self.dataStruct.setFile(file)
    
    #this needs to be called before anything related to semantic comparison
    #or database retrieval is done. The reason this is not initialized
    #is to make sure it doesn't load all at beginning, but when I want to.
    def load(self):
        try:
            nltk.download('punkt')
            
            self.status = 'Loaded.'
            self.loaded = True
            self.dataStruct = dataModify.Data()
        except:
            self.status = 'Already Loaded in nltk and stop_words.'
            
    #Certain files will have their data as lists, but these lists will be strings.
    #This will fix that and turn it to lists again.
    def recieveTranslations(self, dictionary):
        newString = dictionary.replace("[", "")
        newString = newString.replace("]", "")
        newString = newString.replace("(", "")
        newString = newString.replace(")", "")
        newString = newString.replace('"', "")
        alp = set()
        for i in string.ascii_letters:
            alp.add(i)
        newString = list(newString)
        for i in range(len(newString)):
            if newString[i] == "'":
                if newString[i-1] not in alp or newString[i+1] not in alp:
                    newString[i] = ""
        finalString = ''.join(newString)
        finalString = finalString.replace("\n", "")
        stringList = finalString.split(",")
        for i in range(len(stringList)):
            if i % 2 != 0:
                stringList[i] = stringList[i].strip()
                stringList[i] = int(float(stringList[i]))
        newList = []

        i = 0
        tempTuple = tuple()
        while i < len(stringList):
            tempTuple += (stringList[i],)
            if len(tempTuple) == 2:
                newList.append(tempTuple)
                tempTuple = tuple()
            i+=1
            
        return newList
    
    #translates simplified chinese to traditional chinese and vice versa. tizi
    #is whether the text itself is simplified or traditional, not the target
    #This works 99% of the time. Will not work with simplified 干 and 面 to traditional
    #always, as usually these will require contexts.
    def switch_tizi(self, phrase, tizi):
        newPhrase = ""
        if tizi == 'JIAN':
            for i in phrase:
                newPhrase += self.hashJF.get(i, i)
            return newPhrase
        if tizi == 'FAN':
            for i in phrase:
                newPhrase += self.hashFJ.get(i, i)
            return newPhrase
        else:
            raise Exception("tizi must either be a string of either JIAN or FAN.")
        
    #Detects whether it is simplified or traditional.
    #Works just about every time.
    #The reason it doesnt work 100% of the time is because
    #It relies on traditional and simplified characters from the entire
    #chinese dictionary. It has these translations
    #however it will sometimes have ancient translations that modern people
    #will not understand now. I have cleaned out most of these in code,
    #and cleaned a tiny bit manually, but I still don't know every traditional
    #character and when the simplified is used because the traditional is outdated.
    def detect_tizi(self, phrase):
        for i in phrase:
            if i in self.hashFJ:
                return 'FAN'
            if i in self.hashFJ.values():
                #print(i)
                return 'JIAN'
        return 'UNKNOWN'
    
    #IF YOU PLAN ON HAVING DETECT TIZI AND SWITCH TIZI, DO THIS
    def makeHashes(self, filename='oneCharTradSimpNew.txt'):
        self.dat = dataModify.Data()
        self.dat.hashMake2Cols(filename)
        self.hashFJ = self.dat.currentHash
        newDict = {}
        for i in self.hashFJ:
            newDict[self.hashFJ[i]] = i
        self.hashJF = newDict
    
    #Function deprecated as far as I know.
    def makeSentenceHash(self):
        self.dat = dataModify.Data()
        self.dat.hashMake2Cols('')
    
    #Will be like semantic compare v1 only that it will take into
    #account thesaurus and review rankings
    def rank_input_v2(self, ans, perfect):
        #ans is a string, perfect is a list of documents.
        print("SEMANTIC COMPARE V2")
    
    
    def rank_input(self, ans, perfect):
        
        #yeah this algorithm sucks but its fine for now
        
        #its a simple tokenizer algorithm. Vectorizes words as tokens and
        #makes a semantic comparison based off token. its ass.
        
        #modified version of https://gist.github.com/4OH4/f727af7dfc0e6bb0f26d2ea41d89ee55
        
        stop_words = set(stopwords.words('english'))
        tokenizer = LemmaTokenizer()
        token_stop = tokenizer(' '.join(stop_words))
        realWords = []
        for i in ans.split():
            if i not in stop_words:
                realWords.append(i)
        #print(realWords)
        
        perfectPhrase = perfect # find a way to get perfect phrase
        vectorizer = TfidfVectorizer(stop_words=token_stop, 
                                  tokenizer=tokenizer)
        doc_vectors = vectorizer.fit_transform([ans] + perfect)
        #print(doc_vectors)
        cosine_similarities = linear_kernel(doc_vectors[0:1], doc_vectors).flatten()
        document_scores = [item.item() for item in cosine_similarities[1:]]
        semantic_score = document_scores[0]
        ind = 0
        if len(document_scores) > 1:
            for i in range(len(document_scores)):
                if document_scores[i] > semantic_score:
                    semantic_score = i
                    ind = i
        
        return (semantic_score, perfect[ind])
    
    def add_sentence(self, sentence, translation, diffculty=1.0):
        pass
    
    #Finds a sentence to display. numRange is the range between each each index it randomizes
    #difficulty dtermines the start index. Mode determines which database it searches through,
    #and ignoreSet determines if it should reroll if the sentence is in the set.
    def findSentence(self, numRange=20, difficulty=1.0, mode=('HSK', 'STRICT'), ignoreSet = set()):
        hskLevel = math.floor(difficulty)
        #sigh. failed dream of having multiple modes. Technically
        #if you want to see them you can just fix the parameter where its called
        if mode[1] == 'STRICT' and mode[0] == 'HSK':
            filename = 'sentences_HSK'+str(hskLevel)+'.tsv'
        if mode[1] == 'MODERATE' and mode[0] == 'HSK':
            filename = 'allHSK_sentence_sort.tsv'
        if mode[0] == 'COMMON':
            filename = 'sentence_ranked_common.tsv'
        else:
            return self.randomSentence()
        self.setFile(filename)
        hskLevelFine = abs(difficulty - hskLevel)
        count = count_lines('Data/Databases/', filename)
        self.count = count
        lowerIndex = math.floor(count * (hskLevelFine))
        upperIndex = math.floor(lowerIndex + numRange)
        if upperIndex > count:
            upperIndex = count - 1
        index = random.randint(lowerIndex, upperIndex)
        phrase = self.dataStruct.indexedSentenceFromData(index)
        sentence = list(phrase['Phrase'].values())[0]
        #print(phrase)
        if sentence in ignoreSet:
            num = 0
            while sentence in ignoreSet:
                num+=1
                phrase = self.dataStruct.indexedSentenceFromData(index+num)
                sentence = list(phrase['Phrase'].values())[0]
                
        
        return phrase
        
    #determines the increase or decrease in level. Notice the 0.25. This is
    #easy mode. Medium will be 0.5, and hard is 0.75.
    def giveLevel(self, sentence_score, currentScore, numRange=20):
        #print(sentence_score)
        score = sentence_score[0] - 0.25 #sigh. This 0.25 was to change to 0.5 for medium difficulty, and 0.75 for hard.
        ans = currentScore + 2 * (score / (self.count / numRange))
        if ans < 1:
            ans = 1.0
        if ans > 6:
            ans = 6.99999
        return ans
    
    #the first version of sentence retrival, literally just grabs a random sentence,
    #only meant to test. Also this is the function called if both HSK and common
    #are set to None.
    def randomSentence(self):
        self.setFile('sentence-pairs.tsv')
        return self.dataStruct.randomSentenceFromData()
    
    
#Tokenizer. That you to Princeton's Wordnet Lemminizer. If this is too much,
#i will make a crude version myself.
class LemmaTokenizer:
    ignore_tokens = [',', '.', ';', ':', '"', '``', "''", '`']
    def __init__(self):
        self.wnl = WordNetLemmatizer()
    def __call__(self, doc):
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc) if t not in self.ignore_tokens]
    

def main():
    newMain = Compare()


    