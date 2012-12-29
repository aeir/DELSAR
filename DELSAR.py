###################################################################
# DELSAR.py                                                       #
#                                                                 # 
# Algorithms:                                                     #
#                                                                 #
# DELSAR                                                          #
# Documented-Emotion Latent Semantic Algorithmic Reducer          #
# Calculates semantic distinctiveness of a corpus, given each     #
# document is labeled using LSC                                   #
# Reduces an initial keyword (label) set using LSC                #
#                                                                 #
# ELSA                                                            #
# Emotional Latent Semantic Analysis                              #
# Calculates the accuracy of emotion-specific sub-corpora, using  #
# the average of maximum cosine similarity between documents      #
#                                                                 #
# @requires MySQLdb, gensim, eLists folder                        #
# @author Eugene Yuta Bann                                        #
# @version 29/12/12                                               #
#                                                                 #
###################################################################

from gensim import corpora, models, similarities
import MySQLdb, time, itertools
from collections import Counter

########## VARIABLES ##############################################

ELSA = False
printDELSAR = True # print array for Excel matrix input

# Uncomment emotion set to test:
# eLists folder contains these files, you are able to edit in a text editor

#emotionTest = "IZARD"
#emotionTest = "RUSSELL"
#emotionTest = "PLUTCHIK"
emotionTest = "EKMAN"
#emotionTest = "TOMKINS"
#emotionTest = "JOHNSON" #OATLEY
#emotionTest = "ALL"
#emotionTest = "DELSAR"
#emotionTest = "BANN"

limit = 100 # Document limit per emotion
dimension = 40 # LSA number of dimensions

# Uncomment additional parameters for MySQL query:

sqlHaving = ""
#sqlHaving = "HAVING idx MOD 4 = 0"
#sqlHaving = "HAVING idx MOD 13 = 1"
#sqlHaving = "HAVING idx MOD 3 = 2"
#sqlHaving = "HAVING (idx MOD 11 = 7 AND idx > 280)"
#sqlHaving = "AND timezone = 'London'"
#sqlHaving = "AND NOT timezone = 'Mountain Time (US & Canada)' AND NOT timezone = 'Pacific Time (US & Canada)' AND NOT timezone = 'Eastern Time (US & Canada)' AND NOT timezone = 'Central Time (US & Canada)' AND NOT timezone = '' AND NOT timezone = 'Quito' AND NOT timezone = 'Atlantic Time (Canada)'"
#sqlHaving = "AND (timezone = 'London' OR timezone = 'Edinburgh' OR timezone = 'Dublin')"
#sqlHaving = "AND (timezone = 'Mountain Time (US & Canada)' OR timezone = 'Pacific Time (US & Canada)' OR timezone = 'Eastern Time (US & Canada)' OR timezone = 'Central Time (US & Canada)')"
#sqlHaving = "AND timezone = 'Pacific Time (US & Canada)'"
#sqlHaving = "AND timezone = 'Eastern Time (US & Canada)'"
#sqlHaving = "AND timezone = 'Central Time (US & Canada)'"
#sqlHaving = "AND timezone = 'Quito'"

# Possible Asia group: Beijing Tokyo Hong Kong Jakarta Kuala Lumpur Singapore

################################################################## 

# Create emotion term arrays
# Change below for where the emotion lists are stored
# .e files are text files, each emotion on a new line
emotionFile = "eLists/" + emotionTest + ".e"
emotionTerms = [emotion.lower().strip() for emotion in open(emotionFile)]
# Database variables
db = MySQLdb.connect("HOSTNAME", "USERNAME", "PASSWORD", "DATABASE")
cursor = db.cursor()
          
###################################################################         

