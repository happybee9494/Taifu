from builtins import print
import requests
from pprint import pprint
import mysql.connector
import itertools
import json
import urllib.parse
import string
import collections

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import KMeans
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
import re
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from pandas import DataFrame
import random
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

import nltk
nltk.download('stopwords')
nltk.download('wordnet')
# Personalized data generator ...................

#////////// Setup Database ///////////////
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="root",
  database="ta_tester"
)
mycursor = mydb.cursor()
#///////////End database setup //////////////



stop = set(stopwords.words('english'))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()


# Cleaning the text sentences so that punctuation marks, stop words &amp; digits are removed
def clean(doc):
    stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
    punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
    processed = re.sub(r"\d+", "", normalized)
    y = processed.split()
    return y

def clusering(vList, no_of_clusters):
    vectorizer = TfidfVectorizer(stop_words='english')#,nmax_features= 50, max_df = 0.5, smooth_idf=True)
    X = vectorizer.fit_transform(vList)

    # Clustering the training 30 sentences with K-means technique
    modelkmeans = KMeans(n_clusters=no_of_clusters, init='k-means++', max_iter=200, n_init=100)
    modelkmeans.fit(X)

    # plt.scatter(df['x'], df['y'], c= modelkmeans.labels_.astype(float), s=50, alpha=0.5)
    # plt.scatter(centroids[:, 0], centroids[:, 1], c='red', s=50)

    clustering = collections.defaultdict(list)

    for idx, label in enumerate(modelkmeans.labels_):
        clustering[label].append(idx)
    #/////////////////////////////// plot generation
    # # reduce the features to 2D
    # pca = PCA(n_components=2, random_state=0)
    # reduced_features = pca.fit_transform(X.toarray())
    #
    # # reduce the cluster centers to 2D
    # reduced_cluster_centers = pca.transform(modelkmeans.cluster_centers_)
    #
    # plt.scatter(reduced_features[:, 0], reduced_features[:, 1], c=modelkmeans.predict(X))
    # plt.scatter(reduced_cluster_centers[:, 0], reduced_cluster_centers[:, 1], marker='x', s=150, c='b')
    # plt.show()

    s = silhouette_score(X, labels=modelkmeans.predict(X))
    print(s)
    return clustering, s

def similarClusters(clusertinDB, newcluster):
    clusertinDB = clusertinDB.replace("[","").replace("]","").replace("'","")
    li = list(clusertinDB.split(','))
    li = [x.strip() for x in li]
    for item in newcluster:
        if item not in li:
            return False
    return True



def printCluters(cluster1_size,clusters, original_list,i):
    ##f = open(str(cluster1_size)+"_clusters_"+ str(i)+".txt", 'w')
    for c, v in enumerate(clusters):
        print('...........................................................................................................')
        ##f.write('........................................................................................................... \n')
        cluster_size = len(clusters[v])
        print(str(c) + '. size =  ' + str(cluster_size))
        ##f.write(str(c) + '. size =  ' + str(cluster_size) +'\n')
        print(clusters[v])
        next_list_for_clustering = []
        for index in clusters[v]:
            print(original_list.__getitem__(index))
            next_list_for_clustering.append(original_list.__getitem__(index))


        ##f.write(str(next_list_for_clustering)+'\n')

        # //////////////// IF Not in DB clusters already
        sql1 = "SELECT  cluster FROM clusters WHERE cluster_size='"+str(cluster_size) + "'"
        mycursor.execute(sql1)
        clusters_list= mycursor.fetchall()
        rc = mycursor.rowcount
        if rc>0:
            isIn = False
            for record in clusters_list:
                if similarClusters(record[0], next_list_for_clustering):
                    isIn = True
            if not isIn:
                # ////////////////Add database record ////////////////////
                sql = "INSERT INTO clusters (cluster,cluster_size) VALUES (%s, %s)"
                val = (str(next_list_for_clustering), str(cluster_size))
                # mycursor.execute(sql, val)
                # mydb.commit()

                print(mycursor.rowcount, "record inserted.")
                # ////////////////End adding database record /////////////

        else:
            # ////////////////Add database record ////////////////////
            sql = "INSERT INTO clusters (cluster,cluster_size) VALUES (%s, %s)"
            val = (str(next_list_for_clustering), str(cluster_size))
            # mycursor.execute(sql, val)
            # mydb.commit()

            print(mycursor.rowcount, "record inserted.")
            # ////////////////End adding database record /////////////


        # if len(next_list_for_clustering)>=5:
        #     clustering_reuslt2 = clusering(next_list_for_clustering, 3)
        #     print(clustering_reuslt2)
        #     for c, v in enumerate(clustering_reuslt2):
        #         print('........................................................' + str(c) + '. size =  ' + str(
        #             len(clustering_reuslt2[v])))
        #         print(clustering_reuslt2[v])
        #         for index in clustering_reuslt2[v]:
        #             print(next_list_for_clustering.__getitem__(index))
    ##f.close()
    return

