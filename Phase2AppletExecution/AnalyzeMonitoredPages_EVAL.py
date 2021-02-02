# !/usr/bin/python2.7
from htmltreediff import diff
from bs4 import BeautifulSoup
import os
from dateutil.parser import parse
import json
from pymongo import MongoClient
import timeit
from bson import json_util
import ast
import hashlib
import base64
import timeit
import requests
############### USER MANUAL ###############################
# SET THE LIST OF SERVICES FOR ANALYZING
# CHANGE THE current_trigger_service
# SPECIFY htmldiff or textdiff
# RUN THE SCRIPT
########################################################################################################################
############################################## DATABASE CONNECTION #####################################################
current_trigger_service = 'android_photos' ####################################################################################
applet_folder_name = 'applets_'+current_trigger_service+'_1'
########################################### prepare folder
directory_name = 'scraped_monitoring (' + current_trigger_service + ' 1)'
alterend_directory_name = 'scraped_monitoring'
if os.path.isdir(directory_name):
    print('directory exists. so rename it!')
    os.rename(directory_name, alterend_directory_name)
##########################################

uri = 'mongodb://127.0.0.1:27017'
client = MongoClient(uri)
tempDB = client.get_database('newevaltemplates')# previously actionmonitor
authDB= client.get_database('services')
resDB= client.get_database(applet_folder_name)
authcollection = authDB.get_collection('monitorauthdetails')
resultcollectionByText = resDB.get_collection('textdiff')
resultcollectionByHtml = resDB.get_collection('htmldiff')
method = None
# for x in authcollection.find({}):
#     try:
#         y = x['service_idnetifier']
#     except KeyError:
#         print(x)
#         #authcollection.delete_one(x)
BASE_FOLDERNAME = None

###############################################
db = client[applet_folder_name]
scollection = db.get_collection('succeed')
fcollection = db.get_collection('failed')
###############################################
###############################################
appletDB = client['evalapplets']
appletcollection = appletDB.get_collection(applet_folder_name)
###############################################

private_keywords = ['onlyme', 'self', 'private','personal']
public_keywords = ['anyone', 'public', 'everyone']
public_resonse = ['200'] ## check key words for failure
private_response = ['403','401']
not_available_response = ['404','400', '502']


########################################################################################################################


def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.
    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False
    except Exception:
        return False

def make_hash_sha256(o):
    hasher = hashlib.sha256()
    hasher.update(repr(make_hashable(o)).encode())
    return base64.b64encode(hasher.digest()).decode()
def make_hashable(o):
    if isinstance(o, (tuple, list)):
        return tuple(sorted((make_hashable(e) for e in o)))

    if isinstance(o, dict):
        return tuple(sorted((k,make_hashable(v)) for k,v in o.items()))

    if isinstance(o, (set, frozenset)):
        return tuple(sorted(make_hashable(e) for e in o))

    return o
######################################################
def compareSummaryDictFurther (dictOld, dictNew):
    if dictOld.items()[0][1].__len__() != dictNew.items()[0][1].__len__() or dictOld.items()[1][1].__len__() != dictNew.items()[1][1].__len__():
        return 0
    else:
        counterV = 0
        counterC = 0
        if dictOld.items()[0][1].__len__() > 0:
            for x in dictOld.items()[0][1]:
                for xx in dictNew.items()[0][1]:
                    if x == xx:
                        counterV = counterV + 1

        if dictOld.items()[1][1].__len__() > 0:
            for x in dictOld.items()[1][1]:
                for xx in dictNew.items()[1][1]:
                    # print(x)
                    # print(xx)
                    if x == xx:
                        counterC = counterC +1
                        break
        if counterV == dictOld.items()[0][1].__len__() and counterC == dictOld.items()[1][1].__len__():
            return 1
##### unicode case
def compareUs(x , y, b):
    if isinstance(x, str):
        x = json.loads(x)
        y = json.loads(y)
        #### Required in Python 2.7
        # if isinstance(y,unicode):
        #     y = json.loads(y)
    if isinstance(x, dict):
        if b:
            return compareSummaryDictFurther(x,y)
        else:
            return compareSummaryDictFurther(x, y)
    elif isinstance(x, list):
        for litem in x:
            if isinstance(litem, str):
                litem = json.loads(litem)
                y = json.loads(y)

            if b:
                result = compareSummaryDictFurther(x, y)
            else:
                result = compareSummaryDictFurther(litem, y)
            if result == 1:
                return 1
        return 0
def compare (listOld, listNew, b):
    if isinstance(listOld, dict):
        xx = [ast.literal_eval(json.dumps(listOld))]
        return compareUs(xx[0], listNew,b)

    if listOld.__len__() == 1:
        return compareUs(listOld[0], listNew[0],b)
    elif listOld.__len__() > 1:
        for lo in listOld:
            result = compareUs(lo,  listNew[0],b)
            if result == 1:
                return 1
        return 0
def compareSummaryDict(summDict1, summDict2):
    if summDict1.items() == summDict2.items():
        for sd1 , sd1v in summDict1.items():
            for sd2, sd2v in summDict2.items():
                if sd1 == sd2:
                    for sd2vitem in sd2v:
                        sd2item = [sd2vitem]
                        if compare (sd1v,sd2item, True) == 0:
                            return 0
    else:
        return 1
def getDeltedAndInsertedContent(deletedContent,insertedContent):
    deleted = []
    for delC in deletedContent:
        deletedTags = []
        for element in delC.find_all():
            currentD = []
            tagName = element.name
            tagContent = json.dumps(element.attrs)  # remove 'u in list
            tag = json.dumps({'tag': tagName})
            currentD.append(tag)
            currentD.append(tagContent)
            deletedTags.append(currentD)

        deleted.append(deletedTags)

    #### Get the inserted content with attributes ###############################
    inserted = []
    for insC in insertedContent:
        inssetedTags = []
        for elementI in insC.find_all():
            currentI = []
            tagNameI = elementI.name
            tagContentI = json.dumps(elementI.attrs)  # remove 'u in list
            tagI = json.dumps({'tag': tagNameI})
            currentI.append(tagI)
            currentI.append(tagContentI)
            inssetedTags.append(currentI)

        inserted.append(inssetedTags)
    return deleted,inserted
    #################################################
def findConstantsAndVariablesInTermsOfDeletionsInNewPage(delContJson, insContJson):
    constants = []
    variables = []
    for delK, delV in delContJson.items():
        for insK, insV in insContJson.items():
            if delK == insK:
                if delContJson[delK] == insContJson[insK]:
                    if delK == 'class':
                        try:
                            constants.append(delK + '=' + delContJson[delK])  # class name
                        except TypeError:
                            clsN = ''
                            for cn in delContJson[delK]:
                                #clsN = clsN + cn ############### UPDATINGGGGGGG .........
                                clsN = clsN + ' '+ cn
                            constants.append(delK + '=' + clsN)  # class name
                    else:
                        try:
                            constants.append(delK + '=' + delContJson[delK])
                        except TypeError:
                            valN = ''
                            for cn in delContJson[delK]:
                                valN = valN + cn
                            constants.append(delK + '=' +valN)
                else:
                    if delK == 'class':
                        continue
                    variables.append(delK)

    return constants,variables
def isDeletedItemEqualInserted(deletedI, inseredI):
    for di in deletedI:
        for ii in inseredI:
            if di[0] in ii:
                return True
    return False
