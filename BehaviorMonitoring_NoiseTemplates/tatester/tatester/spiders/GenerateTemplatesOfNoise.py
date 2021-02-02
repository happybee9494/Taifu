# !/usr/bin/python2.7
from htmltreediff import diff
from bs4 import BeautifulSoup
import os
import json
from pymongo import MongoClient
import timeit
import itertools
from bson import json_util
import ast
from threading import Thread
import time
import pprint
#from pathlib import Path
#install html5lib
import sys
########################################################################################################################
############################################## DATABASE CONNECTION #####################################################
uri = 'mongodb://127.0.0.1:27017'
client = MongoClient(uri)
# db = client['actionmonitor']
#client = MongoClient('mongodb+srv://ifttt:ifttt@cluster0-b5sb3.mongodb.net/test?retryWrites=true&w=majority')
tempDB = client.get_database('ntemplates')
authDB= client.get_database('services')
authcollection = authDB.get_collection('authdetails')
########################################################################################################################
############################################## SERVICE RELATED SETTINGS ################################################
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
                    if x == xx:
                        counterC = counterC +1
                        break
        if counterV == dictOld.items()[0][1].__len__() and counterC == dictOld.items()[1][1].__len__():
            return 1
def compareUs(x , y, b):
    if isinstance(x, str):
        x = json.loads(x)
        y = json.loads(y)
        #### Required in Python 2.7
        if isinstance(y,unicode):
            y = json.loads(y)
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
    ####### Check whether, a new (variable/constant dict) is in the full dict list of old
    ####### if it is in then return 1 else return 0
    if isinstance(listOld, dict):
        #x = [json.dumps(listOld)]
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
    if summDict1 and summDict2:
        if summDict1.items() != summDict2.items():
            return 0
        if summDict1.items() == summDict2.items():
            for sd1, sd1v in summDict1.items():
                for sd2, sd2v in summDict2.items():
                    if sd1 == sd2:
                        for sd2vitem in sd2v:
                            sd2item = [sd2vitem]
                            if compare(sd1v, sd2item, True) == 0:
                                return 0

        return 1

######################################################>>>>>>>>>>>>>>>>>>>>
def getSimilarItemsFromTwoDict(summDict1, summDict2):
    ## only check if the item size is equal to procceeed withs
    if len(summDict1) == len(summDict2):
        returnFilteredSumDict = {}
        for sd1, sd1v in summDict1.items():
            for sd2, sd2v in summDict2.items():
                if sd1 == sd2:
                    updatedsd2v = sd2v
                    for sd2vitem in sd2v:
                        sd2itemX = [sd2vitem]
                        ### check if an item in the new dict is in the old dict
                        if compare(sd1v, sd2itemX, True) == 0:
                            # if not in the list => should remove  sd2item from the new list
                            updatedsd2v.remove(sd2vitem)
                    ### add the checked item list to the return dictionary
                    returnFilteredSumDict[sd2] = updatedsd2v
        return returnFilteredSumDict
######################################################################>>>>>>
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
def findConstantsAndVariables(delContJson,insContJson):
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
                                clsN = clsN + cn
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
def analyzeDeletedAndInsertedContent(deleted,inserted):
    print('Begin  analyzeDeletedAndInsertedContent()---->')
    alteredTags = {}
    for delItemsSet in deleted:
        for insItemSet in inserted:
            if (insItemSet.__len__() == delItemsSet.__len__() or isDeletedItemEqualInserted(delItemsSet ,insItemSet)):
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
                            constants, variables = findConstantsAndVariables(delContJson, insContJson)
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

    print('End  analyzeDeletedAndInsertedContent()---->')
    return alteredTags
def analyzeDeletedAndInsertedContentB(deleted,inserted):
    print('Begin  analyzeDeletedAndInsertedContent()---->')
    alteredTags = {}
    newInsertedTags = []
    for insItemSet in inserted:
        countMatched = 0
        for delItemsSet in deleted:
            if (insItemSet.__len__() == delItemsSet.__len__() or isDeletedItemEqualInserted(delItemsSet ,insItemSet)):
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
                            constants, variables = findConstantsAndVariables(delContJson, insContJson)
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
                newInsertedTags.append(insItemSet)

    print('End  analyzeDeletedAndInsertedContent()---->')
    return alteredTags,newInsertedTags
