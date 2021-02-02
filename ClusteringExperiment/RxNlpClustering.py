from builtins import print
import mysql.connector
from pyrxnlp.api.cluster_sentences import ClusterSentences
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
import re
import collections
from sklearn.metrics import silhouette_score
import random

# PAPER: http://rxnlp.com/api-citation/#.XZMGBnWWaV4
# replace this with your api key (see: http://www.rxnlp.com/api-key/)
apikey = "298356655amsha2cb9bdd684ee4fp18476bjsn183eb62f9613"

#////////// Setup Database ///////////////
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="root",
  database="ta_tester"
)
mycursor = mydb.cursor()
#///////////End database setup //////////////

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

#/////////////// 1. Retreive triggers from DB //////////////////
sql1 = "SELECT DISTINCT field_label FROM Service_Configuration WHERE field_type = 'text'" #type_of_trigger_or_action = 'trigger' and  #service_identifier,field_name,
mycursor.execute(sql1)
trigger_results = mycursor.fetchall()
rc = mycursor.rowcount
print('initial : '+str(rc))
train_clean_sentences = []
# #///////////////////////////////////////////////
# for x in trigger_results:
#     x = x[2].strip()
#     train_clean_sentences.append(x)

for x in trigger_results:
    x = x[0].strip()
    cleaned = clean(x)
    cleaned = ' '.join(cleaned)
    train_clean_sentences.append(cleaned)

# remove duplicates
train_clean_sentences = list(dict.fromkeys(train_clean_sentences))
print('after cleaned: '+str(len(train_clean_sentences)))
# initialize sentence clustering
clustering = ClusterSentences(apikey)

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

    s = silhouette_score(X, labels=modelkmeans.predict(X))
    print(s)
    return clustering, s

def printCluters(cluster1_size,clusters, original_list,i):
    for c, v in enumerate(clusters):
        print('...........................................................................................................')
        cluster_size = len(clusters[v])
        print(str(c) + '. size =  ' + str(cluster_size))
        ##f.write(str(c) + '. size =  ' + str(cluster_size) +'\n')
        print(clusters[v])
        next_list_for_clustering = []
        for index in clusters[v]:
            print(original_list.__getitem__(index))
            next_list_for_clustering.append(original_list.__getitem__(index))
    return

def addNewClustersToDB(clusters, original_list):
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
                cluster_sentence_list.append(cluster_sentences[sents])
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
                # mycursor.execute(sql, val)
                # mydb.commit()
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

# check results
c = 0
while c<5:
    clusters = clustering.cluster_from_list(train_clean_sentences)
    if clusters is not None:
        print("------------------------------")
        print("Clusters from a list of sentences")
        print("------------------------------")
        clustering.print_clusters(clusters)
    new_list, remainning, sentence_count = addNewClustersToDB(clusters,train_clean_sentences)
    c = c +1
    train_clean_sentences = new_list
    print ('all sentences : '+ str(len(sentence_count)))
    print('remainning : ' + str(len(remainning)))
    print(remainning)
############################################## DONE ##########################################