### alteration is defined as ====> specifiy deleted or removed tags in the new page
def analyzeDeletedAndInsertedContent(deleted,inserted):
    print('Begin  analyzeDeletedAndInsertedContent()---->')
    ### FORMAT OF AN ARRAY ITEM [tag (type is dict), attributes (type is dict)]
    # print(len(deleted))
    alteredTags = {}
    newInsertedTags = []

    for insItemSet in inserted:
        # print('###################################################')
        # print('check this inserted item: ')
        # print(insItemSet)
        # print('###################################################')
        if insItemSet.__len__() > 0:
            countMatched = 0
            itemAddedToNewItem = False
            if deleted:
                for delItemsSet in deleted:
                    ## If the inserted not included in any delete set it is a totally new content
                    ## IF the inserted size = deleted size, that means an alteration has happend
                    if (insItemSet.__len__() == delItemsSet.__len__() and isDeletedItemEqualInserted(delItemsSet,insItemSet)):
                        # print('is an deleted item = hence may be altered')
                        print('DELTED FOUND !!!!!!!!!!!!11')
                        #################################################################
                        ## Compare and find constants and variables #####################
                        nowDeleted = delItemsSet
                        poteInserted = insItemSet
                        for nD in nowDeleted:
                            tagND = nD[0]
                            tagNDContent = nD[1]
                            for pI in poteInserted:
                                tagNI = pI[0]
                                tagNIContent = pI[1]
                                TagConstandVar = {}
                                if tagND[0] is tagNI[0]:  # if tag name is correct in both Del and Ins
                                    delContJson = json.loads(tagNDContent)
                                    insContJson = json.loads(tagNIContent)
                                    ########################################################################
                                    constants, variables = findConstantsAndVariablesInTermsOfDeletionsInNewPage(
                                        delContJson,
                                        insContJson)
                                    if constants.__len__() + variables.__len__() == len(delContJson):
                                        TagConstandVar['constants'] = constants
                                        TagConstandVar['variables'] = variables
                                        dictInList = [json.dumps(TagConstandVar)]
                                        if tagND in alteredTags:
                                            existList = alteredTags[tagND]
                                            if compare(existList, dictInList, False) != 1:
                                                alteredTags[tagND] = existList + dictInList
                                        else:
                                            alteredTags[tagND] = dictInList
                    else:
                        countMatched = countMatched + 1
                        if countMatched == deleted.__len__():
                            ###################################UNDER EXPERIMENT ########################>>>>>>>>>>>>>>>>>>
                            # if not equal with any deleted item => then check for the deletedItem closer to the inserted OR
                            # try removing items in the deleted set one by one => check which delted itme can remove more from the inserted ITME
                            # This is to reduce the size of the inserted item (since sometimes inserted item includes existing data which were deleted)
                            for delItemsSet in deleted:
                                newINSET = []
                                for iI in insItemSet:
                                    found = False
                                    hashTagI = iI[0]
                                    hashContentI = iI[1]
                                    temp = []  # track the no of times and item appear in the deletedset , hence not all in the inserted will be removecs
                                    for dI in delItemsSet:
                                        hashTagD = dI[0]
                                        hashContentD = dI[1]
                                        if hashTagI == hashTagD:
                                            if hashContentI == hashContentD:
                                                temp.append(hashContentD)
                                                if temp.count(hashContentD) < delItemsSet.count(dI):
                                                    found = True

                                    if not found:
                                        newINSET.append(iI)
                                if len(newINSET) < len(insItemSet):
                                    newInsertedTags.append(newINSET)
                                    itemAddedToNewItem = True
                                    # if ['{"tag": "div"}','{"class": ["ynRLnc"]}'] in newINSET:
                            if not itemAddedToNewItem:
                                newInsertedTags.append(insItemSet)
                            ############################################################################>>>>>>>>>>>>>>>>>>
            else:
                newInsertedTags.append(insItemSet)
    print('End  analyzeDeletedAndInsertedContent()---->')
    return alteredTags,newInsertedTags
def analyzeDeletedAndInsertedContentUPDATED(deleted,inserted):
    print('Begin  analyzeDeletedAndInsertedContentUPDATED()---->')
    ### FORMAT OF AN ARRAY ITEM [tag (type is dict), attributes (type is dict)]
    # print(len(deleted))
    alteredTags = {}
    newInsertedTags = []
    movedcontentTags = []
    print('inserted' + str(len(inserted)))
    print('deleted' + str(len(deleted)))
    print(deleted)
    for insItemSet in inserted: # list of lists
        ### an itemset is corresponding to a unique tag name e.g., div, iframe, etc.
        # print('###################################################')
        # print('check this inserted item: ')
        #print(insItemSet)
        # print('###################################################')
        if insItemSet.__len__() > 0:
            countMatched = 0
            itemAddedToNewItem = False
            ########################
            ###### go through each item in the itemset
            for iitem in insItemSet: # list of [dict, dict]
                # iitem => inserted item [dict, dict] =>  e.g., [{tag, x}, {attributes...}]
                # print('inserted item: ')
                #print(iitem)
                deletedItemFound = False
                if deleted:
                    ## deleted item sets  exist
                    for delItemsSet in deleted:# list of lists
                        if not deletedItemFound:
                            ######## go through each deleted item in the itemset
                            for ditem in delItemsSet:  # list of [dict, dict]
                                if not deletedItemFound:
                                    # ditem = deleted item e.g., {tag, y},{attributes...}
                                    ######################################################
                                    ###### first check if the iitem's tag equal ditem's tag==> if not continue
                                    if json.loads(iitem[0])['tag'] == json.loads(ditem[0])['tag']:
                                        ########## check the attribute set size is equal
                                        iattrs = json.loads(iitem[1])
                                        dattrs = json.loads(ditem[1])
                                        # added bcoz of facebook case
                                        if 'nonce' in iattrs.keys():
                                            iattrs.pop('nonce')
                                        if 'nonce' in dattrs.keys():
                                            dattrs.pop('nonce')

                                        if len(iattrs) == len(dattrs):
                                            if (cmp(iattrs, dattrs)) == 0:
                                                itemattrs = json.loads(iitem[1]) # attrs
                                                deletedItemFound = True
                                                #print('delted DELETED ITEM FOUND !!!!!!!')
                                                # if the item has class attribute and it is a list then correct the class name before update tht class name
                                                # check keys of the attriubtes dict
                                                if 'class' in itemattrs.keys():
                                                    classAttr = itemattrs['class']
                                                    classValue = ''
                                                    if type(classAttr) == list:
                                                        for cav in classAttr:
                                                            classValue = classValue + ' '+cav
                                                            classValue = classValue.strip()

                                                        ## remove the class item and add the new class
                                                        del itemattrs['class']
                                                        itemattrs['class'] = classValue
                                                        ## remove the attrs from the list [dict,dict] and add the new attrs
                                                        iitem.remove(iitem[1])
                                                        iitem.append(itemattrs)
                                                movedcontentTags.append(iitem)

                                        else:
                                            continue
                                    else:
                                        continue



                if not deletedItemFound:
                    #print('NOT FOUND')
                    itemattrs = json.loads(iitem[1])  # attrs
                    if 'class' in itemattrs.keys():
                        classAttr = itemattrs['class']
                        classValue = ''
                        if type(classAttr) == list:
                            for cav in classAttr:
                                classValue = classValue + ' ' + cav
                                classValue = classValue.strip()

                            ## remove the class item and add the new class
                            del itemattrs['class']
                            itemattrs['class'] = classValue
                            ## remove the attrs from the list [dict,dict] and add the new attrs
                            iitem.remove(iitem[1])
                            iitem.append(itemattrs)
                    #movedcontentTags.append(iitem)
                    newInsertedTags.append(iitem)

    print('End  analyzeDeletedAndInsertedContent()---->')
    return alteredTags,newInsertedTags, movedcontentTags
def htmlDiffAnalysis(x,y):
    print('BEGIN HTML tree analysis ---->')
    s1 = timeit.default_timer()
    htmlAdjcentDiffResult = diff(y,x, pretty=False)
    e1 = timeit.default_timer()
    print('Time for diff library function= '+ str(e1-s1))
    ############################################################################
    ########### Extract deleted and inserted content for each occurence of url##
    htmlAdjacentDiffContent = BeautifulSoup(htmlAdjcentDiffResult, "html.parser")
    #print(htmlAdjacentDiffContent.prettify() )
    deletedContent = htmlAdjacentDiffContent.findAll('del', recursive=True)
    insertedContent = htmlAdjacentDiffContent.findAll('ins', recursive=True)
    ############################################################################
    ###### For all scraped occurences ##########################################
    #### Get the deleted content with attributes ###############################
    s2 = timeit.default_timer()
    deleted, inserted = getDeltedAndInsertedContent(deletedContent, insertedContent)
    e2 = timeit.default_timer()
    print('Time getDeltedAndInsertedContent function= ' + str(e2 - s2))
    #############################################################################
    ################# Each Scraped PAGE #########################################
    #### Compare deleted vs inserted tags #######################################
    #############################################################################
    s3 = timeit.default_timer()
    alteredTags, newInsertedTags, movedcontentTags = analyzeDeletedAndInsertedContentUPDATED(deleted, inserted)
    e3 = timeit.default_timer()
    print('Time analyzeDeletedAndInsertedContent function= ' + str(e3 - s3))
    print('Time htmlDiffAnalysis function= ' + str(e3 - s1))
    print('END HTML tree analysis ---->')
    return alteredTags, newInsertedTags, movedcontentTags
