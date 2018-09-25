import buildindex
import re,glob,os

#NEED TO TEST MORE.

#input = [file1, file2, ...]
#res = {word: {filename: {pos1, pos2}, ...}, ...}
class Query:

	def __init__(self, filenames):
		self.filenames = filenames
		self.index = buildindex.BuildIndex(self.filenames)
		print(self.index)
		self.invertedIndex = self.index.totalIndex
		self.regularIndex = self.index.regdex


	def one_word_query(self, word):
		word=word.lower()                  																	#lowercase the words
		
		pattern = re.compile('[\W_]+')						 												#removing spaces
		word = pattern.sub(' ',word)                                   
		if word in self.invertedIndex.keys():																#if word in index rank the results 
			return self.rankResults([filename for filename in self.invertedIndex[word].keys()], word)
		else:
			return []

	def free_text_query(self, string):
		
		pattern = re.compile('[\W_]+')												#removing spaces
		string = pattern.sub(' ',string)
		result = []
		for word in string.split():													#spliting string
			
			result += self.one_word_query(word)										#quering each word individually
		return self.rankResults(list(set(result)), string)

	#inputs = 'query string', {word: {filename: [pos1, pos2, ...], ...}, ...}
	#inter = {filename: [pos1, pos2]}
	def phrase_query(self, string):
		pattern = re.compile('[\W_]+')								#removing spaces			
		string = pattern.sub(' ',string)
		listOfLists, result = [],[]
		for word in string.split():                                                                                 
			  word=word.lower()
			  listOfLists.append(self.one_word_query(word))
		setted = set(listOfLists[0]).intersection(*listOfLists)
		for filename in setted:
			temp = []
			for word in string.split():
				word=word.lower()
				temp.append(self.invertedIndex[word][filename][:])
			for i in range(len(temp)):
				for ind in range(len(temp[i])):
					temp[i][ind] -= i
			if set(temp[0]).intersection(*temp):
				result.append(filename)
		return self.rankResults(result, string)

	def make_vectors(self, documents):
		vecs = {}
		for doc in documents:
			docVec = [0]*len(self.index.getUniques())                     #we decompose every document into a vector of length N, where N is the total number of unique terms in 
			for ind, term in enumerate(self.index.getUniques()):		  # that document, and each entry is the number of times that specific term appears in that document.
				docVec[ind] = self.index.generateScore(term, doc)         # For multiple documents, a more convenient way of defining N is as the number of unique words in all 
			vecs[doc] = docVec 											  #documents in the search space. This allows us to represent every document as a vector, and make the vectors unit.
		return vecs


	def query_vec(self, query):
		pattern = re.compile('[\W_]+')                                                       #creating query vector to compare with documents vector to rank result using cosine 
		query = pattern.sub(' ',query)
		queryls = query.split()
		queryVec = [0]*len(queryls)
		index = 0
		for ind, word in enumerate(queryls):
			queryVec[index] = self.queryFreq(word, query)
			index += 1
		queryidf = [self.index.idf[word] for word in self.index.getUniques()]
		magnitude = pow(sum(map(lambda x: x**2, queryVec)),.5)
		freq = self.termfreq(self.index.getUniques(), query)
		#print('THIS IS THE FREQ')
		tf = [x/magnitude for x in freq]
		final = [tf[i]*queryidf[i] for i in range(len(self.index.getUniques()))]
		#print(len([x for x in queryidf if x != 0]) - len(queryidf))
		return final

	def queryFreq(self, term, query):
		count = 0
		#print(query)                                                    #calculating query frequency
		#print(query.split())
		for word in query.split():
			if word == term:
				count += 1
		return count

	def termfreq(self, terms, query):
		temp = [0]*len(terms)                                        #calcultaing term frequency
		for i,term in enumerate(terms):
			temp[i] = self.queryFreq(term, query)
			#print(self.queryFreq(term, query))
		return temp

	def dotProduct(self, doc1, doc2):
		if len(doc1) != len(doc2):                                             #calculating dot product
			return 0
		return sum([x*y for x,y in zip(doc1, doc2)])

	def rankResults(self, resultDocs, query):
		vectors = self.make_vectors(resultDocs)
		#print(vectors)                                                                                      
		queryVec = self.query_vec(query)
		#print(queryVec)
		results = [[self.dotProduct(vectors[result], queryVec), result] for result in resultDocs]
		#print(results)
		results.sort(key=lambda x: x[0])
		#print(results)
		results = [x[1] for x in results]
		return results




path = os.getcwd()
os.chdir(path)

textfilea = []
for file in glob.glob("*.txt"):
	textfilea.append(file)

print(textfilea)
q = Query(textfilea)

while(1):
	key = input()
	dawt = input()
	if dawt == "ftq":
		print(q.free_text_query(key))
	elif dawt == "pq":	
		print(q.phrase_query(key))
	elif dawt == "owq":
	    print(q.one_word_query(key))
	else:
		print("Enter correct word")			


   