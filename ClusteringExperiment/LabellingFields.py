import mysql.connector
from builtins import print
import mysql.connector
from pyrxnlp.api.cluster_sentences import ClusterSentences
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
import re
from sklearn.metrics import silhouette_score
import collections

############### Setup Database ################
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="root",
  database="ta_tester"
)
mycursor = mydb.cursor()
############### END Setup Database #############

################################################
# Cleaning the text sentences so that punctuation marks, stop words &amp; digits are removed
stop = set(stopwords.words('english'))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()
def clean(doc):
    stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
    punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
    processed = re.sub(r"\d+", "", normalized)
    y = processed.split()
    return y
##################################################

################################## 1 #################################################
def addUnCleanedClustersToDB(clusters, original_list):
    return_list = []
    sentence_count = []
    if clusters is not None:
        for cluster in clusters:
            cluster_topics = cluster['clusterTopics']
            cluster_score = cluster['clusterScore']
            cluster_size = cluster['clusterSize']
            cluster_sentences = cluster['clusteredSentences']

            cluster_sentence_list = []
            for sents in cluster_sentences:
                cluster_sentence_list.append(' '.join(clean(cluster_sentences[sents])))
                v = cluster_sentences[sents]
                sentence_count.append(v)
                if v in original_list:
                    original_list.remove(v)

            topic_string = ",".join(cluster_topics)
            cluster_string = ",".join(cluster_sentence_list)

            if topic_string != 'sentences_with_no_cluster_membership':
                # ################# Add database record #############################
                sql = "INSERT INTO all_rxnlp_clusters (cluster_label, cluster,cluster_size, cluster_score) VALUES (%s, %s, %s, %s)"
                val = (topic_string, cluster_string, str(cluster_size), str(cluster_score))
                mycursor.execute(sql, val)
                mydb.commit()
                #print(mycursor.rowcount, "record inserted.")
                # ################ End adding database record #######################

            elif topic_string == 'sentences_with_no_cluster_membership':
                unclustered_list = []
                for sents in cluster_sentences:
                    unclustered_list.append(cluster_sentences[sents].split(':')[1])
                    v = cluster_sentences[sents].split(':')[1]
                    sentence_count.append(v)
                    if v in original_list:
                        original_list.remove(v)
                return_list = unclustered_list

    sentence_count = list(dict.fromkeys(sentence_count))
    return return_list, original_list, sentence_count
#####################################################################################

#################################### 2 ###############################################
def cluserbyOriginalFieldLabel(missed_list):
    # replace this with your api key (see: http://www.rxnlp.com/api-key/)
    apikey = "298356655amsha2cb9bdd684ee4fp18476bjsn183eb62f9613"
    # initialize sentence clustering
    clustering = ClusterSentences(apikey)

    # apply clustering to the missed list without cleanning
    missed_list = list(dict.fromkeys(missed_list))
    clusters = clustering.cluster_from_list(missed_list)

    new_list, remainning, sentence_count = addUnCleanedClustersToDB(clusters, missed_list)
    #print(remainning)

    # if clusters is not None:
    #     print("------------------------------")
    #     print("Clusters from a list of sentences")
    #     print("------------------------------")
    #     clustering.print_clusters(clusters)
    return
########################################################################################


# START .................................................................................
# 1) Retrieve field label from Service_Configuration
sql1 = "SELECT DISTINCT field_label FROM Service_Configuration WHERE field_type = 'text'"
mycursor.execute(sql1)
search_results = mycursor.fetchall()
rc = mycursor.rowcount
print('distinct fields : '+str(rc))

c = 0
missed_list = []
for field in search_results:
    c = c + 1
    original_field = field[0].strip()
    print(str(c) +'.) original_field : ' + original_field)
    cleaned_field = clean(original_field)
    cleaned_field = ' '.join(cleaned_field)
    print('cleaned_field : ' + cleaned_field)

    # 2) Retreive lables assigned for the original cleaned_field from all_rxnlp_clusters
    sql1 = "SELECT cluster_label FROM all_rxnlp_clusters WHERE cluster like '%,"+cleaned_field+ ",%' or cluster like '%,"+cleaned_field+ "' or cluster like '"+cleaned_field+ ",%' or cluster like '%"+cleaned_field+ ",%'  and cluster not like '% "+cleaned_field+ ",%' or cluster like '%,"+cleaned_field+ "%' and cluster not like '%,"+cleaned_field+ " %'"
    mycursor.execute(sql1)
    cluster_results = mycursor.fetchall()
    rc = mycursor.rowcount
    print('cluster labels : ' + str(cluster_results))
    if rc == 0:
        missed_list.append(original_field)