def linkanalysis(url, response, publicurl, privateurl,otheresponse):#lists
    hasPublicURL = False
    hasPrivateURL = False
    for pub in public_resonse:
        if pub == str(response.status_code):
            hasPublicURL = True
            publicurl.add(url)
    for pri in private_response:
        if pri == str(response.status_code):
            hasPrivateURL = True
            privateurl.add(url)
    for oth in not_available_response:
        if oth == str(response.status_code):
            otheresponse.add(url)

    i

    return hasPublicURL, hasPrivateURL, publicurl, privateurl,otheresponse
def linkanalysis2(url, response, publicurl, privateurl,otheresponse):# .,.,dict, dict, list
    print(url)
    print(response)
    for pub in public_resonse:
        if pub == str(response.status_code):
            publicurl.add(url)
    for pri in private_response:
        if pri == str(response.status_code):
            privateurl.add(url)
    for oth in not_available_response:
        if oth == str(response.status_code):
            otheresponse.add(url)
    return publicurl, privateurl,otheresponse
def textanalysis(parentString,privatetext,publictext):
    hasPrivateText = False
    hasPublicText = False
    normlaizedstring = parentString.lower().replace(' ', '').replace('-', '').replace('_', '')
    for seckey in private_keywords:
        if seckey in normlaizedstring:
            hasPrivateText = True
            privatetext.add(seckey)

    for pubkey in public_keywords:
        if pubkey in normlaizedstring:
            hasPublicText = True
            publictext.add(pubkey)
    return hasPublicText, hasPrivateText,privatetext,publictext
def htmlTEXTDiffAnalysis(first, second, service, page, collection,domains):
    print('BEGIN HTML TEXT analysis ---->')
    ############################################################################
    ########### Extract deleted and inserted content for each occurence of url##
    firsthtml = BeautifulSoup(first, "html.parser")
    secondhtml = BeautifulSoup(second, "html.parser")
    # print(htmlAdjacentDiffContent.prettify() )
    # divFirsthtml = firsthtml.findAll('div', recursive=True)
    # divSecondhtml = secondhtml.findAll('div', recursive=True)
    divFirsthtml = [s.get_text(separator="\n", strip=True) for s in firsthtml.find_all('div', recursive=True)]
    divSecondhtml = [s.get_text(separator="\n", strip=True) for s in secondhtml.find_all('div', recursive=True)]

    firstSet = set()
    secondSet = set()

    print('text from the first page (0) : ')
    firstseen = set()
    for dfh in divFirsthtml:
        if dfh in firstseen:
            continue
        else:
            firstseen.add(dfh)
        #print(dfh)
        values  = dfh.split(os.linesep)
        for vl in values:
            if len(vl.strip()) < 2:
                continue
            if vl.strip() not in ['', '.', ',','-', '_'] and not vl.strip().isnumeric() and not is_date(vl.strip()) and vl.strip() not in firstSet:
                vl = vl.encode('utf-8')
                if dfh.strip() != '':
                    firstSet.add(vl)

    print('text from the second page (1) :')
    secondseen = set()
    for dfh in divSecondhtml:
        if dfh in secondseen:
            continue
        else:
            secondseen.add(dfh)
        values  = dfh.split(os.linesep)
        for vl in values:
            if len(vl.strip()) < 2:
                continue
            if vl.strip() not in ['', '.', ',','-', '_'] and not vl.strip().isnumeric() and not is_date(vl.strip()) and vl.strip() not in secondSet:
                vl = vl.encode('utf-8')
                if dfh.strip() != '':
                    secondSet.add(vl)

    print('#############################')
    extracted_data = {}
    privacyof_text = {}
    privacyof_url = {}
    for x in firstSet:
        if x in secondSet:
            pass
        else:
            print('########')
            print(x)
            hasPrivateText = False
            hasPublicText = False
            privatetext = set()
            publictext = set()
            hasPrivateURL = False
            hasPublicURL = False
            privateurl= set()
            publicurl = set()
            otheresponse = set()
            data = set()
            fh = firsthtml.findAll('div', text=x)
            if len(fh) == 0:
                fh = firsthtml.findAll('span', text=x)
            for fhi in fh:
                parentfjhi = fhi.parent.parent
                #############################################################################
                ### get the tags as a string to find privacy related keywords of text content
                parentString = parentfjhi.encode('utf-8')
                data.add(parentString)# add all tags
                hasPublicText, hasPrivateText,privatetext,publictext = textanalysis(parentString, privatetext, publictext)
                ########################################################
                ####### get all urls in the tags, and check accessiblity
                fimg = parentfjhi.findAll('img', recursive=True)

                for m in fimg:
                    print('##img##')
                    print(m)
                    try:
                        url = m.attrs['src'].replace('amp;','')
                        if url.startswith('./'):
                            url = url.replace('./', '/')
                            if domains is list:
                                domains = domains[0]
                            url = 'https://' + domains + url
                        elif url.startswith('/'):
                            if domains is list:
                                domains = domains[0]
                            url = 'https://' + domains + url
                        response = requests.get(url,timeout=20)
                        print(url)
                        print(response)
                        ######
                        if response is not None:
                            hasPublicURL, hasPrivateURL,  publicurl, privateurl,otheresponse = linkanalysis(url, response, publicurl, privateurl,otheresponse)
                        #######
                    except Exception:
                        print('exception occurd')
                    data.add(m.encode('utf-8')) # add url
                fa = parentfjhi.findAll('a', recursive=True)
                for a in fa:
                    print('##aaa##')
                    print(a)
                    try:
                        url = a.attrs['href']
                        url = url.replace('amp;', '')
                        if url.startswith('./'):
                            url = url.replace('./', '/')
                            if domains is list:
                                domains = domains[0]
                            url = 'https://' + domains + url
                        elif url.startswith('/'):
                            if domains is list:
                                domains = domains[0]
                            url = 'https://' + domains + url
                        response = requests.get(url, timeout=20)
                        #########
                        print(url)
                        print(response)
                        if response is not None:
                            hasPublicURL, hasPrivateURL,  publicurl, privateurl,otheresponse = linkanalysis(url, response, publicurl, privateurl,otheresponse)
                        #########
                    except Exception:
                        print('exception occurd')
                    data.add(a.encode('utf-8'))
                #########################################################
            privacyof_url[x] = {'has_private_url': hasPrivateURL, 'private_url': list(privateurl), 'has_public_url': hasPublicURL, 'public_url': list(publicurl), 'other_urls': list(otheresponse)}
            privacyof_text[x] = {'has_private_text':hasPrivateText, 'private_text' : list(privatetext),'has_public_text':hasPublicText,'public_text':list(publictext)}
            extracted_data[x] = list(data)
    print('######### update db #############')
    collection.update({'service_idnetifier': service},
                       {'$set': {'page': page, 'extracted_data': extracted_data, 'text_privacy':privacyof_text, 'url_privacy':privacyof_url}}, upsert=True)
    ##############################################
def removeTagsFromHTML(htmlCList,tagConetentToBeRemovedList):
    returnUpdatedList = []
    for hcl in htmlCList:
        ph = hcl.encode('ascii')
        hclString = ph.decode('utf-8')
        for tcr in tagConetentToBeRemovedList:
            pt = tcr.encode('ascii')
            tcrString = pt.decode('utf-8')
            if tcrString in hclString:
                hclString = hclString.replace(tcrString,'')
        if hclString.strip() != '':
            returnUpdatedList.append(hclString.replace('\n\n','\n').replace('\n\n','\n'))#replace('\r', '').replace('\n', ''))

    return returnUpdatedList
def orderHTMLnamelist(namelist):
    outputnamelist  = []
    htmlfilename = None
    indexlist = []
    if len(namelist)> 0:
        htmlfilename = namelist[0].split('_')[0]
        for ele in namelist:
            indexlist.append(int(json.loads(ele.split('_')[1].split('.')[0])))
    if htmlfilename is not None:
        indexlist.sort(reverse=True)
        for no in indexlist:
            outputnamelist.append(htmlfilename+ '_'+ str(no)+ '.html')

    return outputnamelist