#//////////////////////////////////////////////
#//////////////////////////////////////////////

#/////////////// 1. Retreive triggers from DB //////////////////
sql1 = "SELECT DISTINCT service_identifier,field_name,field_label FROM Service_Configuration WHERE type_of_trigger_or_action = 'trigger' and field_type = 'text'"
mycursor.execute(sql1)
trigger_results = mycursor.fetchall()
rc = mycursor.rowcount
print('initial : '+str(rc))
#print('initial :' +str(trigger_results))
#///////////////////////////////////////////////

train_clean_sentences = []

for x in trigger_results:
    x = x[2].strip()
    cleaned = clean(x)
    cleaned = ' '.join(cleaned)
    train_clean_sentences.append(cleaned)

# remove duplicates
train_clean_sentences = list(dict.fromkeys(train_clean_sentences))
print('after cleaned: '+str(len(train_clean_sentences)))
#print('after cleaned: '+str(train_clean_sentences))
#//////////////////////

#///////////// check no of clusters WCSS.................
#find the appropriate cluster number
# plt.figure(figsize=(10, 8))
# from sklearn.cluster import KMeans
# wcss = []
# vectorizer = TfidfVectorizer(stop_words='english')
# X = vectorizer.fit_transform(train_clean_sentences)
# for i in range(1, 50):
#     kmeans = KMeans(n_clusters = i, init = 'k-means++', random_state = 42)
#     kmeans.fit(X)
#     wcss.append(kmeans.inertia_)
# plt.plot(range(1, 50), wcss)
# plt.title('The Elbow Method')
# plt.xlabel('Number of clusters')
# plt.ylabel('WCSS')
# plt.show()
##/////////////////////////////// SSE......................
# sse = {}
# vectorizer = TfidfVectorizer(stop_words='english')
# X = vectorizer.fit_transform(train_clean_sentences)
# for k in range(1, 50):
#     kmeans = KMeans(n_clusters=k, max_iter=1000)
#     kmeans.fit(X)
#     #X["clusters"] = kmeans.labels_
#     #print(data["clusters"])
#     sse[k] = kmeans.inertia_ # Inertia: Sum of distances of samples to their closest cluster center
# plt.figure()
# plt.plot(list(sse.keys()), list(sse.values()))
# plt.xlabel("Number of cluster")
# plt.ylabel("SSE")
# plt.show()


#////////////////
c = 0
current_list = train_clean_sentences
score_string = ''
cluster1_size = 37
while c<100:
    clustering_reuslt, sil_score  = clusering(current_list, cluster1_size)
    score_string = score_string + '\n'+ str(c) + ': score = ' + str(sil_score)
    printCluters(cluster1_size, clustering_reuslt, current_list,c)
    c = c+1
    print('################################################################################ SHUFFEL #####################################################################')
    shuffle_list = random.sample(current_list, len(current_list))
    current_list = shuffle_list

print(score_string)

#adjusted_rand_score requires true labels