missed_list = list(dict.fromkeys(missed_list))
print('missed count : ' + str(len(missed_list)))
print(missed_list)
# 3.) call to cluster again the missed list
cluserbyOriginalFieldLabel(missed_list) #  uncomment
print('################################## END ##################################################')
########################################################################################################
########################################################################################################
########################################################################################################

############################### 3 #####################################
def clusering(vList, no_of_clusters):
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(vList)

    # Clustering the training 30 sentences with K-means technique
    modelkmeans = KMeans(n_clusters=no_of_clusters, init='k-means++', max_iter=200, n_init=100)
    modelkmeans.fit(X)

    clustering = collections.defaultdict(list)

    for idx, label in enumerate(modelkmeans.labels_):
        clustering[label].append(idx)

    s = silhouette_score(X, labels=modelkmeans.predict(X))
    return clustering, s
########################################################################

############################## 4 #######################################
def printClutersNaddToDB(cluster1_size, clusters, original_list, i):
    for c, v in enumerate(clusters):
        print('........................................................')
        cluster_size = len(clusters[v])
        print(str(c) + '. size =  ' + str(cluster_size))
        ##f.write(str(c) + '. size =  ' + str(cluster_size) +'\n')
        print(clusters[v])
        next_list_for_clustering = []
        for index in clusters[v]:
            print(original_list.__getitem__(index))
            next_list_for_clustering.append(original_list.__getitem__(index))

        seperator = ','
        string_clusters = seperator.join(next_list_for_clustering)
        # ////////////////Add database record ////////////////////
        sql = "INSERT INTO all_rxnlp_clusters (cluster,cluster_size) VALUES (%s, %s)"
        val = (string_clusters, str(cluster_size))
        mycursor.execute(sql, val)
        mydb.commit()
        print(mycursor.rowcount, "record inserted.")
        # ////////////////End adding database record /////////////
    return
#########################################################################

# SECOND START .......................................................................
# If still the missed count is >10 apply kmean
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# clean the missed list
new_missed_list =[]
for x in missed_list:
    cleaned = clean(x)
    cleaned = ' '.join(cleaned)
    new_missed_list.append(cleaned)

# remove duplicates
new_missed_list = list(dict.fromkeys(new_missed_list))
print('after cleaned: '+str(len(new_missed_list)))

# truncate to remove one word sentences
truncated_list = []
for sentence in new_missed_list:
    word_list = sentence.split(" ")
    if len(word_list) >1:
        truncated_list.append(sentence)
print('after truncated: '+str(len(truncated_list)))
##################################################
# plot wcss elbow curve to find the no of clusters
# plt.figure(figsize=(10, 8))
# wcss = []
# vectorizer = TfidfVectorizer(stop_words='english')
# X = vectorizer.fit_transform(truncated_list)
# for i in range(1, 100):
#     kmeans = KMeans(n_clusters=i, init='k-means++', random_state=42)
#     kmeans.fit(X)
#     wcss.append(kmeans.inertia_)
# plt.plot(range(1, 100), wcss)
# plt.title('The Elbow Method')
# plt.xlabel('Number of clusters')
# plt.ylabel('WCSS')
# plt.show()
##################################################

##################################################
# cluster no is 29 0r 52 : kmean clustering
c = 0
current_list = truncated_list  #new_missed_list #missed_list
score_string = ''
cluster1_size = 29 #55
while c < 0:
    c = c + 1
    clustering_reuslt, sil_score = clusering(current_list, cluster1_size)
    print( 'score = ' + str(sil_score))
    printClutersNaddToDB(cluster1_size, clustering_reuslt, current_list, c)

###################################################

###################################################################################################
###################################################################################################
###################################################################################################

# THRID START ....................................................................
# https://ai.intelligentonlinetools.com/ml/k-means-clustering-example-word2vec/
# If still not good try following clustering
from gensim.models import Word2Vec
from nltk.cluster import KMeansClusterer
import nltk
from sklearn import cluster
from sklearn import metrics

# clean the missed list
new_missed_list =[]
for x in missed_list:
    cleaned = clean(x)
    cleaned = ' '.join(cleaned)
    new_missed_list.append(cleaned)

