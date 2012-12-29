DELSAR
======

Document-Emotion Latent Semantic Analysis Reducer (DELSAR) Clustering Algorithm

<<<< TWEETS.sql >>>>

Run this on a MySQL server to create the table structure for harvested tweets.

<<<< twitter_stream_word.php >>>>

Run this on a unix server to collect tweets into the above DB.
Remember to change the name of the database host and password and your Twitter credentials.
My account has the Gardenhose enabled, if you do not request this you will only receive 1% of all tweets (as opposed to 10%).

<<<< DELSAR.py >>>>

Run this this to analyse the tweets.
DELSAR shows which emotions are the most distinct relative to the documents for all emotions in a given set.
It also *reduces* an emotion set to its most semantically distinct keywords.
This *is* different than removing the least distinct keywords at once on the first iteration.
ELSA shows which emotions are the most distinct relative to the documents within that emotion.
Remember to reference the correct database host/credentials used.

Any problems or questions please do not hesitate to email me:
eugene@aeir.co.uk

Code is updated periodically. Next update due by the end of Feb 2013.