def getHTMLcontentAsString(v,baseFolderName):
    htmlfileContentsasStrings = []
    v = orderHTMLnamelist(v)
    for fname in v:
        try:
            print(fname)
            filepath = baseFolderName + fname
            f = open(filepath, "r")
            fileContent = f.read()  # .decode('utf-8')
            f.close()
        except IOError:
            return None
        pagecontent = BeautifulSoup(fileContent, "html.parser")
        htmlcontent = pagecontent.findAll('html', recursive=True)
        scrptcontent = pagecontent.findAll('script', recursive=True)
        stylecontent = pagecontent.findAll('style', recursive=True)
        hiddenContent1 = pagecontent.select('[style="display:none"]')
        hiddenContent2 = pagecontent.select('[style="display: none;"]')
        updatedhtml = removeTagsFromHTML(htmlcontent,scrptcontent)
        updatedhtml = removeTagsFromHTML(updatedhtml,stylecontent)
        updatedhtml = removeTagsFromHTML(updatedhtml,hiddenContent1)
        updatedhtml = removeTagsFromHTML(updatedhtml,hiddenContent2)

        # print('updatedhtml')
        # # print(len(updatedhtml))
        # # print(updatedhtml)
        # xx = pagecontent.findAll('div', {'class': 'docs-homescreen-floater-header-cell docs-homescreen-floater-header-title'})
        # print(xx)

        # assuming one html page includes
        if updatedhtml:
            print(len(updatedhtml[0]))
            htmlfileContentsasStrings.append(updatedhtml[0])

    return htmlfileContentsasStrings
def getClusterDetails(htmlfiles):
    clusterbynamedict = {}
    crawledTotalForEachCount = {}
    for htmlf in htmlfiles:
        basename = htmlf.split('_')[0]
        if basename in clusterbynamedict.keys():
            clusterbynamedict[basename].append(htmlf)
        else:
            clusterbynamedict[basename] = [htmlf]
        ###############capture the total of each count number####################
        crawlNo = htmlf.split('_')[1].replace('.html', '')
        crawlN = int(crawlNo)
        if crawlN in crawledTotalForEachCount:
            crawledTotalForEachCount[crawlN] = crawledTotalForEachCount[crawlN] + 1
        else:
            crawledTotalForEachCount[crawlN] = 1 ## so we can assure 4 th run occured successfuly
    return clusterbynamedict, crawledTotalForEachCount
def analyzeTotallyDeleteOrInserted(clusterbynamedict,collection,allSingleOccuredPagesKeys,baseFolderName):
    diffURL = []
    basePageHtmlStrings = []
    basePageHtmlString = []
    totallyDeletedOrInstertedPAges = []
    ######## Base pages include the single pages of the first/min crawl number #######################
    # randomly select the baseDeltePageKey for now
    i = 0
    for kp, vp in clusterbynamedict.items():
        for singlePageKey in allSingleOccuredPagesKeys:
            if kp == singlePageKey and i == 0:
                basePageHtmlString = getHTMLcontentAsString([vp[0]], baseFolderName)
                basePageHtmlStrings.append(basePageHtmlString)
                continue
        if vp.__len__() < 5:
            totallyDeletedOrInstertedPAges.append(vp[0])
    # print(totallyDeletedOrInstertedPAges)
    # print(basePageHtmlString)
    # Deleted Page
    print(totallyDeletedOrInstertedPAges)
    ##################################################################################################
    ############ Open html files and extract only html conntent as a string ##########################
    htmlfileContentsasStrings = getHTMLcontentAsString(totallyDeletedOrInstertedPAges, baseFolderName)

    for htmlS in htmlfileContentsasStrings:
        alteredTagsOfTotalDeletedOrInsertedPages, newInsertedTags, movedcontentTags = htmlDiffAnalysis(basePageHtmlString[0], htmlS)
        diffURL.append(alteredTagsOfTotalDeletedOrInsertedPages)
    print(diffURL)

    baseDictionaryD = diffURL[0]
    counterD = 0
    for summaryDict in diffURL:
        if compareSummaryDict(baseDictionaryD, summaryDict) == 0:
            #print('atleast on instance not equal')
            pageData = {}
            pageData['differentPageDeleteVsInsert1'] = summaryDict
            #collection.insert_one(pageData)
            collection.update(pageData, pageData, upsert=True)
            # print(summaryDict)
        else:
            counterD = counterD + 1
    if counterD > 0:
        pageData = {}
        # print(baseDictionaryD)
        pageData['differentPageDeleteVsInsert2'] = baseDictionaryD
        #collection.insert_one(pageData)
        collection.update(pageData, pageData, upsert=True)
def getSameURLSummary(clusterbynamedict,baseFolderName,service, collection,domains):
    singleOccurenceKeys = []
    summary = {}
    insertedSum = {}
    print(clusterbynamedict)
    for k, v in clusterbynamedict.items():  # k - unique url, v- scraped pages of k url
        print('################# new URL start ....htmldiff analysis ####################################### ' + k)
        if len(v) == 1:  ## If page occured only onces => Reaonse: expired, not crawled
            singleOccurenceKeys.append(k)
            continue
        ###################################################################################################
        ############# Open html files and extract only html conntent as a string ##########################
        print(k)
        print(v)
        htmlfileContentsasStrings = getHTMLcontentAsString(v, baseFolderName)

        print('Got HTML String !!')
        ###################################################################################################
        ################ Compare adjacent scraped pages ###################################################
        ############### Extract constant elements and variable elements ###################################
        sameURL = []
        sameURLInsert = []
        if htmlfileContentsasStrings:
            for i in range(v.__len__()):
                if i == 0 or i == (v.__len__()):
                    print('')
                else:
                    print(i)
                    alteredTags,newInsertedTags,movedcontentTags = htmlDiffAnalysis(htmlfileContentsasStrings[i - 1], htmlfileContentsasStrings[i])
                    print(' page comarison summary: ==============>')
                    print('alteredTags ' + str(alteredTags))
                    print('newInsertedTags' + str(newInsertedTags))
                    print('newInsertedTags size ' + str(len(newInsertedTags)))
                    print('movedcontentTags' + str(movedcontentTags))
                    print('movedcontentTags size ' + str(len(movedcontentTags)))
                    havecommontagsInsertedAndMoved = False
                    ####### check if newlyinserted adn movedcontent tags that are common exists ########################
                    commonitemAsInserted = []
                    for inlistitem in newInsertedTags:
                        for movelistitem in movedcontentTags:
                            if cmp(inlistitem[0], movelistitem[0]) == 0 : #if (cmp(json.loads(iitem[1]), json.loads(ditem[1]))) == 0:
                                if cmp(inlistitem[1], movelistitem[1]) == 0:
                                    commonitemAsInserted.append(inlistitem)
                                    havecommontagsInsertedAndMoved = True

                    print(len(commonitemAsInserted))
                    ####################################################################################################
                    ################### print new tags
                    if not havecommontagsInsertedAndMoved:
                        finalresutlslist_after = getTextOrUrlForATagUPDATED(k, newInsertedTags, 1)
                        finalresutlslist_before = getTextOrUrlForATagUPDATED(k, newInsertedTags, 0)

                        newcontent = []
                        privacyof_url = {}
                        privacyof_text = {}
                        fullString = ''
                        privateurl = set()
                        publicurl = set()
                        otheresponse = set()
                        hasPublicURL = False
                        hasPrivateURL = False
                        has_private_url = False
                        has_public_url = False


                        for rafter in finalresutlslist_after:
                            found = False
                            for rbefore in finalresutlslist_before:
                                if rafter == rbefore:
                                    found = True
                            if not found:
                                print(rafter)
                                print('####')
                                newcontent.append(rafter.encode('utf-8'))
                                newString = rafter.encode('utf-8')
                                fullString = fullString + newString
                                url = None
                                response = None
                                if rafter.name == 'a':
                                    try:
                                        url = rafter.attrs['href']
                                        url = url.replace('amp;', '')
                                        if url.startswith('./'):
                                            url = url.replace('./', '/')
                                            if domains is list:
                                                domains = domains[0]
                                            url = 'https://'+ domains + url
                                        elif url.startswith('/'):
                                            if domains is list:
                                                domains = domains[0]
                                            url = 'https://' + domains + url
                                        response = requests.get(url,timeout=10)
                                    except KeyError:
                                        print('no href key')
                                    except Exception as ex:
                                        ################### check exception details ####################################################
                                        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                                        message = template.format(type(ex).__name__, ex.args)
                                        print (message)
                                        print('exception caught')
                                if rafter.name == 'img':
                                    try:

                                        url = rafter.attrs['src']
                                        url = url.replace('amp;', '')
                                        if url.startswith('./'):
                                            url = url.replace('./', '/')
                                            if domains is list:
                                                domains = domains[0]
                                            url = 'https://' + domains + url
                                        elif url.startswith('/'):
                                            if domains is list:
                                                domains = domains[0]
                                            url = 'https://' + domains + url
                                        response = requests.get(url,timeout=10)

                                    except Exception as ex:
                                        ################### check exception details ####################################################
                                        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                                        message = template.format(type(ex).__name__, ex.args)
                                        print (message)
                                        print('exception caught')
                                    #########
                                if url is not None and response is not None:
                                    print(response)
                                    publicurl, privateurl, otheresponse = linkanalysis2(url, response, publicurl, privateurl, otheresponse)

                        if len(privateurl) > 0:
                            has_private_url = True
                        if len(publicurl) >0 :
                            has_public_url = True
                        ######## find keywords in text ###############
                        hasPublicText, hasPrivateText, privatetext, publictext = textanalysis(fullString, set(), set())
                        print('######### update db #############')
                        privacyof_url = {'has_private_url': has_private_url, 'private_urls':   list(privateurl),
                                         'has_public_url':has_public_url, 'public_urls':  list(publicurl),
                                           'other_urls': list(otheresponse)}
                        privacyof_text = {'has_private_text': hasPrivateText, 'private_text': list(privatetext),
                                             'has_public_text': hasPublicText, 'public_text': list(publictext)}

                        collection.update({'service_idnetifier': service},
                                          {'$set': {'page': k, 'extracted_data': newcontent,'text_privacy':privacyof_text, 'url_privacy':privacyof_url}}, upsert=True)
                    ####################################################################################################

            #         sameURL.append(alteredTags)
            #         if newInsertedTags:
            #             sameURLInsert.append(newInsertedTags)
            #         print('######################## A page of ' + str(
            #             k) + ' done analysis >_< ##################################')
            # summary[k] = sameURL
            # if sameURLInsert:
            #     insertedSum[k] = sameURLInsert
            # print('################# ' + str(
            #     k) + ' ############################### ' + ' DONE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

        # TODO: delete only or insert only
    return summary,insertedSum,singleOccurenceKeys