# remove duplicates
new_missed_list = list(dict.fromkeys(new_missed_list))
print('after cleaned: '+str(len(new_missed_list)))

# generate word list
sentence_list_of_words = []
for sentence in new_missed_list:
    word_list = sentence.split(" ")
    if len(word_list) ==1:
        sentence_list_of_words.append(word_list[0])
print(sentence_list_of_words)
print('sentence_list_of_words: '+str(len(sentence_list_of_words)))
# training data
sentences = sentence_list_of_words
# training model
model = Word2Vec(sentences, min_count=1)

# get vector data
X = model[model.wv.vocab]

NUM_CLUSTERS = 15
kclusterer = KMeansClusterer(NUM_CLUSTERS, distance=nltk.cluster.util.cosine_distance, repeats=25)
assigned_clusters = kclusterer.cluster(X, assign_clusters=True)
print(assigned_clusters)

words = list(model.wv.vocab)
kmeans = cluster.KMeans(n_clusters=NUM_CLUSTERS)
kmeans.fit(X)

labels = kmeans.labels_
centroids = kmeans.cluster_centers_


from sklearn.decomposition import PCA
pca = PCA(n_components=2, random_state=0)
reduced_features = pca.fit_transform(X)

# reduce the cluster centers to 2D
reduced_cluster_centers = pca.transform(kmeans.cluster_centers_)

# plt.scatter(reduced_features[:, 0], reduced_features[:, 1], c=kmeans.predict(X))
# plt.scatter(reduced_cluster_centers[:, 0], reduced_cluster_centers[:, 1], marker='x', s=150, c='b')
# plt.show()

clustering = collections.defaultdict(list)
original_list = sentences
for idx, label in enumerate(kmeans.labels_):
    clustering[label].append(idx)

for c, v in enumerate(clustering):
    print('........................................................')
    cluster_size = len(clustering[v])
    print(str(c) + '. size =  ' + str(cluster_size))
    ##f.write(str(c) + '. size =  ' + str(cluster_size) +'\n')
    print(clustering[v])

    for index in clustering[v]:
        print(sentence_list_of_words.__getitem__(index))
#########################################################################################

###################################################################################################
###################################################################################################
###################################################################################################

# FOURTH START ....................................................................
print('##################################################################################')
# https://science.sciencemag.org/content/315/5814/972
# https://stats.stackexchange.com/questions/123060/clustering-a-long-list-of-strings-words-into-similarity-groups

import numpy as np
import sklearn.cluster
import distance

words = sentence_list_of_words # single words left from rxnlp and kmean clustering
words = np.asarray(words) #So that indexing with a list will work
lev_similarity = -1*np.array([[distance.levenshtein(w1,w2) for w1 in words] for w2 in words])

affprop = sklearn.cluster.AffinityPropagation(affinity="precomputed", damping=0.5)
affprop.fit(lev_similarity)
for cluster_id in np.unique(affprop.labels_):
    exemplar = words[affprop.cluster_centers_indices_[cluster_id]]
    cluster = np.unique(words[np.nonzero(affprop.labels_==cluster_id)])
    cluster_str = ", ".join(cluster)
    print(" - *%s:* %s" % (exemplar, cluster_str))
    # print(exemplar)
    # print(cluster_str)

    # # ////////////////Add database record ////////////////////
    sql = "INSERT INTO all_rxnlp_clusters (cluster_label, cluster,cluster_size) VALUES (%s, %s, %s)"
    val = (str(exemplar),str(cluster_str), str(cluster_size))
    # mycursor.execute(sql, val)
    # mydb.commit()
    #print(mycursor.rowcount, "record inserted.")
    # ////////////////End adding database record /////////////

#########################################################################################

###################################################################################################
###################################################################################################
###################################################################################################

# Summarize the labels
sql1 = "SELECT DISTINCT cluster_label FROM all_rxnlp_clusters "
mycursor.execute(sql1)
cluster_labels = mycursor.fetchall()
rc = mycursor.rowcount
print('cluster labels count: ' + str(rc))

