from datetime import datetime
from invertedIndex import invertedIndex
import sys


'''
# import required libraries
from pydoc import doc
from telnetlib import theNULL
import numpy as np
from numpy.linalg import norm
 
# define two lists or array
A = np.array([2,1,2,3,2,9])
B = np.array([3,4,2,4,5,5])
 
print("A:", A)
print("B:", B)
 
# compute cosine similarity
cosine = np.dot(A,B)/(norm(A)*norm(B))
print("Cosine Similarity:", cosine)

# https://www.geeksforgeeks.org/how-to-calculate-cosine-similarity-in-python/
# visit link to look how to solve 2d arrays

# cosine similarity measures the similarity between two vectors of an inner product space
# higher cosine means coduments are more similar
'''

# GOALS
# 1. top 5 URLs for each of the queries:
#    ("cristina lopes", "machine learning", "ACM", "master of software engineering")
# 2. search interface in action


if __name__ == '__main__':
    i = invertedIndex('./DEV', "docHash.json", "offsets.json", 55393)
    print("Welcome to our Search Engine!")
    print("Please type in a query")
    print("Enter 'quit()' to leave")
    for line in sys.stdin:
        #Because it says for line in sys.stdin
        #It means that if there is no more input, it will wait for the next input from the command line
        #Basically it will pause
        query = line.strip().lower()
        if 'quit()' == query:
            break
        #Query handling
        #Error Checking?
        #Query handling
        print(f'Processing query: {query}')
        start_time = datetime.now()
        response = i.handleCosineQuery(query)
        end_time = datetime.now()
        
        time_diff = (end_time - start_time)
        execution_time = time_diff.total_seconds() * 1000

        if response == 'no files pertain to your search':
            print(response)
        else:
            for q, (v,s) in enumerate(response, 1): 
                print(f"{q}) {v}\t(score: {s})")
        print("Time", execution_time)
        print("Enter 'quit()' to leave")
    print("Done")