def getTEXTSummary(clusterbynamedict,baseFolderName, service, collection,domains):
    singleOccurenceKeys = []
    summary = {}
    insertedSum = {}
    print(clusterbynamedict)
    for k, v in clusterbynamedict.items():  # k - unique url, v- scraped pages of k url
        print('################# new URL start ....####################################### ' + k)
        if len(v) == 1:  ## If page occured only onces => Reaonse: expired, not crawled
            singleOccurenceKeys.append(k)
            continue
        ###################################################################################################
        ############# Open html files and extract only html conntent as a string ##########################
        print(k)
        print(v)
        htmlfileContentsasStrings = getHTMLcontentAsString(v, baseFolderName)

        print('Got HTML String !!')
        ###################################################################################################
        ################ Compare adjacent scraped pages ###################################################
        ############### Extract constant elements and variable elements ###################################
        sameURL = []
        sameURLInsert = []
        if htmlfileContentsasStrings:
            for i in range(v.__len__()):
                if i == 0 or i == (v.__len__()):
                    print('')
                else:
                    print(i)
                    htmlTEXTDiffAnalysis(htmlfileContentsasStrings[i - 1], htmlfileContentsasStrings[i], service , k, collection,domains)

################# analyse same URL summary #######>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def compareSummaryDictFurtherB (dictOld, dictNew):
    nonMatchingVarAndCons = {}
    vars = []
    const = []
    if dictOld.items()[0][1].__len__() != dictNew.items()[0][1].__len__() or dictOld.items()[1][1].__len__() != dictNew.items()[1][1].__len__():
        return dictNew # 0
    else:
        counterV = 0
        counterC = 0
        if dictOld.items()[0][1].__len__() > 0:
            for x in dictOld.items()[0][1]:
                for xx in dictNew.items()[0][1]:
                    if x == xx:
                        counterV = counterV + 1
                    else:
                        vars.append(xx)

        if dictOld.items()[1][1].__len__() > 0:
            for x in dictOld.items()[1][1]:
                for xx in dictNew.items()[1][1]:
                    if x == xx:
                        counterC = counterC +1
                        #break
                    else:
                        const.append(xx)
        if counterV == dictNew.items()[0][1].__len__() and counterC == dictNew.items()[1][1].__len__():
            return 1
        else:
            varK = dictNew.items()[0][0] # variables
            consK = dictNew.items()[1][0] # constants
            nonMatchingVarAndCons[varK] = vars
            nonMatchingVarAndCons[consK] = const
            return nonMatchingVarAndCons # 0
def compareUsB(x , y, b):
    if isinstance(x, str):
        x = json.loads(x)
        y = json.loads(y)
        #### Required in Python 2.7
        # if isinstance(y,unicode):
        #     y = json.loads(y)
    if isinstance(x, dict):
        return compareSummaryDictFurtherB(x, y)
    elif isinstance(x, list):
        for litem in x:
            if isinstance(litem, str):
                litem = json.loads(litem)
                y = json.loads(y)
            result = compareSummaryDictFurtherB(x, y)
            if result == 1:
                return 1
        return 0
def compareB(listOld, listNew, b):
    if isinstance(listOld, dict):
        # x = [json.dumps(listOld)]
        # return compareUsB(x[0], listNew[0],b)
        xx = [ast.literal_eval(json.dumps(listOld))]
        return compareUs(xx[0], listNew,b)

    # if listOld.__len__() == 1:
    #     return compareUsB(listOld[0], listNew[0],b)
    if listOld.__len__() >= 1:
        matchCount = 0
        collectNonMatched = []
        for ln in listNew:
            for lo in listOld:
                result = compareUsB(lo, ln, b)
                if result == 1:
                    matchCount = matchCount + 1
                else:
                    if result not in collectNonMatched: ## THIS LINE INCREASES PROCESS TIME 4->6
                        collectNonMatched.append(result)

        if matchCount == listNew.__len__():
            return 1
        else:
            return collectNonMatched
def getTemplates(service_name):
    tempList = []
    collection = tempDB.get_collection(str('templates_' + service_name))
    for template in collection.find({}):
        tempList.append(json.loads(json.dumps(template, indent=4, default=json_util.default)))
    return tempList
def getTemplateMatchWithPage(templates, page):
    pageTemplates = []
    for temp in templates:
        for pageT, pageTemplate in temp.items():
            ### Each page or URL can have several templates
            if pageT == page:
                pageTemplates.append(pageTemplate)
    return pageTemplates
def compareSameURLMonitoredSummaryWithTemplate(template, pagesum):
    allMatched = False
    tempsnonMatchingItems = {}
    tempstagSizeofNotMatched = {}
    tempsmatchingItems = {}
    tempstagSizeofMatched = {}
    tagSuCounter = 0
    for tag, values in pagesum.items():
        tagFound = False
        for tempTag, tempValue in template.items():
            if tag == tempTag:
                tagFound = True
                # print('matching Tag')
                result = compareB(tempValue, values, False)
                if result !=1:
                    # print('atleast on instance not equal')
                    tempsnonMatchingItems[tag] = result #values
                    tempstagSizeofNotMatched[tag] = result.__len__() #values.__len__()
                else:
                    # print('matching with old ')
                    tagSuCounter = tagSuCounter + 1
                    tempsmatchingItems[tag] = values
                    tempstagSizeofMatched[tag] = values.__len__()
        if not tagFound:
            tempsnonMatchingItems[tag] = values
            tempstagSizeofNotMatched[tag] = values.__len__()

    if tagSuCounter == len(pagesum): ## changed from len of template to => len of summary, so all values in summary has to be in the template to be able to all equal
        allMatched = True
    return tempsnonMatchingItems,tempstagSizeofNotMatched,tempsmatchingItems, tempstagSizeofMatched, allMatched

