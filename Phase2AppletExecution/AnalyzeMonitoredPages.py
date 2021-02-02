# !/usr/bin/python2.7
from htmltreediff import diff
from bs4 import BeautifulSoup
import os
import json
from pymongo import MongoClient
import timeit
from bson import json_util
import ast
import hashlib
import base64
import timeit
from threading import Thread
from multiprocessing.pool import ThreadPool
import time
from lxml import etree, html
#install html5lib
import pprint
# mongoexport --collection=appletcollection --db=applets --out=successmonitoring.json --pretty
# mongo --quiet services --eval 'printjson(db.authdetails.find({'connected':true}))'> output.json
########################################################################################################################
############################################## DATABASE CONNECTION #####################################################
uri = 'mongodb://127.0.0.1:27017'
client = MongoClient(uri)
tempDB = client.get_database('ntemplates')# previously actionmonitor
authDB= client.get_database('services')
authcollection = authDB.get_collection('authdetails')
###############################################
db = client['iftttmonitor4']
scollection = db.get_collection('succeed')
fcollection = db.get_collection('failed')
###############################################
###############################################
appletDB = client['applets']
appletcollection = appletDB.get_collection('appletcollection4')
###############################################
########################################################################################################################
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
### alteration is defined as ====> specifiy deleted or removed tags in the new page
def analyzeDeletedAndInsertedContent(deleted,inserted):
    print('Begin  analyzeDeletedAndInsertedContent()---->')
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
                    if (insItemSet.__len__() == delItemsSet.__len__() and isDeletedItemEqualInserted(delItemsSet,
                                                                                                     insItemSet)):
                        # print('is an deleted item = hence may be altered')
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
    alteredTags, newInsertedTags = analyzeDeletedAndInsertedContent(deleted, inserted)
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
    htmlfileContentsasStrings = []
    for fname in v:
        try:
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

        # assuming one html page includes
        if updatedhtml:
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
        alteredTagsOfTotalDeletedOrInsertedPages, newInsertedTags = htmlDiffAnalysis(basePageHtmlString[0], htmlS)
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
    return summary,insertedSum,singleOccurenceKeys
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

        # get the template/templates available under the page URL key
        templateOrtemplates = getTemplateMatchWithPage(tempList, page)
        if type(templateOrtemplates) is list:
            #print('several templates for the page URL')
            for template in templateOrtemplates:
                template = ast.literal_eval(json.dumps(template))
                if not allMatched:
                    snonMatchingItems, stagSizeofNotMatched, smatchingItems, stagSizeofMatched, allMatched = compareSameURLMonitoredSummaryWithTemplate(
                        template, pageSum)
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
            npepDiffSummary, newInsertedTags = htmlDiffAnalysis(epHTML[0], npHTML[0])
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
    exceList = ['strava', 'ios_photos', 'telegram', 'sms', 'sms', 'ios_calendar', 'ios_calendar']
    finalResults = {}
    if serv in exceList:
        return
    for sucesssObj in scollection.find({}):#'action_data':{'action_service': serv}
        maxScrapedPagesCount = 0
        service_identifier = sucesssObj['action_data']['action_service']
        hasMonitored = sucesssObj['monitored']
        serviceObjectID = sucesssObj['_id']
        if service_identifier != serv:  # for serv in successList2:# //////// critical input!!!!!!!!!!!!!!!!!!!!!!!!!!!
            continue
        # if service_identifier == 'flickr':
        #     continue
        # if (service_identifier != 'pocket'):#  and (service_identifier != 'google_sheets') and (service_identifier != 'google_calendar'):
        #     continue
        hasMonitored = True  # CONSTANT SET BY ME
        print(hasMonitored)
        if hasMonitored:
            print(
                '################## Analyzing Start for the service: ' + service_identifier + " ################################")
            foldername = 'scraped_monitoring/scraped_' + service_identifier #for serv in successList2:# //////// critical input!!!!!!!!!!!!!!!!!!!!!!!!!!!
            baseFolderName = './' + foldername + '/'
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
                summary, insertedSum, singleOccurenceKeys = getSameURLSummary(clusterbynamedict, baseFolderName)
                # ****************************************************************************************************
                print(
                    '###################### Same URL (Pre-Post) Noise Analysis ##################################')
                rpmatchedPages = None
                rpnotmatchedPAges = None
                rpexpiredPages = None
                rpsnonMatchingDictList = None
                timeforrepeated = None
                sameURLResults = {}
                diffURLResults = {}
                if len(summary) > 0:
                    rpmatchedPages, rpnotmatchedPAges, rpexpiredPages, rpsnonMatchingDictList, timeforrepeated = analyzeMonitoredSummaryWithTemplate(
                        templates, summary)
                    sameURLResults['matched'] = rpmatchedPages
                    sameURLResults['nonmathced'] = rpnotmatchedPAges
                    sameURLResults['expired'] = rpexpiredPages
                    sameURLResults['nonmatchedlist'] = rpsnonMatchingDictList
                    sameURLResults['time'] = timeforrepeated

                # ****************************************************************************************************
                print('###################### Expired VS New URL Noise Analysis ##################################')
                nematchedPages, nenotmatchedPAges, neexpiredPages, nesnonMatchingDictList, timefornewvsexp = analyzeMonitoredExpiredPagesWithTemplates(
                    clusterbynamedict, templates, baseFolderName)
                #########################################################################################
                endTime = timeit.default_timer()  ## end time calculating
                template_generation_time = endTime - startTime
                scollection.update({'_id': serviceObjectID},
                                   {'$set': {'comparison_with_template_time': template_generation_time}})
                #########################################################################################
                diffURLResults['matched'] = nematchedPages
                diffURLResults['nonmathced'] = nenotmatchedPAges
                diffURLResults['expired'] = neexpiredPages
                diffURLResults['nonmatchedlist'] = nesnonMatchingDictList
                diffURLResults['time'] = timefornewvsexp

                pageAnalysisResults['totally_new'] = insertedSum
                pageAnalysisResults['sameURL'] = sameURLResults
                pageAnalysisResults['diffURL'] = diffURLResults
                pageAnalysisResults['applet'] = sucesssObj
                finalResults[service_identifier] = pageAnalysisResults
                # ****************************************************************************************************
            except OSError:
                continue



    #########################################################################################################################
    #########################################################################################################################
    #########################################################################################################################
    #########################################################################################################################
    for service, finalRslt in finalResults.items():
        print(
            '#########################################################################################################################')
        print(
            '#########################################################################################################################')
        print(' RESULTS OF THE SERVICE MONITORING: ' + str(service))
        foldername = 'scraped_monitoring/scraped_' + service
        baseFolderName = './' + foldername + '/'
        appletObject = finalRslt['applet']
        service_results = {}
        service_results['action_service'] = appletObject['action_data']['action_service'].encode('utf-8')
        extractedTextUrls = {}
        for key, reslts in finalRslt.items():
            if key == 'sameURL' or key == 'diffURL':
                print('################################## ' + str(key) + ' results ##################################')
                print('(1) Fully matched with NOISE TEMPLATES:')
                try:
                    print(reslts['matched'])
                except KeyError:
                    print('no matched')
                print('(2) NOT Fully matched with NOISE TEMPLATES:')
                try:
                    print(reslts['nonmathced'])
                except KeyError:
                    print('no nonmathced')
                print('(3) Expired template pages in database:')
                try:
                    print(reslts['expired'])
                except KeyError:
                    print('no expired')
                print('(4) Non-Matched Content. Possibly new content !!!!')
                try:
                    print(reslts['nonmatchedlist'])
                except KeyError:
                    print('no nonmatchedlist')
                try:
                    newTextOnlyInsetedAll1 = []
                    for nmatch in reslts['nonmatchedlist']:
                        for page, nmatchitem in nmatch.items():
                            newTextOnlyInseted1 = findNewTextInPageWithRespectToOldPage(page, nmatchitem,
                                                                                        'altered_tags',
                                                                                        baseFolderName)
                            if newTextOnlyInseted1.__len__() > 0:
                                newTextOnlyInsetedAll1.append(list(set(newTextOnlyInseted1)))
                            for nT in list(set(newTextOnlyInseted1)):
                                print(nT)
                    extractedTextUrls[key] = newTextOnlyInsetedAll1
                    print('(4) Time: ' + str(reslts['time']))
                except KeyError:
                    print('')
            if key == 'totally_new':
                print('###################### Totally New Insertions In the Pages ##################################')
                newTextOnlyInsetedAll2 = []
                for ki, iv in reslts.items():
                    newTextOnlyInseted2 = findNewTextInPageWithRespectToOldPage(ki, iv, 'new_inserts', baseFolderName)
                    if newTextOnlyInseted2.__len__() > 0:
                        newTextOnlyInsetedAll2.append(list(set(newTextOnlyInseted2)))
                    for nT in list(set(newTextOnlyInseted2)):
                        print(nT)
                extractedTextUrls[key] = newTextOnlyInsetedAll2
        service_results['results'] = extractedTextUrls
        scollection.update({'_id': appletObject['_id']}, {'$set': {'action_data': service_results}})
        for app in appletcollection.find({'applet_id': appletObject['applet_id']}):
            scollection.update({'_id': appletObject['_id']}, {'$set': {'applet_knowledge': app}})