for label in cluster_labels:
    # clean label
    label  = label[0].replace("'","").replace(",","")
    # retrieve clusters belong to the label
    sql1 = "SELECT cluster, cluster_size FROM all_rxnlp_clusters WHERE cluster_label = '"+ str(label)+"'"
    mycursor.execute(sql1)
    clusters = mycursor.fetchall()
    rc = mycursor.rowcount
    print('cluster count: ' + str(rc))
    print(clusters)
    cluster_size = 0
    string_clusters=''
    # aggregate them
    if rc>1:
        new_cluster_string_list = []
        for cluster in clusters:
            # clean data
            cluster = cluster[0].replace("'", "")
            new_cluster_string_list.append(cluster)
            cluster_size = cluster_size + int(cluster[1],36)


        seperator = ','
        string_clusters = seperator.join(new_cluster_string_list)

    elif rc == 1:
        string_clusters = clusters[0][0].replace("'", "")
        cluster_size = int(clusters[0][1],36)
    # add them to the new table all_rxnlp_clusters_smmarized
    print(cluster_size)

    # # ////////////////Add database record ////////////////////
    sql = "INSERT INTO all_rxnlp_clusters_smmarized (cluster_label, cluster,cluster_size) VALUES (%s, %s, %s)"
    val = (str(label),str(string_clusters), str(cluster_size))
    # mycursor.execute(sql, val)
    # mydb.commit()
    #print(mycursor.rowcount, "record inserted.")
    # ////////////////End adding database record /////////////

#########################################################################################

###################################################################################################
###################################################################################################
###################################################################################################

# add the final clusters to new table

sql1 = "SELECT cluster_label, cluster FROM all_rxnlp_clusters_smmarized "
mycursor.execute(sql1)
clusters = mycursor.fetchall()

for record in clusters:
    label = record[0]
    cluster_list = record[1].split(',')
    new_cluster_list = list(dict.fromkeys(cluster_list))
    cluster_size = len(new_cluster_list)
    seperator = ','
    string_clusters = seperator.join(new_cluster_list)
    # # ////////////////Add database record ////////////////////
    print(string_clusters)
    sql = "INSERT INTO final_clusters (cluster_label, cluster,cluster_size) VALUES (%s, %s, %s)"
    val = (str(label),str(string_clusters), str(cluster_size))
    # mycursor.execute(sql, val)
    # mydb.commit()
    #print(mycursor.rowcount, "record inserted.")
    # ////////////////End adding database record /////////////

#########################################################################################

###################################################################################################
###################################################################################################
###################################################################################################

# create field_label table

sql1 = "SELECT DISTINCT field_label FROM Service_Configuration WHERE field_type = 'text'"
mycursor.execute(sql1)
search_results = mycursor.fetchall()
rc = mycursor.rowcount
print('distinct fields : '+str(rc))

# retrieve clusters belong to the label
# sql2 = "SELECT cluster_label FROM final_clusters WHERE cluster like '%," + cleaned_field + ",%' or cluster like '%," + cleaned_field + "' or cluster like '" + cleaned_field + ",%' or cluster like '%" + cleaned_field + ",%'  and cluster not like '% " + cleaned_field + ",%' or cluster like '%," + cleaned_field + "%' and cluster not like '%," + cleaned_field + " %'"
sql2 = "SELECT cluster_label, cluster FROM final_clusters"
mycursor.execute(sql2)
final_clusters = mycursor.fetchall()

b = 0
cluster_dict = {}
for cluster in final_clusters:
    b = b + 1
    cluster_label = cluster[0].strip()
    clusterV = cluster[1].strip()
    cluster_value_list = clusterV.split(",")
    cluster_dict[cluster_label] = cluster_value_list

print(cluster_dict)

for field in search_results:
    c = c + 1
    original_field = field[0].strip() #//
    print(str(c) +'.) original_field : ' + original_field)
    cleaned_field = clean(original_field)
    cleaned_field = ' '.join(cleaned_field)#//
    print('cleaned_field : ' + cleaned_field)

    labels = []
    string_labels = ''
    for dic in cluster_dict:
        label = dic
        cluster_values = cluster_dict[dic]
        #check if the cleaned field in the cluster_values
        if cleaned_field in cluster_values:
            labels.append(label)

    seperator = ','
    string_labels = seperator.join(labels)  # //
    # # ////////////////Add database record ////////////////////
    print(string_labels)
    sql = "INSERT INTO field_label (text_field, cleaned_field, cluster_labels) VALUES (%s, %s, %s)"
    val = (str(original_field),str(cleaned_field), str(string_labels))
    # mycursor.execute(sql, val)
    # mydb.commit()
    #print(mycursor.rowcount, "record inserted.")
    # ////////////////End adding database record /////////////