def findTextInResultedTags(tagsforcheck,pagecontent):
    print('####################### findTextInResultedTags################################')
    textInPage = []
    for tag, values in tagsforcheck.items():# tagsforcheck dict
        tagg = ast.literal_eval(tag)  # str to dict convertion
        tagName = tagg['tag']
        # print('tag and values: ')
        # print(tagName)
        # print(values)
        # tagcontents = pagecontent.findAll(tagName, recursive=True)
        for val in values:
            atrValDict = {}
            hasClassatt = False
            if type(val) is str:
                val = ast.literal_eval(val)  # str to dict convertion
            variableAttNames = []
            for varr in val['variables']:
                variableAttNames.append(varr)
            for atriVal in val['constants']:
                # find a div in the corresponding page with a attriubte and a value as specified in the constants
                att = atriVal.split('=')[0]
                valA = atriVal.split('=')[1]
                atrValDict[att] = valA.strip()
                if att == 'class':
                    hasClassatt = True
            if hasClassatt:
                #print('has class so all tags: ') #docs-homescreen-floater-header-cell docs-homescreen-floater-header-title
                # print('pagecontent')
                # print(pagecontent)
                # for pc in pagecontent.findAll(tagName):
                #     print (pc)
                #print(atrValDict)
                # results = pagecontent.find(tagName, atrValDict)
                # print(results)
                #print('######################################################')
                results = pagecontent.findAll(tagName, atrValDict,text=True)
                #print(results)
                #############################################################
                allTags = pagecontent.findAll(tagName, atrValDict)
                #print(allTags)
                for all in allTags:
                    links = all.findAll('a', recursive=True)
                    for lk in links:
                        results.append(lk.get("href"))
                #############################################################
                for r in results:
                    if type(r) is not unicode:
                        if r is not None:
                            rtext = r.text.encode("utf-8")  ##ast.literal_eval(r.text)
                            count = 0
                            for varA in variableAttNames:
                                if r.has_attr(varA):
                                    count = count + 1
                            if variableAttNames:
                                if count == len(variableAttNames):
                                    textInPage.append(rtext)
                            else:
                                textInPage.append(rtext)

                    else:
                        textInPage.append(r)
    print('############################################################')
    return textInPage
def getTextOrUrlForATag(page, tagsummary):
    global BASE_FOLDERNAME
    page1 = str(page) + '_1.html'
    print(BASE_FOLDERNAME)
    try:
        pageHtml1 = getHTMLcontentAsString([page1], BASE_FOLDERNAME)

        if pageHtml1 is not None:
            pagecontent1 = BeautifulSoup(pageHtml1[0], "html.parser")
        print(set(findTextInResultedTags(tagsummary, pagecontent1)))
    except Exception as ex:
        ################### check exception details ####################################################
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print (message)
        print('exception caught')
def findTextInResultedTagsUPDATED(tagsforcheck,pagecontent):
    print('####################### findTextInResultedTagsUPDATED################################')
    #print(pagecontent)
    textInPage = []
    finalresutlslist = []
    count = 0
    cons_value = -1
    #Example: [['{"tag": "div"}', {u'style': u'-moz-user-select: none;', 'class': u'docs-homescreen-list-header', u'id': u':3q'}],...]
    for tagitem in tagsforcheck: #  [dict, dict]
        if count <=cons_value:
            print(tagitem)


        tagitem_name =  json.loads(tagitem[0])['tag']
        if type(tagitem[1]) ==  str:
            tagitem_attrs = json.loads(tagitem[1])
        elif type(tagitem[1]) == dict:
            tagitem_attrs = tagitem[1]

        ### if tagitem attrs' include  class attr
        if 'nonce' in tagitem_attrs.keys():
            tagitem_attrs.pop('nonce')


        # print('###########################')
        # print(tagitem_name)
        # print(tagitem_attrs)


        results = pagecontent.findAll(tagitem_name, tagitem_attrs, text=True)
        if count <= cons_value:
            print(len(results))
        for result in results:
            finalresutlslist.append(result)

        #############################################################
        allTags = pagecontent.findAll(tagitem_name, tagitem_attrs)
        if count <= cons_value:
            print(len(allTags))
        for all in allTags:
            if all.name == 'img' or all.name == 'a' :#or  all.name == 'div':
                finalresutlslist.append(all)

            links = all.findAll('a', recursive=False)
            for lk in links:
                finalresutlslist.append(lk)
            links = all.findAll('img', recursive=False)
            for lk in links:
                finalresutlslist.append(lk)

        count = count + 1

        #############################################################
        # for r in results:
        #     if type(r) is not unicode:
        #         if r is not None:
        #             rtext = r.text.encode("utf-8")  ##ast.literal_eval(r.text)
        #             count = 0
        #             for varA in variableAttNames:
        #                 if r.has_attr(varA):
        #                     count = count + 1
        #             if variableAttNames:
        #                 if count == len(variableAttNames):
        #                     textInPage.append(rtext)
        #             else:
        #                 textInPage.append(rtext)
        #
        #     else:
        #         textInPage.append(r)


    print('############################################################')

    finalresutlslist = list(set(finalresutlslist))
    # for fr in finalresutlslist:
    #     print(fr)

    return finalresutlslist

def getTextOrUrlForATagUPDATED(page, tagsummary, digit):
    global BASE_FOLDERNAME
    page1 = str(page) + '_'+str(digit)+'.html'
    print(BASE_FOLDERNAME)
    try:
        pageHtml1 = getHTMLcontentAsString([page1], BASE_FOLDERNAME)
        if pageHtml1 is not None:
            pagecontent1 = BeautifulSoup(pageHtml1[0], "html.parser")
            # if digit == 1:
            #     print(pagecontent1)
            return findTextInResultedTagsUPDATED(tagsummary, pagecontent1)
    except Exception as ex:
        ################### check exception details ####################################################
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print (message)
        print('exception caught')
def analyzeMonitoredSummaryWithTemplate(tempList, monitoredSummary):
    s4 = timeit.default_timer()
    if not monitoredSummary:
        return
    matchedPages = []
    notmatchedPAges = []
    expiredPages = []
    snonMatchingDictList = []
    for page, pageSummary in monitoredSummary.items():
        ## page summary is from pre and post of a URL => hence only one summary dictionary per URL
        pageSum = pageSummary[0]
        allMatched =  False
        print('page summary tags')
        print(pageSum)
        getTextOrUrlForATag(page, pageSum)

        ################### COMMENTED FOR UPDATED template DB as summary and insertedsummary
        # get the template/templates available under the page URL key
        # templateOrtemplates = getTemplateMatchWithPage(tempList, page)
        ############################## UPDATE here ===>
        #  Since only one page is scrapped ====> only one template is available
        print('tempList size:'  + str(len(tempList)))
        templateOrtemplates = tempList[0]['summary']
        #####################################################################################
        if type(templateOrtemplates) is list:
            #print('several templates for the page URL')
            print('templateOrtemplates' + str(len(templateOrtemplates)))# no of templates
            for template in templateOrtemplates:
                template = ast.literal_eval(json.dumps(template))
                print('template')
                print(template)
                if not allMatched:# initially it is False
                    snonMatchingItems, stagSizeofNotMatched, smatchingItems, stagSizeofMatched, allMatched = compareSameURLMonitoredSummaryWithTemplate(template, pageSum)
                    print('MATCHING items')
                    print(smatchingItems)
                    getTextOrUrlForATag(page, smatchingItems)
                    print('stagSizeof Matched')
                    print(stagSizeofMatched)
                    print('items NOT-MATCHING')
                    print(snonMatchingItems)
                    getTextOrUrlForATag(page, snonMatchingItems)
                    print('stagSizeof NotMatched')
                    print(stagSizeofNotMatched)
                    print('ALL MATCHED')
                    print(allMatched)
                    if not allMatched:
                        stat = []
                        dstat = {}
                        sdetails = {}
                        snonMatchingDict = {}
                        dstat['matchedD'] = stagSizeofMatched
                        dstat['non-matchedD'] = stagSizeofNotMatched
                        sdetails['matched'] = smatchingItems
                        sdetails['non-matched'] = snonMatchingItems
                        sdetails['details'] = dstat
                        stat.append(len(smatchingItems))
                        stat.append(len(snonMatchingItems))
                        stat.append(len(template))
                        sdetails['stat'] = stat
                        snonMatchingDict[page] = sdetails
                        notmatchedPAges.append(page)
                        snonMatchingDictList.append(snonMatchingDict)
        else:
            print('no template for the Page URL')

        if allMatched:
            matchedPages.append(page)
            #print('all matched ')
        e4 = timeit.default_timer()
        #print('Time to compare page with  function= ' + str(e4 - s4))
    return matchedPages, notmatchedPAges, expiredPages,snonMatchingDictList, str(e4 - s4)
################# analyse ex vs new URL summary #######>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def getTemplateMatchWithExpVsNewPages(templates):
    pageTemplates = []
    for temp in templates:
        for pageT, pageTemplate in temp.items():
            ### Each page or URL can have several templates
            if 'expired' in pageT:
                pageTemplates.append(pageTemplate)
    return pageTemplates