def htmlDiffAnalysis(x,y):
    print('BEGIN HTML tree analysis ---->')
    s1 = timeit.default_timer()
    htmlAdjcentDiffResult = diff(x,y, pretty=False)
    e1 = timeit.default_timer()
    print('Time for diff library function= '+ str(e1-s1))
    ############################################################################
    ########### Extract deleted and inserted content for each occurence of url##
    htmlAdjacentDiffContent = BeautifulSoup(htmlAdjcentDiffResult, "html.parser")
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
    alteredTags, newInsertedTags = analyzeDeletedAndInsertedContentB(deleted, inserted)
    e3 = timeit.default_timer()
    print('Time analyzeDeletedAndInsertedContent function= ' + str(e3 - s3))
    print('Time htmlDiffAnalysis function= ' + str(e3 - s1))
    print('END HTML tree analysis ---->')
    return alteredTags, newInsertedTags
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
        returnUpdatedList.append(hclString)
    return returnUpdatedList
def getHTMLcontentAsString(v,baseFolderName):
    print(v)
    htmlfileContentsasStrings = []
    for fname in v:
        filepath = baseFolderName+ fname
        f = open(filepath, "r")
        fileContent = f.read()  # .decode('utf-8')
        f.close()

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

        # assuming one html page includes
        if updatedhtml:
            htmlfileContentsasStrings.append(updatedhtml[0])

    return htmlfileContentsasStrings
############################## EXPIRED URLS ##################>>>>>>>>>>>>>>>>>>>>
def getClusterDetails(htmlfiles):
    # find if each URL has crawled 5 times
    clusterbynamedict = {}
    crawledTotalForEachCount = {}# stores crawled no as key
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
def getTemplateMatchWithExpVsNewPages(service_name):
    templates = []
    collection = tempDB.get_collection('templates_' + str(service_name))
    for template in collection.find({}):
        templates.append(json.loads(json.dumps(template, indent=4, default=json_util.default)))
    pageTemplates = []
    for temp in templates:
        for pageT, pageTemplate in temp.items():
            ### Each page or URL can have several templates
            if 'expired' in pageT:
                pageTemplates.append(pageTemplate)
    return pageTemplates
