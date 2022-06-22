import pandas as pd
import numpy as np
import os
import json
import string
import sentence_translation
import csv
import time

#NOT MEANT TO BE RUN BY MAIN


path = "Data/saves/"
database_path = "Data/Databases/"

class Cleaner:
    def __init__(self):
        self.cleaned = False
        self.saves_set = False
        self.saves = []
    def __bool__(self):
        return self.cleaned
    def clean(self):
        if self.cleaned:
            return
        pass
        
    #sets up the json files if they are gone.
    def setup_saves(self):
        if self.saves_set:
            return
        for i in os.listdir(path):
            if i.endswith('.json'):
                self.saves.append(i)
        if self.saves == []:
            for i in range(3):
                j = open(path + f'save{i+1}' + ".json", 'w')
                j.close()
        tempList = []
        for i in os.listdir(path):
            if os.stat(path + i).st_size != 0:
                tempList.append(i)
        if len(os.listdir(path)) == len(tempList):
            return
        start_data = {'level':1.0,'hsk':1,'options':{'tizi':'JIAN','pinyin':True,
                                                     'zhuyin':False,'loading_screen':'loading2.gif','font_size':30},
                      'sentences_practiced':[],'hsk_adherence':'MODERATE','common_adherence':'NONE','random':False,
                      'sentences':20, 'num_practiced':0}
        json_data = json.dumps(start_data, indent = 4)
        #with open(path+"save1.json", "w") as p:
        #    json.dump(start_data, p)
        for i in os.listdir(path):
            with open(path + i, 'w') as p:
                json.dump(start_data, p, indent=4)
        if 'saveuse.txt' not in os.listdir(path):
            with open(path + 'saveuse.txt', 'w') as p:
                p.write('save1.json')
    
    #generates a filter ignore list to leave room for only hanzi detection, and from
    #a file.
    def genFilterIgnoreList(self, filter_file='sorted_hsk1.csv'):
        list1 = []
        for i in range(len(filter_file)):
            row = filter_file.iloc[[i]].to_dict()
            #print(row)
            list1.append(row['char'][i])
        for i in string.ascii_letters:
            list1.append(i)
        for i in string.digits:
            list1.append(i)
        for i in string.punctuation:
            list1.append(i)
        list1.append('。')
        list1.append('…')
        list1.append('！')
        list1.append('？')
        list1.append('?')
        list1.append('、')
        list1.append('!')
        list1.append('，')
        return list1
    
    #basic ignore list, only punctuation and everything.
    def genBasicIgnoreList(self):
        list1 = []
        for i in string.ascii_letters:
            list1.append(i)
        for i in string.digits:
            list1.append(i)
        for i in string.whitespace:
            list1.append(i)
        for i in string.punctuation:
            list1.append(i)
        list1.append('。')
        list1.append('…')
        list1.append('！')
        list1.append('？')
        list1.append('?')
        list1.append('、')
        list1.append('!')
        list1.append('，')
        return list1
        
    #how I made the HSK Strict Files.            
    def format_hskModeStrict(self, hsk='1', encoding='utf-8'):
        print("formatting..")
        file = pd.read_csv(database_path+'sentence-pairs.tsv', sep='\t')
        filter_file = pd.read_csv(database_path+'sorted_hsk'+hsk+'.csv')
        hash1 = {}
        #a set is used cause my computer is bad so efficiency matters
        list1 = self.genFilterIgnoreList(filter_file)
        c = sentence_translation.Sentence('test.json')
        c.makeHashes()
        
        d = {}
        for i in range(len(file)):
            row = file.iloc[[i]].to_dict()
            #print(row)
            sentence = row['Phrase'][i]
            if c.detect_tizi(sentence) == 'FAN':
                sentence = c.switch_tizi(sentence, 'FAN')
            if self.verifyForHSK(sentence, list1):
                if d.get(sentence) == None:
                    d[sentence] = [[row['Translation'][i], row['ID'][i]]]
                else:
                    d[sentence].append([row['Translation'][i], row['ID'][i]])
        print(d)
        return d
    
    #if you file only relies on one hanzi, you can speed up sentence searching
    #exponentially by having this use sets instead of lists, faster.
    def format_algorithm_with_set(self, filename, output='sentence_ranked_common.tsv'):
        print("starting..")
        finalDict = {}
        file = pd.read_csv(database_path+filename, sep='\t')
        #filter_file = pd.read_csv(database_path+filter_file)
        wordList = self.genBasicIgnoreList()
        print("files read.")
        print("starting sorting.")
        sentenceSet = set()
        common_list = self.make_list_from_txt_col('sorted.txt')
        wordSet = set(wordList)
        #print(wordSet)
        wordDict = {}
        #hsk_file = pd.read_csv(database_path+'all_hsk.csv')
        print("hashing done.")
        
        for i in range(len(file)):
            row = file.iloc[[i]].to_dict()
            wordDict[row['Phrase'][i]] = [[row['Translation'][i], row['ID'][i]]]
            
        print("made dictionary.")
        index = 0
        print("starting..")
        
        for i in range(len(common_list)):
            sentenceSet = set()
            wordSet.add(common_list[i])
            for j in wordDict:
                string = j
                valid = True
                for k in string:
                    if k not in wordSet:
                        valid = False
                        break
                if valid:
                    sentenceSet.add(j)
                    finalDict[j] = wordDict[j]
            for s in sentenceSet:
                wordDict.pop(s)
            if i % 100 == 0:
                print(f'{i} / {len(common_list)} and len of {len(wordDict)}')
        
        print(finalDict)
        print(len(finalDict))
        f = open(database_path+output, 'w', encoding='utf-8')
        for i in finalDict:
            f.write(str(i) + '\t' + str(finalDict[i]) + '\n')
        print(f'wrote to {output}. Done.')
    
    #How I made the main file, HSK Moderate. Takes long to generate, since it
    #relies on searching a list (since this needs to be an ordered search)
    #can take a couple hours dependent on your machine.
    def format_algorithm(self,filename, filter_file, output='sentence_ranked_HSK.tsv'):
        print("starting..")
        #wordList = []
        finalDict = {}
        file = pd.read_csv(database_path+filename, sep='\t')
        filter_file = pd.read_csv(database_path+filter_file)
        wordList = self.genBasicIgnoreList()
        print("files read.")
        c = sentence_translation.Sentence('test.json')
        c.makeHashes()
        print("hashes made.")
        print("starting sorting.")
        sentenceSet = set()
        wordSet = set(wordList)
        #print(wordSet)
        setList = [set(), set(), set(), set(), wordSet]
        wordDict = {}
        hsk_file = pd.read_csv(database_path+'all_hsk.csv')
        hskSet = set()
        #for i in range(len(hsk_file)):
        #    hskSet.add(hsk_file.iloc[[i]].to_dict()['char'][i])
        
        for i in range(len(file)):
            row = file.iloc[[i]].to_dict()
            
            #if self.verify(row['Phrase'][i], hskSet):
            wordDict[row['Phrase'][i]] = [[row['Translation'][i], row['ID'][i]]]
            
        wordDictForHSK = {}
        for i in range(len(filter_file)):
            time1 = time.time()
            indexSet = set()
            hsk = filter_file.iloc[[i]].to_dict()
            setListInd = (len(setList) - 1) - len(hsk['char'][i])
            setList[setListInd].add(hsk['char'][i])
            #print(wordList)
            for j in wordDict:
                if self.verifybyHash(j, setList):
                    indexSet.add(j)
                    finalDict[j] = wordDict[j]
                    sentenceSet.add(j)
            for k in indexSet:
                wordDict.pop(k)
            time2 = time.time()
            tot = time2 - time1
            print(f'{i} / {len(filter_file)} completed in {tot} seconds. wordDict is length {len(wordDict)} and wordDictForHSK is len {len(finalDict)}')
                
        print("done.")
        print(finalDict)
        print("printed.")
        f = open(database_path+'allHSK_sentence.tsv', 'w', encoding='utf-8')
        for i in finalDict:
            f.write(str(i) + '\t' + str(finalDict[i]) + '\n')
        print("wrote to file. Done.")
    
    #Translates a TSV from simplified to traditional, and vice versa
    #made to speed up algorithm formatting.
    def translateTSV(self, filename, output = 'new_sentence-pairs.tsv', tizi = 'FAN'):
        file = pd.read_csv(database_path+filename, sep='\t')
        f = open(database_path+output, 'w', encoding='utf-8')
        c = sentence_translation.Sentence('test.json')
        c.makeHashes()
        print("Hashes made.")
        for i in range(len(file)):
            #print(i)
            row = file.iloc[[i]].to_dict()
            if c.detect_tizi(row['Phrase'][i]) == tizi:
                row['Phrase'][i] = c.switch_tizi(row['Phrase'][i], tizi)
            f.write(str(row['Num'][i]) + '\t' + str(row['Phrase'][i]) + '\t' + str(row['ID'][i]) + '\t' + str(row['Translation'][i]) + '\n')
        print("done.")
        f.close()
            
        
    #makes text file from hash
    def makeTextFile(self, name='sentences_HSK1.tsv'):
        
        f = open(database_path+name, 'w', encoding='utf-8')
        f.write('Num\tPhrase\tTranslation\n')
        hskNum = name[-5]
        hash_dict = self.format_hskModeStrict(hsk=hskNum)
        print(f'making file {name} with hsk {hskNum}')
        count = 1
        for i in hash_dict:
            #print(hash_dict[i])
            for j in hash_dict[i]:
                j[0] = j[0].replace(",", "，")
                #print(j)
            f.write(str(count)+"\t"+i+"\t"+str(hash_dict[i])+"\n")
            count+=1
            
        f.close()
        print("done.")
    
    #makes a list from the text file first line.
    def make_list_from_txt_col(self, filename, encoding='utf-8'):
        f = open(database_path + filename, 'r', encoding=encoding)
        finalList = []
        for i in f.readlines():
            finalList.append(i[0])
        f.close()
        return finalList
    
    #All of these verifies were me experimenting to see if I could
    #verify sentences faster.
    #I could not.
    def verify(self, phrase, setHash):
        for i in setHash:
            phrase = phrase.replace(i, "")
        if len(phrase) == 0 or phrase.isspace():
            return True
        return False
    
    def verifybyHash(set, phrase, setList):
        for i in setList:
            for j in i:
                phrase = phrase.replace(j, "")
        if len(phrase)==0 or phrase.isspace():
            return True
        return False
    
    def verifyForHSK(self, phrase, filterList):
        for i in range(len(filterList)):
            phrase = phrase.replace(filterList[i], "")
        #print(repr(phrase))
        if len(phrase) == 0 or phrase.isspace():
            return True
        return False
    
    #sorts a CSV by the size of char row.
    #important, since sentence fragmentation in chinese
    #relies on big word first, then little word.
    def CSVsortBySize(self, csvFile, name = "file1.csv"):
        f = pd.read_csv(database_path+csvFile)
        fields = list(f)
        print(fields)
        rows = []
        for i in range(len(f)):
            row = f.iloc[[i]].to_dict()
            #print(row)
            rows.append([row['char'][i], row['pinyin'][i], row['def'][i]])
        print(rows)
        
        #i have done it. I have mode the worst sorting algorithm ever.
        
        newList = []
        maximum = 1
        activated = True
        print(len(rows))
        lenny = len(rows)
        while maximum < 10:
            i = len(rows) - 1
            while i >= 0:
                if len(rows[i][0]) == maximum:
                    newList.insert(0, rows[i])
                i -= 1
                #print(i)
            maximum += 1
        print(len(newList))
        
        with open(database_path+name, mode='w', encoding='utf-8') as csvF:  
            csvwriter = csv.writer(csvF) 
            csvwriter.writerow(fields) 
            csvwriter.writerows(newList)
        
    #How I made the tradTizi files, and the oneChar files.        
    def format_tradTizi(self):
        types_of_encoding = ["utf8"]
        lineList = []
        
        # modification of https://stackoverflow.com/questions/30598350/unicodedecodeerror-charmap-codec-cant-decode-byte-0x8d-in-position-7240-cha
        for encoding_type in types_of_encoding:
            with open("Data/Databases/simplified.txt", encoding = encoding_type) as file:
                lineList = file.readlines()
        file.close()
        finalDict = {}
        for i in lineList:
            #print(i.split())
            lst = i.split()
            finalDict[lst[0]] = lst[1]
        #print(finalDict)
        
        #finalFile = codecs.open("Data/Databases/onlyTradChars.txt", mode = 'w' encoding = encoding_type[0], errors = 'replace')
        with open('Data/Databases/simpp.txt', 'w', encoding='utf-8') as f:
            j = 0
            for i in finalDict:
                j += 1
                val = finalDict[i]
                f.write(f'{j}\t{val}\n')
        f.close()
        
        oneChar = []
        with open('Data/Databases/cedict_ts.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i in lines:
                splitLines = i.split()
                if len(splitLines[0]) == 1:
                    oneChar.append(i)
        #print(oneChar)
        f.close()
        with open('Data/Databases/oneCharTradSimp.txt', 'w', encoding='utf-8') as f:
            for i in oneChar:
                j = i.split()
                if j[0] != j[1]:
                    f.write(i)
        f.close()
        newList = []
        with open('Data/Databases/oneCharTradSimp.txt', 'r', encoding='utf') as f:
            
            for i in f.readlines():
                if i.find("variant of ") == -1 and i.find("(old)") == -1:
                    newList.append(i)