def analyzeMonitoredExpiredPagesWithTemplates(clusterbynamedict, templates,baseFolderName):
    s4 = timeit.default_timer()
    matchedPages = []
    notmatchedPAges = []

    # Get all expired vs new templates from the templates list.
    expvsnewtemplates = getTemplateMatchWithExpVsNewPages(templates)
    # Identify the expired or new page URLs
    expiredPages = {}
    newPages = {}
    for kp, vp in clusterbynamedict.items():
        if vp.__len__() == 1:
            print(vp)
            #check if the page is an expired or a new page
            # expired pages are with _0's and new pages are wth _1's
            if '_0.html' in vp[0]:
                expiredPages[kp] = vp[0]
            if '_1.html' in vp[0]:
                newPages[kp] = vp[0]
    # analyze each new URL with an expired URL

    allMatched = False
    snonMatchingDictList = []
    for npK , npV in newPages.items():
        npHTML = getHTMLcontentAsString([npV], baseFolderName)
        for epK, epV in expiredPages.items():
            epHTML = getHTMLcontentAsString([epV], baseFolderName)
            ### get the summary of exp vs new URLs
            npepDiffSummary, newInsertedTags, movedcontentTags = htmlDiffAnalysis(epHTML[0], npHTML[0])
            ### check if the diff summary match with any previous expired templates
            ## if matched then it is noise if not matched then it is a new page
            for expvsnwtemplate in expvsnewtemplates:
                expvsnwtemplate = ast.literal_eval(json.dumps(expvsnwtemplate))
                if not allMatched:
                    snonMatchingItems, stagSizeofNotMatched, smatchingItems, stagSizeofMatched, allMatched  = compareSameURLMonitoredSummaryWithTemplate(expvsnwtemplate, npepDiffSummary)
                    if not allMatched:
                        stat = []
                        dstat = {}
                        sdetails = {}
                        snonMatchingDict = {}
                        dstat['matchedD'] = stagSizeofMatched
                        dstat['non-matchedD'] = stagSizeofNotMatched
                        sdetails['matched'] = smatchingItems
                        sdetails['non-matched'] = snonMatchingItems
                        sdetails['details'] = dstat
                        stat.append(len(smatchingItems))
                        stat.append(len(snonMatchingItems))
                        stat.append(len(expvsnwtemplate))
                        sdetails['stat'] = stat
                        snonMatchingDict[npK] = sdetails
                        notmatchedPAges.append(npK)
                        snonMatchingDictList.append(snonMatchingDict)

        if allMatched:
            matchedPages.append(npK)
            print('all matched ')

    e4 = timeit.default_timer()
    return matchedPages, notmatchedPAges, expiredPages,snonMatchingDictList, str(e4 - s4)
################################# utils ####################################################
def findStringListInList(llist, tagValues):
    for ll in llist:
        if not type(ll[0]) is str:
            findStringListInList(ll, tagValues)
        elif type(ll[0]) is str:
            tagValues.append(ll)
    return tagValues
################################# analyze results ####################################################
def findTextInResultedTagsOfPageNewInserts(resultedTagValLList, pagecontent):
    textInPage = []
    tagValues = []
    tagValesList = findStringListInList(resultedTagValLList, tagValues)
    for tagVales in tagValesList:
        tag = tagVales[0]
        attrbutes = tagVales[1]
        taggDict = ast.literal_eval(tag)  # str to dict convertion
        tagNamee = taggDict['tag']
        attrbutesDict = ast.literal_eval(attrbutes)  # str to dict convertion
        hasClassat = False
        ################################################
        # for each tag, find if the tag and attri in the html
        allAttrForTagDict = {}
        for att, attv in attrbutesDict.items():
            if att == 'class':
                hasClassat = True
                attv = list(attv)
                actualV = ""
                for av in attv:
                    actualV = actualV + av
                    actualV = actualV + " "
                actualV = actualV.strip()
                allAttrForTagDict[att] = actualV
            else:
                allAttrForTagDict[att] = attv
        if hasClassat:
            results = pagecontent.findAll(tagNamee, allAttrForTagDict ,text=True )
            #############################################################
            allTags = pagecontent.findAll(tagNamee, allAttrForTagDict)
            for all in allTags:
                links = all.findAll('a', recursive=True)
                for lk in links:
                    results.append(lk.get("href"))
            #############################################################
            for r in results:
                if r:
                    if type(r) is not unicode:
                        textt = r.text.encode("utf-8")  ##ast.literal_eval(r.text)
                    else:
                        textt = r
                    if textt:
                        textInPage.append(textt)
    return textInPage
def findTextInResultedTagsOfPagesAlteredContent(nmatchitem,pagecontent):
    textInPage = []
    for tag, values in nmatchitem['non-matched'].items():
        tagg = ast.literal_eval(tag)  # str to dict convertion
        tagName = tagg['tag']
        # tagcontents = pagecontent.findAll(tagName, recursive=True)
        for val in values:
            atrValDict = {}
            hasClassatt = False
            if type(val) is str:
                val = ast.literal_eval(val)  # str to dict convertion
            variableAttNames = []
            for varr in val['variables']:
                variableAttNames.append(varr)
            for atriVal in val['constants']:
                # find a div in the corresponding page with a attriubte and a value as specified in the constants
                att = atriVal.split('=')[0]
                valA = atriVal.split('=')[1]
                atrValDict[att] = valA
                if att == 'class':
                    hasClassatt = True
            if hasClassatt:
                results = pagecontent.findAll(tagName, atrValDict,text=True)
                #############################################################
                allTags = pagecontent.findAll(tagName, atrValDict)
                for all in allTags:
                    links = all.findAll('a', recursive=True)
                    for lk in links:
                        results.append(lk.get("href"))
                #############################################################
                for r in results:
                    if type(r) is not unicode:
                        if r is not None:
                            rtext = r.text.encode("utf-8")  ##ast.literal_eval(r.text)
                            count = 0
                            for varA in variableAttNames:
                                if r.has_attr(varA):
                                    count = count + 1
                            if variableAttNames:
                                if count == len(variableAttNames):
                                    textInPage.append(rtext)
                            else:
                                textInPage.append(rtext)

                    else:
                        textInPage.append(r)

    return textInPage
def findNewTextInPageWithRespectToOldPage(page, results, stringT,baseFolderName):
    page0 = str(page)+ '_0.html'
    page1 = str(page)+ '_1.html'
    pageHtml0 = getHTMLcontentAsString([page0], baseFolderName)
    pageHtml1 = getHTMLcontentAsString([page1], baseFolderName)
    newTextInAfterText = []
    if (pageHtml0 is not None) and (pageHtml1 is not None):
        pagecontent0 = BeautifulSoup(pageHtml0[0], "html.parser")
        pagecontent1 = BeautifulSoup(pageHtml1[0], "html.parser")
        beforeText = []
        afterText = []
        if stringT == 'new_inserts':
            beforeText = findTextInResultedTagsOfPageNewInserts(results, pagecontent0)
            afterText = findTextInResultedTagsOfPageNewInserts(results, pagecontent1)
        if stringT == 'altered_tags':
            beforeText = findTextInResultedTagsOfPagesAlteredContent(results, pagecontent0)
            afterText = findTextInResultedTagsOfPagesAlteredContent(results, pagecontent1)
        # print(beforeText)
        # print(afterText)
        temp = []
        for aT in afterText:
            inBefore = False
            if aT in beforeText:
                if temp.count(aT) < beforeText.count(aT):
                    temp.append(aT)
                    inBefore = True
            if not inBefore:
                newTextInAfterText.append(aT)
    elif pageHtml1 is not None:
        # if page0 not exists when analysizing diff content then just output the page1 results
        pagecontent1 = BeautifulSoup(pageHtml1[0], "html.parser")
        newTextInAfterText = findTextInResultedTagsOfPagesAlteredContent(results, pagecontent1)
    return newTextInAfterText
