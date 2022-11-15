import math
from bs4 import BeautifulSoup
from collections import Counter
import glob
import json
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
import os
import re
import sys
# import sklearn
# from urllib.request import urlopen


class Posting:
    def __init__(self, docID, tfidf) -> None:
        self.docID = docID
        self.tfidf = tfidf
        #self.fields = fields
    

class invertedIndex:

    def __init__(self, dev_path, docHash_path = None, offsets_path = None, num_docs = None) -> None:
        # Create stemmer object
        self.stemmer = PorterStemmer()
        # Tokenizer object
        # self.tokenizer = RegexpTokenizer("[A-Za-z']+")
        self.tokenizer = RegexpTokenizer("(\w+(?:'?\w+)*)")
        # Current JSON fragment file number
        self.fileNo = 0
        # index
        self.index = dict()        
        # json corpus dataa
        self.dev_path = dev_path
        # Counts num of unique tokens
        self.numUnique = 0
        # docID
        self.currDocID = num_docs if num_docs else 0
        # self.currDocID = 0          #55393
        # Number of webpages to show when searching
        self.numHits = 10
        # stop words
        self.stopwords = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", 
            "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", 
            "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", 
            "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", 
            "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", 
            "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", 
            "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", 
            "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", 
            "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]
        # Dictionary of docID: URL
        if docHash_path != None:
            with open(docHash_path, 'r') as file1:
                self.docHash = json.load(file1)
        else:
            self.docHash = {} 
        # Dictionary of offsets
        if offsets_path != None:
            with open(offsets_path, 'r') as file2:
                self.offsets = json.load(file2)
        else:
            self.offsets = {} 

    def buildIndex(self, D, url) -> None:
        soup = BeautifulSoup(D, 'lxml')
        tokens = self.tokenizer.tokenize(soup.get_text())
        # tokens = [word.lower() for word in tokens if word.isalnum()]
        # Gets list of stems from the tokens
        stems = [self.stemmer.stem(token) for token in tokens]
        self.docHash[self.currDocID] = (url,len(stems))
        # Create an alphabetical set of unique stems
        uniqueStems = sorted(list(set(stems)))

        # Counts the frequency of each stem in the document
        c = Counter(stems)
        postingData = []
        for stem in uniqueStems:
            postingData.append((stem, c[stem]))

        
        # pseudo - for all tokens e in T do 
        for word, count in postingData:
            # if the token is not in indexes, add the docId as the first element in that deque
            if word not in self.index:
                self.index[word] = [Posting(self.currDocID, count)]
            # otherwise add the docId to the current deque
            else:
                self.index[word].append(Posting(self.currDocID, count))

        # increment n before going to the next document 
        self.currDocID += 1

        
    def run(self):
        for dir in os.listdir(self.dev_path):
            f = os.path.join(self.dev_path, dir)
            # checking if it is a file
            for filename in os.listdir(f):
                full = os.path.join(f, filename)
                if os.path.isfile(full):
                    corpus_data = json.load(open(full))
                    # Store docID: URL in docHash 
                    # self.docHash[self.currDocID] = corpus_data['url']
                    self.buildIndex(corpus_data['content'], corpus_data['url'])
                    #print(corpus_data['url'])
                    #full.close()
                if self.currDocID % 1000 == 0:
                    print("Completed:", self.currDocID)
                if self.currDocID % 5000 == 0:
                    print("Index Size:", sys.getsizeof(self.index))
                if sys.getsizeof(self.index) >= 7500000:
                    #The final size of the dictionary was 41943136 bytes
                    #Store data in the machine
                    print(f"Done with {self.currDocID} documents\nDumping into fragment{self.fileNo}.txt")
                    self.dumpDict()
        #at the end store last file into the disk
        if len(self.index) != 0: 
            print(f"Final dump into fragment{self.fileNo}.txt")
            self.dumpDict()
        self.mergeFragments()
        self.dumpHashOffsets()
        #     break
        # print(self.index)

    def dumpHashOffsets(self) -> None:
        with open("docHash.json", "w") as dh, open("offsets.json", "w") as off:
            json.dump(self.docHash, dh)
            json.dump(self.offsets, off)
        
    def dumpDict(self) -> None:
        with open(f'fragment{self.fileNo}.txt', 'w') as f:
            #key is string
            #val is list of posting objects
            alphabetical = sorted(self.index.items(), key = lambda x:x[0])
            for key, val in alphabetical:
                s = ''
                for posting in val:
                    # Creates string of postings
                    s += f"({str(posting.docID)},{str(posting.tfidf)})"
                # write key followed by postings
                f.write(f'{key}\t{s}\n')
        self.fileNo += 1
        self.index = dict() 
        
        
    def mergeFragments(self) -> dict:
        '''Open file pointers for all fragment*.txt files
        Open write file pointer to the big dictionary
        
        Read fragments line by line
            process with regex
            iterate through regex for each line in each file also
            find the index that comes first in all of the files and put that one
            Break ties? shouldnt have to but maybe
        output to big boi file yuh
        '''
        fragmentList = glob.glob('fragment*.txt', recursive=False)
        # Make list of file pointers
        pointerList = []
        # make list of all fragment file pointers
        for frag in fragmentList:
            pointerList.append(open(frag, 'r'))
        
        reIndexWord = "(.+)\t"
        rePostings = "((\((\d+)\,(\d+)\))+)"

        # holds tuples of (matched word, matched postings)
        parsedLines = []
        for pointer in pointerList:
            # get a line from each fragment file
            line = pointer.readline()
            '''ERROR CHECKING THE LINE (EOF)'''
            # add tuples to the parsedLines list
            parsedLines.append((re.match(reIndexWord, line).group(1), re.search(rePostings, line)[0]))


        '''
        Find lowest alphabetical index word (min())
        Write that into the output file first
        Readline on that same fragment file again
        Repeat:
            Find lowest alphabetical index word (min())
            Write that into the output file first
        '''
        #index file
        with open('index.txt', 'w') as out:
            prev = ''
            # if this is the first line we write
            firstLine = True
            while len(pointerList) != 0:
                # TODO Find lowest alphabetical index word (min())
                lowest_alpha = min(parsedLines, key=lambda m: m[0])
                index = parsedLines.index(lowest_alpha, 0)
                # TODO Write that into the output file first
                #if the current minimum is the same as the previous, continue line
                if lowest_alpha[0] == prev:
                    out.write(f"{lowest_alpha[1]}")
                else: 
                    self.numUnique += 1
                    # If this is the first line we write, do not put a newline
                    if not firstLine:
                        out.write("\n")
                    # if this is the first line, we skip the newlines
                    else: 
                        firstLine = False
                    # write term into out file
                    out.write(f"{lowest_alpha[0]}\t")
                    # get position of pointer in out file
                    pos = out.tell()
                    # write postings to out file
                    out.write(f'{lowest_alpha[1]}')
                    # add offset to dictionary
                    self.offsets[lowest_alpha[0]] = pos
                    # sets prev value to current before we moce to the next iteration
                    prev = lowest_alpha[0]
                # TODO Readline on that same fragment file again
                line = pointerList[index].readline()
                if line == '':
                    parsedLines.pop(index)
                    pointerList[index].close()
                    pointerList.pop(index)
                    continue
                else:
                    parsedLines[index] = (re.match(reIndexWord, line).group(1), re.search(rePostings, line)[0])


        '''the number of documents, 
        the number of [unique] tokens, 
        total size (in KB) of your index on disk.'''
        with open('output.txt', 'w') as out:
            out.write("Cole Schiffer - 52736804\n")
            out.write("Matthew Wu - 91425294\n")
            out.write("Alex Ibasitas - 14913216\n")
            out.write(f"\nNumber of Documents: {str(self.currDocID)}\nNumber of Unique Tokens: {str(self.numUnique)}\nSize of Index: {str(os.path.getsize('index.txt')/1024.0)} KB")



    def handleCosineQuery(self, query: str):
        scores = {}
        length = {} #length is sqrt(sum_all_tf_in_d(tf**2))

        #split by white space
        #each word is an and
        terms = query.lower().split(' ')
        # print(terms)
        termPostings = []
        # get postings for each term
            # find each term and its offsets from dict
            # use the offset in the index.txt file
        runningSet = set()
        docids = set()
        smax = 0
        with open('index.txt', 'r') as index:
            for term in set(terms):
                
                # Calculate w_t,q 
                # print("term",term)
                tf_tq = query.lower().count(term)
                # print("tf_tq", tf_tq)
                w_tq = (1 + math.log10(tf_tq))


                s = self.stemmer.stem(term)

                discount = 1 if s not in self.stopwords else 0.4
                

                # get offset for term
                if s not in self.offsets:
                    return 'no files pertain to your search'
                offset = self.offsets[s]

                # seek into the index.txt file and get line
                index.seek(offset)
                line = index.readline()

                # parse the postings
                rePostings = "\((\d+)\,(\d+)\)"
                
                #re.find all 
                # fetches poting list for term 
                posts = re.findall(rePostings, line)    #returns match objects like '(100, 1000)' for example
                
                for d, tf in posts:
                    d = int(d)
                    tf = int(tf)
                    


                    docLen = self.docHash[str(d)][1]
                    w_td = (1 + math.log10(tf)) * math.log10(self.currDocID/len(posts))
                    # print("Wtd",w_td)
                    if d not in scores:
                        scores[d] = 0
                    if d not in length:
                        length[d] = 0
                    scores[d] += w_td * w_tq * discount
                    # print("scores[d]",scores[d])
                    length[d] += docLen
                    # print("length[d]",length[d])
                    
                
                # set of the docids
                s = {int(i) for i, freq in posts}
                docids.update(s)

        # Normalize?
        for d in docids:
            scores[d] /= math.sqrt(length[d])
            smax = max(scores[d], smax)



        if len(scores) > 0:
            sortedlist = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
            if len(scores) >= self.numHits:
                # print("MAX",smax)
                return [(self.docHash[str(id)][0],score) for id,score in sortedlist[:10]]
            else:
                # print("MAX",smax)
                return [(self.docHash[str(id)][0],score) for id,score in sortedlist]
        else: return 'no files pertain to your search'

        

        
if __name__ == "__main__":
    # i = invertedIndex('./DEV', "docHash.json", "offsets.json", num_docs=55393)
    i = invertedIndex('./DEV')
    i.run()


