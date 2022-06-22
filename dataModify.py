import time
import numpy as np
import pandas as pd
import os
import json
import random


path = 'Data/Databases/'

class Data:
    def __init__(self):
        self.sentenceFile = None
        self.filename = None
        self.currentHash = {}
        self.sentence_hash = {}
        self.file = self.sentenceFile
        
    def __repr__(self):
        return str(self.sentenceFile.shape)
    
    #sets the file
    def setFile(self, filename):
        try:
            self.filename = filename
            if filename[-3:] == "csv":
                self.file = pd.read_csv(path+filename)
            else:
                self.file = pd.read_csv(path + filename, sep="\t")
        except:
            print("Import Fail. Make sure spelt correct, csv or tsv, and in " + path)
    
    #loads all json
    def loadSaves(self, filename, filePath=path):
        with open(filePath + filename) as json_file:
            data = json.load(json_file)
        json_file.close()
        return data
    
    #grabs a random sentence
    def randomSentenceFromData(self):
        database = self.file
        num = random.randint(0,len(self.file))
        info = database.iloc[[num]].to_dict()
        return info
    
    #returns whatever sentence from index
    def indexedSentenceFromData(self, index):
        database = self.file
        info = database.iloc[[index]].to_dict()
        return info
    
    #Same thing as random sentence, just if you are using multiple files.
    def randomSentenceFromFile(self, filename):
        file = pd.read_csv(path+filename, sep="\t")
        num = random.randint(0,len(file))
        info = file.iloc[[num]].to_dict()
        return info
    
    
    #make a hash with whatever specified columns you give.        
    def hashMake2Cols(self, filename, encoding='utf-8', tag = None, col1 = 0, col2 = 1):
        try:
            f = open(path + filename, 'r', encoding=encoding)
            for i in f.readlines():
                splitString = i.split()
                self.currentHash[splitString[col1]] = splitString[col2]
        except:
            raise Exception("Unable to parse .txt file")
    
    #determines what each file is seperated by.
    #if none, returns none
    def findSeperation(self, filename, path_toFile = path, encoding='utf-8'):
        if filename[-3:] == "csv":
            return ','
        elif filename[-3:] == "tsv":
            return '\t'
        else:
            try:
                f = open(path_toFile + filename, 'r', encoding=encoding)
                line = f.readline()
                sep = set()
                for i in line:
                    if i.isalnum() == False:
                        sep.add(i)
                if len(sep) == 1:
                    for i in sep:
                        return sep
            except:
                return None
            return None
    
    #deprecated
    def hashMake2ColsSV(self, filename):
        try:
            file = pd.read_csv(path+filename, sep=findSeperation(filename))
            
        except:
            raise Exception("Unable to parse csv or tsv")
    
    #makes a JSON from a file, meant to convert file to dictionary for easy use.
    def makeJSONfromFile(self, filename, jsonname):
        if jsonname in os.listdir(path):
            return
        try:
            #print(findSeperation(filename))
            file = pd.read_csv(path+filename, sep=self.findSeperation(filename))
        except:
            raise Exception("Could not read file.")
        for i in range(len(file)):
            
            row = file.iloc[[i]].to_dict()
            #print(row)
            #print(list(row['Phrase'].values())[0])
            #print(list(row['Translation'].values())[0])
            key = list(row['Phrase'].values())[0]
            valTuple = (list(row['Translation'].values())[0], list(row['ID'].values())[0])
            if key in self.sentence_hash:
                self.sentence_hash[key].append(valTuple)
            else:
                self.sentence_hash[key] = [valTuple]
        #json_data = json.dumps(start_data, indent = 4)
        with open(path + 'sentences.json', 'w') as p:
            json.dump(self.sentence_hash, p, indent=4)
        p.close()
            #self.sentence_hash[row['Phrase'].values()[0]] = [row[]]
    
#     def sortJSON(self, jsonname, sortBy, sortedFile='sortedJSON.json', overwrite=False, encoding='utf-8'):
#         files = os.listdir(path)
#         try:
#             assert(jsonname in files)
#         except:
#             raise Exception("Unable to open " + jsonname+". Check Path: " + path)
#         try:
#             if overwrite == False:
#                 assert(sortedFile not in files)
#         except:
#             raise Exception("File " + sortedFile + " already in " + path + ", Enable overwrite to overwrite.")
#         if sortBy[-3:] == 'tsv' or sortBy[-3:] == 'csv':
#             data = pd.read_csv(path+sortBy, sep=self.findSeperation(filename))
#         elif sortBy[-3:] == 'txt':
#             data = open(path+sortBy, 'r', encoding=encoding)
#         elif type(sortBy) == list:
#             
#         else:
#             raise Exception("Unable to sort.")
        
        
        
    
        
    


        