## sucess list get from IFTTTfeed script

successList = ['blogger', 'diigo', 'narro', 'pocket', 'google_calendar', 'office_365_calendar', 'amazonclouddrive', 'google_docs', 'google_drive', 'google_sheets', 'cisco_spark', 'telegram', 'google_contacts', 'office_365_contacts', 'github', 'particle', 'email', 'office_365_mail', 'fitbit', 'strava', 'android_device', 'ios_calendar', 'deezer', 'musixmatch', 'spotify', 'evernote', 'sms', 'flickr', 'ios_photos', 'stockimo', 'reddit', 'twitter', 'todoist', 'toodledo']
successList = list(set(successList))

print('start here')
s1 = timeit.default_timer()
threads = []
nonCrawledServices = [] ####'strava'
# for serv in successList:  # //////// critical input!!!!!!!!!!!!!!!!!!!!!!!!!!!
#     #analyze(exceList, serv)
#     # with the thread
#     process = Thread(target=analyze, args=[exceList, serv])
#     process.start()
#     threads.append(process)
#
# # with the thread
# for process in threads:
#     process.join()
# #################
# e1 = timeit.default_timer()
# print('Time for analysis function= ' + str(e1 - s1))
##################################################################################
pools = ThreadPool(processes=successList.__len__())
work_args = []
for serv in successList:  # //////// critical input!!!!!!!!!!!!!!!!!!!!!!!!!!!
    work_args.append(serv)
print(work_args)
pools.map(analyze, work_args)

e1 = timeit.default_timer()
print('Time for analysis function= ' + str(e1 - s1))