#########################################################################################################################
#########################################################################################################################
#########################################################################################################################
#########################################################################################################################
#########################################################################################################################
#########################################################################################################################
def analyze(serv):
    global method
    global BASE_FOLDERNAME
    print('analyze... '+ str(serv))
    finalResults = {}

    ### commented due to testing stage ###########################################################
    # for sucesssObj in scollection.find({}):#'action_data':{'action_service': serv}
    #     maxScrapedPagesCount = 0
    #     service_identifier = sucesssObj['action_data']['action_service']
    #     hasMonitored = sucesssObj['monitored']
    #     serviceObjectID = sucesssObj['_id']
    #     if service_identifier != serv:  # for serv in successList2:# //////// critical input!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #         continue
    #######replaced by following###############################################################
    for sucesssObj in authcollection.find({'service_idnetifier':serv}):
        service_identifier = sucesssObj['service_idnetifier']
        domains = sucesssObj['domains']
    ######################################################################
        hasMonitored = True  # CONSTANT SET BY ME
        if hasMonitored:
            print(
                '################## Analyzing Start for the service: ' + service_identifier + " ################################")
            foldername = 'scraped_monitoring/evalscraped_' + service_identifier #for serv in successList2:# //////// critical input!!!!!!!!!!!!!!!!!!!!!!!!!!!
            baseFolderName = './' + foldername + '/'
            BASE_FOLDERNAME = baseFolderName
            pageAnalysisResults = {}
            try:
                htmlfiles = [x for x in os.listdir("./" + foldername) if x.endswith(".html")]
                templates = getTemplates(service_identifier)
                startTime = timeit.default_timer()  ## start time calcuating
                ############################ FOR EACH SERVICE #######################################################
                #####################################################################################################
                ###################### Cluster html filenames based on unique url (FOR CURRENT SERVICE)##############
                clusterbynamedict, crawledTotalForEachCount = getClusterDetails(htmlfiles)
                #####################################################################################################
                ## Process html files ###############################################################################
                #####################################################################################################

                if method == 'textdiff' :
                    st = timeit.default_timer()
                    getTEXTSummary(clusterbynamedict, baseFolderName, serv, resultcollectionByText,domains)
                    et = timeit.default_timer()
                    print('######### update db #############')
                    resultcollectionByText.update({'service_idnetifier': serv}, {'$set': {'time': et-st}})
                elif method == 'htmldiff':
                    st = timeit.default_timer()
                    getSameURLSummary(clusterbynamedict, baseFolderName,serv, resultcollectionByHtml,domains)
                    et = timeit.default_timer()
                    print('######### update db #############')
                    resultcollectionByHtml.update({'service_idnetifier': serv}, {'$set': {'time': et-st}})
                    # ##############################################################################################
                    # endTime = timeit.default_timer()  ## end time calculating
                    # template_generation_time = endTime - startTime
                    # ### commented due to testing stage ###########################################################
                    # # scollection.update({'_id': serviceObjectID},
                    # #                    {'$set': {'comparison_with_template_time': template_generation_time}})
                    # ##############################################################################################
                # **************************************************************************************************
            except OSError:
                continue



    #########################################################################################################################
    #########################################################################################################################
    #########################################################################################################################
    #########################################################################################################################
    # for service, finalRslt in finalResults.items():
    #     print(
    #         '#########################################################################################################################')
    #     print(
    #         '#########################################################################################################################')
    #     print(' RESULTS OF THE SERVICE MONITORING: ' + str(service))
    #     foldername = 'scraped_monitoring/evalscraped_' + service
    #     baseFolderName = './' + foldername + '/'
    #     appletObject = finalRslt['applet']
    #     service_results = {}
    #     ### commented due to testing stage ###########################################################
    #     ##########################################################################################
    #     #service_results['action_service'] = appletObject['action_data']['action_service'].encode('utf-8')
    #     ##########################################################################################
    #     service_results['action_service'] = appletObject
    #     ##########################################################################################
    #     extractedTextUrls = {}
    #     for key, reslts in finalRslt.items():
    #         if key == 'sameURL' or key == 'diffURL':
    #             print('################################## ' + str(key) + ' results ##################################')
    #             print('(1) Fully matched with NOISE TEMPLATES:')
    #             try:
    #                 print(reslts['matched'])
    #             except KeyError:
    #                 print('no matched')
    #             print('(2) NOT Fully matched with NOISE TEMPLATES:')
    #             try:
    #                 print(reslts['nonmathced'])
    #             except KeyError:
    #                 print('no nonmathced')
    #             print('(3) Expired template pages in database:')
    #             try:
    #                 print(reslts['expired'])
    #             except KeyError:
    #                 print('no expired')
    #             print('(4) Non-Matched Content. Possibly new content !!!!')
    #             try:
    #                 print(reslts['nonmatchedlist'])
    #             except KeyError:
    #                 print('no nonmatchedlist')
    #             try:
    #                 newTextOnlyInsetedAll1 = []
    #                 for nmatch in reslts['nonmatchedlist']:
    #                     for page, nmatchitem in nmatch.items():
    #                         newTextOnlyInseted1 = findNewTextInPageWithRespectToOldPage(page, nmatchitem,
    #                                                                                     'altered_tags',
    #                                                                                     baseFolderName)
    #                         if newTextOnlyInseted1.__len__() > 0:
    #                             newTextOnlyInsetedAll1.append(list(set(newTextOnlyInseted1)))
    #                         for nT in list(set(newTextOnlyInseted1)):
    #                             print(nT)
    #                 extractedTextUrls[key] = newTextOnlyInsetedAll1
    #                 print('(4) Time: ' + str(reslts['time']))
    #             except KeyError:
    #                 print('')
    #         if key == 'totally_new':
    #             print('###################### Totally New Insertions In the Pages ##################################')
    #             newTextOnlyInsetedAll2 = []
    #             for ki, iv in reslts.items():
    #                 newTextOnlyInseted2 = findNewTextInPageWithRespectToOldPage(ki, iv, 'new_inserts', baseFolderName)
    #                 if newTextOnlyInseted2.__len__() > 0:
    #                     newTextOnlyInsetedAll2.append(list(set(newTextOnlyInseted2)))
    #                 for nT in list(set(newTextOnlyInseted2)):
    #                     print(nT)
    #             extractedTextUrls[key] = newTextOnlyInsetedAll2
    #     service_results['results'] = extractedTextUrls
    #     print(extractedTextUrls)
        ### commented due to testing stage ###########################################################
        # scollection.update({'_id': appletObject['_id']}, {'$set': {'action_data': service_results}})
        # for app in appletcollection.find({'applet_id': appletObject['applet_id']}):
        #     scollection.update({'_id': appletObject['_id']}, {'$set': {'applet_knowledge': app}})


############# for after monitoring get the successful service #################
db3 = client['evalapplets']
scollect3 =  db3.get_collection(applet_folder_name)
db2 = client[applet_folder_name]
scollect =  db2.get_collection('succeed')
successappletlist = []
for sc in scollect.find({}):
    successappletlist.append(sc['applet_id'])
successactionservicelist = []
for sc3 in scollect3.find({}):
    if sc3['applet_id'] in successappletlist:
        successactionservicelist.append(sc3['action_service'])
print(successactionservicelist)
print(len(successactionservicelist))

current_services = ['bitly','facebook','google_contacts','instapaper','slack', 'date_and_time','maker_webhooks','twitter','youtube','wordpress','withings','weebly',
               'toodledo','todoist','tesco','strava','medium','musixmatch','pocket','reddit','google_docs','google_drive',
               'google_sheets','instagram','fitbit','flickr','gmail', 'email','google_calendar','blogger','dropbox','diigo','evernote',
                'ios_health', 'if_notifications','android_device', 'location','do_button', 'android_phone','android_messages', 'voip_calls','line', 'do_camera',
                'ios_photos', 'ios_reading_list','foursquare', 'android_battery','android_photos', 'qualitytime','ios_reminders', 'ios_contacts','do_note']

all_successList = ['bitly','facebook','google_contacts','instapaper','slack','twitter','youtube','wordpress','withings','weebly',
               'toodledo','todoist','tesco','strava','medium','musixmatch','pocket','reddit','google_docs','google_drive',
               'google_sheets','instagram','fitbit','flickr','gmail','google_calendar','blogger','dropbox','diigo','evernote']
#method = 'textdiff'
#method = 'htmldiff'
method = 'textdiff'
print('start here')
s1 = timeit.default_timer()
threads = []
nonCrawledServices = [] ####'strava'

##################################################################################
remaining = ['twitter', 'toodledo', 'reddit', 'slack', 'instagram','bitly']
x =['ios_photos', 'android_device', 'if_notifications', 'voip_calls', 'instapaper', 'toodledo', 'reddit', 'google_docs', 'flickr', 'fitbit', 'ios_health', 'blogger', 'slack', 'google_drive', 'ios_reading_list', 'twitter', 'google_sheets', 'ios_reminders', 'wordpress', 'pocket', 'dropbox', 'line', 'todoist', 'diigo', 'android_messages']
##############################################################
###############################################################
###### IMPORTANT: require to change the 'method' to text or html
##############################################################
###############################################################
for serv in current_services:#x + remaining:
    analyze(serv)
##############################################################
###############################################################
e1 = timeit.default_timer()
print('Time for analysis function= ' + str(e1 - s1))
########################################## once finished revert changes to folder
if os.path.isdir(alterend_directory_name):
    print('directory exists. so revert it!')
    os.rename(alterend_directory_name, directory_name)
##########################################