## For DELSA (without reduction):
## set reduceTo to a number higher than the initial set
def DELSAR(initial, reduceTo):
     # Corpus class to load each document iteratively from database
     class MyCorpus(object):
          def __iter__(self):
               for emotion in range(len(emotionTerms)):
                    try:
                         sql = "SELECT text, @idx:=@idx+1 AS idx FROM ETWEETS WHERE emotion = '%s' %s LIMIT %d" % (emotionTerms[emotion], sqlHaving, limit)
                         cursor.execute("SELECT @idx:=0;")
                         cursor.execute(sql)
                         results = cursor.fetchall()
                         for row in results:
                              yield dictionary.doc2bow(row[0].lower().split())
                    except:
                         print "Error: unable to fetch data"
     emotionTerms = initial
     if (len(initial) > reduceTo and not ELSA):
          print str(len(initial)) + " emotions, " + str(len(initial)-reduceTo) + " reductions remaining."
     else:
          print str(len(initial)) + " emotions, 0 reductions remaining."
     print "Creating dictionary..."
     # Create a dictionary
     dictionary = corpora.Dictionary()
     for emotion in range(len(emotionTerms)):
          try:
               sql = "SELECT text, @idx:=@idx+1 AS idx FROM ETWEETS WHERE emotion = '%s' %s LIMIT %d" % (emotionTerms[emotion], sqlHaving, limit)
               cursor.execute("SELECT @idx:=0;")
               cursor.execute(sql)
               results = cursor.fetchall()
               dictionary.add_documents(row[0].lower().split() for row in results)
          except MySQLdb.Error, e:
               print "Error %d: %s" % (e.args[0], e.args[1])
     # We don't use a stoplist
     stoplist = set("a".split())
     stop_ids = [dictionary.token2id[stopword] for stopword in stoplist
                 if stopword in dictionary.token2id]
     # We get rid of words that only occur once in the entire corpus
     once_ids = [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() if docfreq == 1]
     dictionary.filter_tokens(stop_ids + once_ids)
     # Remove gaps in id sequence after words that were removed
     dictionary.compactify()
     # Print dictionary information
     print dictionary

     ###############################################################

     print "Creating corpus object..."
     # Create corpus object from database iteratively, doesn't load into memory
     corpus_memory_friendly = MyCorpus()
     print "Done."

     ###############################################################

     print "Generating LSA Space..."     
     # use a log-entropy model to weight terms
     logent = models.LogEntropyModel(corpus_memory_friendly)
     # initialize an LSI transformation
     corpus_logent = logent[corpus_memory_friendly]
     lsi = models.LsiModel(corpus_logent, id2word=dictionary, num_topics=dimension)
     # create a double wrapper over the original corpus: bow->logent->fold-in-lsi
     corpus_lsi = lsi[corpus_logent]
     print corpus_lsi
     
     print "Indexing LSA Space..."
     index = similarities.Similarity("index.e", corpus_lsi, num_features=dimension)     
     print "Done."

     # ALPHA CODE FOR CLASSIFIER TO BE RELEASED IN FEB2013
     # Save Emotive Brain Model (for above future work)
     # We can have a new brain model each month for example
     #index.save("EB0")
     # Load Emotive Brain Model
     #index = similarities.MatrixSimilarity.load("EB0")

     ###############################################################

     print "Clustering Documents..."     
     mapEmotion = [] # index, word
     queryMatch = [] # word, max cosine (ELSA)/index (DELSAR)
     sequentialCount = 0 # We need this to keep track of streaming
     # Stream back all documents in order
     for emotion in range(len(emotionTerms)):
          try:
               sql = "SELECT text, @idx:=@idx+1 AS idx FROM ETWEETS WHERE emotion = '%s' %s LIMIT %d" % (emotionTerms[emotion], sqlHaving, limit)
               cursor.execute("SELECT @idx:=0;")
               cursor.execute(sql)
               results = cursor.fetchall()
               for row in results:
                    # For each document, a is actual term, b is most similar term using LSA
                    a = emotionTerms[emotion]
                    # Delete the emotion keyword from the document
                    tweet = row[0].replace(emotionTerms[emotion], "")
                    # Convert the document to logent LSA space
                    vec_bow = dictionary.doc2bow(tweet.lower().split())
                    query_lsi = lsi[logent[vec_bow]]
                    # Compute document similarity
                    sims = index[query_lsi]
                    sims = sorted(enumerate(sims), key=lambda item: item[0])
                    # Delete the current document from the array
                    del sims[sequentialCount]
                    if(ELSA):
                         # ELSA uses maximum cosine value
                         b = max(sims, key=lambda x: x[1])
                    else:
                         # DELSAR just wants to know what emotion is the most similar document
                         b = sims.index(max(sims, key=lambda x: x[1]))
                    queryMatch.append([a,b]) 
                    mapEmotion.append(emotionTerms[emotion]) 
                    sequentialCount += 1
          except MySQLdb.Error, e:
               print "Error %d: %s" % (e.args[0], e.args[1])      
     accuracy = []
     totalHit = 0
     totalMiss = 0
     if(printDELSAR):
          clusters = []
     if(ELSA):
          # For each emotion we get an average maximum cosine value
          floatNums = [float(vec[1][1]) for vec in queryMatch]
          average = sum(floatNums) / len(queryMatch)
          accuracy.append([emotionTerms[0], average])
          for vec in accuracy:
               numbers.append(vec[1])
               print vec
     else: 
          # DELSAR
          # This bit determines accuracy of clustering (labelling)
          # If the nearest document is the same emotion, it is a hit,
          # otherwise it is a miss. In both occassions, we record
          # the actual emotion in the clusters array if required
          # for printing to Excel
          for a in range(len(emotionTerms)):
               hitRate = 0
               hit = 0
               miss = 0
               for vec in queryMatch:
                    if vec[0] == emotionTerms[a]:
                         if vec[0] == mapEmotion[vec[1]]:
                              hit += 1
                              totalHit += 1
                              if(printDELSAR):
                                   clusters.append((vec[0],mapEmotion[vec[1]]))
                         else:
                              miss += 1
                              totalMiss += 1
                              if(printDELSAR):
                                   clusters.append((vec[0],mapEmotion[vec[1]]))
               c = float(hit)
               d = float(miss)
               if c+d > 0:
                    hitRate = c/(c+d)
               # Accuracy of hit rate for each emotion gets appended to this array
               accuracy.append([emotionTerms[a], hitRate])
          totalHit = float(totalHit)
          totalMiss = float(totalMiss)
          if((totalHit+totalMiss) > 0):
               total = (totalHit/(totalHit+totalMiss))
          else:
               total = 0
          # Reduce emotion set and rerun DELSAR if we need to reduce more emotions
          if(len(initial) > reduceTo):
               print "Removed %s (%f)" % (min(accuracy, key=lambda x: x[1])[0], min(accuracy, key=lambda x: x[1])[1])
               del initial[initial.index(min(accuracy, key=lambda x: x[1])[0])]
               DELSAR(initial, reduceTo)
          # Otherwise we're done
          else:
               for vec in accuracy:
                    print vec
               print "TOTAL ACCURACY: %f" % total  
          if(printDELSAR):
               # Print DELSAR clustering values in order for copy&paste into Excel
               c = Counter(clusters)
               for i in range(len(emotionTerms)):
                    for j in range(len(emotionTerms)):
                         for vec in c:
                              if vec[0] == emotionTerms[i]:
                                   if vec[1] == emotionTerms[j]:
                                        print c[vec]


###############################################################

# START PROGRAM HERE:

###############################################################

# Start the timer
t0 = time.clock()
if(ELSA):
     numbers = []
     for a in emotionTerms:
          print "ELSA" + str(limit) + " testing " + a + " with " + str(dimension) + " dimensions."
          print sqlHaving
          DELSAR([a], 88) # Make sure the number here is greater than the emotion set size
     for vec in numbers:
          print vec
else: # DELSAR
     print "DELSAR" + str(limit) + " testing " + emotionTest + " with " + str(dimension) + " dimensions."
     print sqlHaving
     DELSAR(emotionTerms, 88) # Change the number here to the final reduced keyword set size
# Close database and print total time taken
db.close()
print "Time Taken:"
print str((time.clock() - t0)/60)

# # # # # # # # -------- END PYTHON -------- # # # # # # # #