def analyzeTotallyDeleteOrInserted(clusterbynamedict,collection,baseFolderName,service_name):
    ######## Base pages include the single pages of the first/min crawl number #######################
    # get existing expired templates
    expvsnewtemplates = getTemplateMatchWithExpVsNewPages(service_name)
    # randomly select the baseDeltePageKey for now
    crawledCountForEachRound = {k: [] for k in '01234'}
    i = 0
    for kp, vp in clusterbynamedict.items():
        ############# identify how many singles at each crawled round #############
        if vp.__len__() < 4:
            roundNo = vp[0].split('.')[0].split('_')[1]
            crawledCountForEachRound[roundNo] = crawledCountForEachRound[roundNo] + vp

    ##################################################################################################
    ############ Open html files and extract only html conntent as a string ##########################
    kmap = {}
    diffURLdict = {}
    counter = 0
    selectedPages = {} # for each round, from the crawledCountForEachRound
    for ck, cv in crawledCountForEachRound.items():
        htmlfileContentsasStrings = getHTMLcontentAsString(cv, baseFolderName)
        if ck != '0':
            for htmlS in htmlfileContentsasStrings:
                if crawledCountForEachRound[str(int(ck) - 1)]:
                    ########## Get the first expired page from the previous crawling #####################
                    firstPageOfCountck = list(crawledCountForEachRound[str(int(ck) - 1)])[0]
                    ########## Get html content as a string ##############################################
                    baseExpiredPage = getHTMLcontentAsString([firstPageOfCountck], baseFolderName)
                    ########## GEt the html tree diff of the pages from consecutive crawing ##############
                    ## need to check agaain
                    if len(baseExpiredPage) > 0:
                        alteredTagsOfTotalDeletedOrInsertedPages, newInsertedTags = htmlDiffAnalysis(baseExpiredPage[0],
                                                                                                     htmlS)
                        counter = counter + 1
                        kmap[counter] = [ck, str(int(ck) - 1)]
                        selectedPages[counter] = [firstPageOfCountck, cv[0]]
                        diffURLdict[counter] = alteredTagsOfTotalDeletedOrInsertedPages



    diffKeyCouples = list(itertools.combinations(diffURLdict.keys(), 2))
    equalCouples = []
    nonEqualCouples = []
    for couple in diffKeyCouples:
        key1= couple[0]
        key2 = couple[1]
        if compareSummaryDict(diffURLdict[key1], diffURLdict[key2]) == 0:
            nonEqualCouples.append(couple)
        else:
            equalCouples.append(couple)

    ###########################################################################################
    ############################### Summarize the template comaprison #########################
    # print(kmap)
    # print(selectedPages)
    # summarize the equals
    # If the templates of the pairs equal store one template in the DB, else add each non-equal
    eqalSummary = []
    noneqalSummary = []
    if equalCouples:
        eqalSummary = [equalCouples[0][0], equalCouples[0][1]]  # initialize
        for pair in equalCouples:
            if pair[0] in eqalSummary or pair[1] in eqalSummary:
                eqalSummary.append(pair[0])
                eqalSummary.append(pair[1])
    eqalSummary = list(set(eqalSummary))
    if nonEqualCouples:
        noneqalSummary = [nonEqualCouples[0][0], nonEqualCouples[0][1]]  # initialize
        for pair in nonEqualCouples:
            if pair[0] in noneqalSummary or pair[1] in noneqalSummary:
                noneqalSummary.append(pair[0])
                noneqalSummary.append(pair[1])
    noneqalSummary = list(set(noneqalSummary))
    uniqueNonEqualTemplatesIndex = []
    if noneqalSummary:
        for neqs in noneqalSummary:
            if not neqs in eqalSummary:
                uniqueNonEqualTemplatesIndex.append(neqs)


    ###########################################################################################
    ############################### UPDATE DB #################################################
    if eqalSummary:
        if eqalSummary[0]:
            if diffURLdict[eqalSummary[0]]:
                pageData = {}
                pageData['expiredPageTemplateFromEquals'] = diffURLdict[eqalSummary[0]]
                collection.update(pageData, pageData, upsert=True)
                print('SUMMARY EXPIRED EQUAL TEMPLATE SUCCESSFULL: ' + str(selectedPages[eqalSummary[0]]))
    if uniqueNonEqualTemplatesIndex:
        i = 0
        for uexptemp in uniqueNonEqualTemplatesIndex:
            if diffURLdict[uexptemp]:
                for expvsnwtemplate in expvsnewtemplates:
                    expvsnwtemplate = ast.literal_eval(json.dumps(expvsnwtemplate))
                    result = compare(expvsnwtemplate, diffURLdict[eqalSummary[0]], False)
                    if result != 1:
                        pageData = {}
                        pageData['expiredPageTemplateFromNonEquals' + str(i)] = diffURLdict[eqalSummary[0]]
                        collection.update(pageData, pageData, upsert=True)
                        print('SUMMARY EXPIRED NON-EQUAL TEMPLATE SUCCESSFULL: ' + str(selectedPages[uexptemp]))
                        i = i + 1


############################# SAME URL #####################>>>>>>>>>>>>>>>>>>>>
def getSameURLSummary(clusterbynamedict,baseFolderName):
    singleOccurenceKeys = []
    summary = {}
    insertedSum = {}
    for k, v in clusterbynamedict.items():  # k - unique url, v- scraped pages of k url
        print('################# new URL start ....####################################### ' + k)
        if len(v) == 1:  ## If page occured only onces => Reaonse: expired, not crawled
            singleOccurenceKeys.append(k)
            continue
        ###################################################################################################
        ############# Open html files and extract only html conntent as a string ##########################
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
                    alteredTags,newInsertedTags = htmlDiffAnalysis(htmlfileContentsasStrings[i - 1], htmlfileContentsasStrings[i])
                    sameURL.append(alteredTags)
                    if newInsertedTags:
                        sameURLInsert.append(newInsertedTags)
                    print('######################## A page of ' + str(
                        k) + ' done analysis >_< ##################################')
            summary[k] = sameURL
            if sameURLInsert:
                insertedSum[k] = sameURLInsert
            print('################# ' + str(
                k) + ' ############################### ' + ' DONE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

        # TODO: delete only or insert only
    return summary,insertedSum, singleOccurenceKeys
def repeaPageGetSameSizeSummaryLists(pageSummary):
    # even a same URL repeats, it is possible that different contetn loads
    # hence identify possible different clusters for the same URL
    dictSummaryBySize = {}
    for summaryDict in pageSummary:
       try:
           dictSummaryBySize[len(summaryDict)].append(summaryDict)
       except KeyError:
           dictSummaryBySize[len(summaryDict)] = [summaryDict]
    return dictSummaryBySize
def analyzeReatedPageInsertions(insertedSum):
    print('TODO: IF necessary')
    ## currently seems no major insertions happens when no actions there
    ##
    # for page, inSummary in insertedSum.items():
    #     print(page)
    #     if inSummary.__len__() > 0:
    #         ### Find possible clusters of the same page crawlings
    #         print(inSummary)
    #         pageInSummaryClusters = repeaPageGetSameSizeSummaryLists(inSummary)
    #         ### Find smmary similarities to find the templates
    #         for ckey, sumCluster in pageInSummaryClusters.items():
    #             print(sumCluster)
    #             if sumCluster.__len__() > 1:
    #                 baseDictionary = sumCluster[0]
    #                 counterS = 0
    #                 intc = 0
    #                 for summaryDict in sumCluster:
    #                     intc = intc + 1 # to avoid the basdict compare with basedict
    #                     if intc != 1:
    #                         if compareSummaryDict(baseDictionary, summaryDict) != 0:
    #                             print('same')
    #                             counterS = counterS + 1
    #                         else:
    #                             #### get common elements in the two dictionaries as the template
    #                             commonDict = getSimilarItemsFromTwoDict(baseDictionary, summaryDict)
    #                             pageData = {}
    #                             pageData[page] = commonDict
    #                             tempcollection.update(pageData, pageData, upsert=True)
    #                             print('SUMMARY INSERT ONLY SUCCESSFULL: ' + str(page))
    #
    #                 if counterS == (sumCluster.__len__()-1): ## since remove (0,0) case
    #                     pageData = {}
    #                     pageData[page] = baseDictionary
    #                     tempcollection.update(pageData, pageData, upsert=True)
    #                     print('SUMMARY INSERT ONLY SUCCESSFULL: ' + str(page))
    #             else:
    #                 pageData = {}
    #                 pageData[page] = baseDictionary
    #                 tempcollection.update(pageData, pageData, upsert=True)
    #                 # tempcollection.insert_one(pageData)  ##########json.dump(x, sys.stdout)
    #                 print('SUMMARY INSERT ONLY SUCCESSFULL: ' + str(page))
def analyzeRepeatedPages(summary,insertedSum,tempcollection):
    if insertedSum:
        analyzeReatedPageInsertions(insertedSum)
    ##### normal analysis
    for page, pageSummary in summary.items():
        print(page)
        if pageSummary.__len__() > 0:
            ### Find possible clusters of the same page crawlings
            pageSummaryClusters = repeaPageGetSameSizeSummaryLists(pageSummary)
            ### Find smmary similarities to find the templates
            for ckey, sumCluster in pageSummaryClusters.items():
                print(sumCluster.__len__())
                if sumCluster.__len__() > 1:
                    baseDictionary = sumCluster[0]
                    counterS = 0
                    intc = 0
                    for summaryDict in sumCluster:
                        intc = intc + 1 # to avoid the basdict compare with basedict
                        if intc != 1:
                            if compareSummaryDict(baseDictionary, summaryDict) != 0:
                                counterS = counterS + 1
                            else:
                                #### get common elements in the two dictionaries as the template
                                commonDict = getSimilarItemsFromTwoDict(baseDictionary, summaryDict)
                                pageData = {}
                                pageData[page] = commonDict
                                tempcollection.update(pageData, pageData, upsert=True)
                                print('SUMMARY SUCCESSFULL: ' + str(page))

                    if counterS == (sumCluster.__len__()-1): ## since remove (0,0) case
                        pageData = {}
                        pageData[page] = baseDictionary
                        tempcollection.update(pageData, pageData, upsert=True)
                        print('SUMMARY SUCCESSFULL: ' + str(page))
                # else:
                #     pageData = {}
                #     pageData[page] = baseDictionary
                #     tempcollection.update(pageData, pageData, upsert=True)
                #     # tempcollection.insert_one(pageData)  ##########json.dump(x, sys.stdout)
                #     print('SUMMARY SUCCESSFULL: ' + str(page))
######################################################>>>>>>>>>>>>>>>>>>>>
#########################################################################################################################
#########################################################################################################################
#########################################################################################################################
def generateNoiseTemplatesForTheService(service_identifier,serviceObjectID,x,tempDB,authcollection):
    print(
        '################## Analyzing Start for the service: ' + service_identifier + " ################################")
    foldername = 'scraped/scraped_' + service_identifier
    baseFolderName = './' + foldername + '/'
    try:
        htmlfiles = [x for x in os.listdir("./" + foldername) if x.endswith(".html")]
        ############################ FOR EACH SERVICE #######################################################
        #####################################################################################################
        ###################### Cluster html filenames based on unique url (FOR CURRENT SERVICE)##############
        clusterbynamedict, crawledTotalForEachCount = getClusterDetails(htmlfiles)
        if len(crawledTotalForEachCount) < 5:
            return
        tempcollection = tempDB.get_collection('templates_' + service_identifier)
        startTime = timeit.default_timer()  ## start time calcuating
        #####################################################################################################
        ## Process html files ###############################################################################
        #####################################################################################################
        summary, insertedSum, singleOccurenceKeys = getSameURLSummary(clusterbynamedict, baseFolderName)
        # TODO: Currently, the newly inserted summary is not
        #####################################################################################################
        ################################## Analyze same URL summary #########################################
        if len(summary) > 0:
            analyzeRepeatedPages(summary, insertedSum, tempcollection)
        print('################################## END SAME URL ###############################################')
        ######################################################################################################
        ################################## Find and  Analyze expired URL  summary ############################
        analyzeTotallyDeleteOrInserted(clusterbynamedict, tempcollection, baseFolderName, service_identifier)
        endTime = timeit.default_timer()  ## end time calculating
        template_generation_time = endTime - startTime
        authcollection.update({'_id': serviceObjectID},
                              {'$set': {'template_generation_time': template_generation_time}})
        print('####################################  END EXPIRED URLS ########################################')
    except OSError:
        return
nonCrawledServices = []
servicelist = [ 'narro', 'diigo', 'twitter','office_365_contacts','office_365_mail','google_docs', 'dropbox', 'pocket','musixmatch','evernote','strava', 'wordpress','spotify','cisco_spark','deezer','email','google_calendar', 'amazonclouddrive', 'google_sheets', 'google_drive', 'google_contacts', 'particle','github', 'fitbit', 'flickr', 'beeminder',  'reddit', 'todoist']
newlist = ['office_365_contacts','github']
threads = []
for service in servicelist: ##///////////critical
    for x in authcollection.find({'service_idnetifier': service}):
        maxScrapedPagesCount = 0
        service_identifier = x['service_idnetifier']
        # if service_identifier != 'pocket':
        #     continue
        isConnected = x['connected']
        serviceObjectID = x['_id']
        if isConnected:
            process = Thread(target=generateNoiseTemplatesForTheService,
                             args=[service_identifier, serviceObjectID, x, tempDB, authcollection])
            process.start()
            threads.append(process)

for process in threads:
    process.join()











