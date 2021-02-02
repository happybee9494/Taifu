# !/usr/bin/python2.7
from htmltreediff import diff
from bs4 import BeautifulSoup
import os
import json
from pymongo import MongoClient
import timeit
from bson import json_util
import ast
from lxml import etree, html
#install html5lib
import pprint
########################################################################################################################
############################################## DATABASE CONNECTION #####################################################
uri = 'mongodb://127.0.0.1:27017'
client = MongoClient(uri)
tempDB = client.get_database('actionmonitor')
authDB= client.get_database('services')
authcollection = authDB.get_collection('authdetails')
########################################################################################################################
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
        x = [json.dumps(listOld)]
        return compareUs(x[0], listNew[0],b)

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
    alteredTags = {}
    newInsertedTags = []
    for insItemSet in inserted:
        countMatched = 0
        for delItemsSet in deleted:
            if (insItemSet.__len__() == delItemsSet.__len__() and isDeletedItemEqualInserted(delItemsSet ,insItemSet)):
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
                            constants, variables = findConstantsAndVariablesInTermsOfDeletionsInNewPage(delContJson, insContJson)
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
        x = [json.dumps(listOld)]
        return compareUsB(x[0], listNew[0],b)

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
        for tempTag, tempValue in template.items():
            if tag == tempTag:
                # print('matching Tag')
                result = compareB(tempValue, values, False)
                if result !=1:
                    print(result)
                    # print('atleast on instance not equal')
                    tempsnonMatchingItems[tag] = result #values
                    tempstagSizeofNotMatched[tag] = result.__len__() #values.__len__()
                else:
                    # print('matching with old ')
                    tagSuCounter = tagSuCounter + 1
                    tempsmatchingItems[tag] = values
                    tempstagSizeofMatched[tag] = values.__len__()
    if tagSuCounter == len(template):
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
            print('several templates for the page URL')
            for template in templateOrtemplates:
                template = ast.literal_eval(json.dumps(template))
                print(template)
                print(len(template))
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
            print('all matched ')
        e4 = timeit.default_timer()
        print('Time to compare page with  function= ' + str(e4 - s4))
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
#########################################################################################################################
#########################################################################################################################
#########################################################################################################################
#########################################################################################################################
#########################################################################################################################
#########################################################################################################################
nonCrawledServices = []
for x in authcollection.find({}):
    maxScrapedPagesCount = 0
    service_identifier = x['service_idnetifier']
    isConnected = x['connected']
    if service_identifier != 'google_docs':
        continue
    if isConnected:
        print('################## Analyzing Start for the service: '+ service_identifier + " ################################")
        foldername = 'scraped_monitoring/scraped_' + service_identifier
        baseFolderName = './' + foldername + '/'
        try:
            htmlfiles = [x for x in os.listdir("./" + foldername) if x.endswith(".html")]
            templates = getTemplates(service_identifier)
            ############################ FOR EACH SERVICE #######################################################
            #####################################################################################################
            ###################### Cluster html filenames based on unique url (FOR CURRENT SERVICE)##############
            clusterbynamedict, crawledTotalForEachCount = getClusterDetails(htmlfiles)
            #####################################################################################################
            ## Process html files ###############################################################################
            #####################################################################################################
            summary, insertedSum, singleOccurenceKeys = getSameURLSummary(clusterbynamedict, baseFolderName)
            print('expired or new pages: ')
            print(singleOccurenceKeys)
            print(templates)
            #****************************************************************************************************
            print('###################### Same URL (Pre-Post) Noise Analysis ##################################')
            rpmatchedPages, rpnotmatchedPAges, rpexpiredPages,rpsnonMatchingDictList, timeforrepeated = analyzeMonitoredSummaryWithTemplate(templates, summary)
            #****************************************************************************************************
            print('###################### Expired VS New URL Noise Analysis ##################################')
            nematchedPages, nenotmatchedPAges, neexpiredPages, nesnonMatchingDictList, timefornewvsexp = analyzeMonitoredExpiredPagesWithTemplates(clusterbynamedict, templates,baseFolderName)
            #****************************************************************************************************
            print('###################### Totally New Insertions In the Pages ##################################')
            for ki, iv in insertedSum.items():
                print(ki)
                print(iv)
            # ****************************************************************************************************
            print(' <<=============================== REPATED PAGES NOISE ANALYSIS RESULTS: =============================>>')
            print('repeated pages fully matched with NOISE TEMPLATE:')
            print(rpmatchedPages)
            print('.........................................................')
            print('repeated pages but not fully  matched with the templates:')
            print(rpnotmatchedPAges)
            print('.........................................................')
            print('expired template pages in database:')
            print(rpexpiredPages)
            print('.........................................................')
            print('details of repeated but not matched with template pages. Possibley new content !!!!')
            print(rpsnonMatchingDictList)
            print('.........................................................')
            print('Time to compare repeated page analysis = ' + timeforrepeated)
            print('')
            print('<<=========================== NEW vs EXPIRED PAGES ANALYSIS RESULTS: ===========================>>')
            print('new pages fully matched with expired NOISE TEMPLATE:')
            print(nematchedPages)
            print('.........................................................')
            print('new  pages but not fully  matched with the templates:')
            print(nenotmatchedPAges)
            print('.........................................................')
            print('expired template pages in database:')
            print(neexpiredPages)
            print('.........................................................')
            print('details of new pages, but not fully matched with noise template. Possibley new content !!!!')
            print(nesnonMatchingDictList)
            print('.........................................................')
            print('Time to compare repeated page analysis = ' + timefornewvsexp)
            print('<<======================================== END: ================================================>>')
        except OSError:
            continue


#############################################################################################################################
#############################################################################################################################
#############################################################################################################################
#########################################################################################################
# ################################## Analyze summary ######################################################
# tempList = []
# baseDictionaryFromDatabase = {}
# baseDeleteInsertedTemplateKey = 'differentPageDeleteVsInsert2'
# ###################### Extract Templates from Database
# for template in collection.find():
#     tempList.append(json.loads(json.dumps(template, indent=4, default=json_util.default)))
#
# newPages = []
# matchedPages = []
# notmatchedPAges = []
# expiredPages = []
#
# snonMatchingDict = {}
# for page, pageSummary in summary.items():
#     print(page)
#     if pageSummary.__len__()>0:
#         monitoredPageDiff = pageSummary[0]
#         #print(monitoredPageDiff)
#     else:
#         print('NEW PAGE !! - no summary')
#         newPages.append(page)
#         continue
#     sdetails = {}
#     snonMatchingItems = {}
#     smatchingItems = {}
#     stagSizeofMatched ={}
#     stagSizeofNotMatched = {}
#     bfound = False
#     s4 = timeit.default_timer()
#     for temp in tempList:
#         for pageT, pageTemplate in temp.items():
#             if pageT == baseDeleteInsertedTemplateKey:
#                 baseDictionaryFromDatabase = pageTemplate
#             if page == pageT:
#                 print ('page template found')
#                 bfound = True
#                 print('#########################')
#                 tagSuCounter = 0
#                 for tag, values in monitoredPageDiff.items():
#                     for tagT, valuesT in pageTemplate.items():
#                         if tag == tagT:
#                             print('matching Tag')
#                             if compare(values, valuesT,False) == 0:
#                                 print('atleast on instance not equal')
#                                 snonMatchingItems[tag] = values
#                                 stagSizeofNotMatched[tag] = values.__len__()
#                             else:
#                                 print('matching with old ')
#                                 tagSuCounter = tagSuCounter + 1
#                                 smatchingItems[tag] = values
#                                 stagSizeofMatched[tag] = values.__len__()
#                 if tagSuCounter == len(pageTemplate):
#                     matchedPages.append(page)
#                     print('all matched ')
#                 else:
#                     stat = []
#                     dstat = {}
#                     dstat['matchedD'] = stagSizeofMatched
#                     dstat['non-matchedD'] = stagSizeofNotMatched
#                     sdetails['matched'] = smatchingItems
#                     sdetails['non-matched'] =snonMatchingItems
#                     sdetails['details'] = dstat
#                     stat.append(len(smatchingItems))
#                     stat.append(len(snonMatchingItems))
#                     stat.append(len(pageTemplate))
#                     sdetails['stat'] = stat
#                     snonMatchingDict[page] = sdetails
#                     notmatchedPAges.append(page)
#                     print('all matched ')
#
#     e4 = timeit.default_timer()
#     print('Time to compare page with  function= ' + str(e4 - s4))
#     if not bfound:
#         print('page template not exist')
#
# for temp in tempList:
#     for pageT, pageTemplate in temp.items():
#         pageT = pageT.encode('utf-8')
#         if pageT not in matchedPages and  pageT not in notmatchedPAges and pageT !='_id':
#             #print(pageT)
#             expiredPages.append(pageT)
#
#
# print('new pages:')
# print(newPages)
# print('matched pages:')
# print(matchedPages)
# print('not matched pages:')
# print(notmatchedPAges)
# print('expired template pages in database:')
# print(expiredPages)
# print('non matching list')
# print(snonMatchingDict)


####################################################################################################################################################################
############### FULLY DELETED AND THEN FULLY INSERTED PAGES ANALYSIS TO FIND THE NOISE INSERTIONS###################################################################
####################################################################################################################################################################


####################################################################################################
######## Find the NEW pages with the same diff pattern as  'differentPageDeleteVsInsert2' ##########
####################################################################################################

####################################################################################################
################ Compare totally delted vs inserted pages ##########################################
############### Extract constant elements and variable elements ####################################
# if hastotallyDeltetotallyInserted:
#     diffURL = {}
#     basePageHtmlStringOfaDeletedPage = []
#     totallyNewInsertedPages = {}
#     for kp, vp in clusterbynamedict.items():
#         ## Prepare the html string of base page (a deleted page)
#         if kp == baseDetetedPageKey:
#             basePageHtmlStringOfaDeletedPage = getHTMLcontentAsString([vp[0]], baseName)
#             continue
#         ## Prepare the html pages of reset of the newly inserted pages
#         if kp in newPages:
#             #### remove pages from new round, identified by _1
#             if vp[0].split('_')[1] == '1.html':
#                 continue
#             totallyNewInsertedPages[kp] = vp[0]
#
#     ###################################################################################################
#     ############# Open html files and extract only html conntent as a string ##########################
#     htmlOfNewPagesDict = {}
#     for kpi, vpi in totallyNewInsertedPages.items():
#         htmlOfNewPagesDict[kpi] = getHTMLcontentAsString([vpi], baseName)
#
#     for kpis, vips in htmlOfNewPagesDict.items():
#         alteredTagsOfTotalDeletedOrInsertedPages = htmlDiffAnalysis(basePageHtmlStringOfaDeletedPage[0], vips[0])
#         diffURL[kpis] = alteredTagsOfTotalDeletedOrInsertedPages  # totallyNewInsertedPagesKeys variable track the keys
#     print(diffURL)  ##
#
#     ###################Base is the differece of existing page diff in the database 'differentPageDeleteVsInsert2'
#     matchingList = []
#     nonMatchingDict = {}
#
#     for kpi, diffInInsert in diffURL.items():
#         tagDifCounter = 0
#         details = {}
#         nonMatchingItems = {}
#         matchingItems = {}
#         tagSizeofMatched = {}
#         tagSizeofNotMatched = {}
#         for tag, values in diffInInsert.items():
#             for tagT, valuesT in baseDictionaryFromDatabase.items():
#                 if tag == tagT:
#                     print('matching Tag')
#                     if compare(values, valuesT, False) == 0:
#                         print('atleast on instance not equal')
#                         nonMatchingItems[tag] = values
#                         tagSizeofNotMatched[tag] = values.__len__()
#                     else:
#                         print('matching with old ' + str(kpi))
#                         matchingItems[tag] = values
#                         tagSizeofMatched[tag] = values.__len__()
#                         tagDifCounter = tagDifCounter + 1
#         if tagDifCounter == len(diffInInsert):
#             matchingList.append(kpi)
#             print('all matched ')
#         else:
#             stat = []
#             dstat = {}
#             dstat['matchedD'] = tagSizeofMatched
#             dstat['non-matchedD'] = tagSizeofNotMatched
#             details['matched'] = matchingItems
#             details['non-matched'] = nonMatchingItems
#             details['details'] = dstat
#             stat.append(len(matchingItems))
#             stat.append(len(nonMatchingItems))
#             stat.append(len(diffInInsert))
#             details['stat'] = stat
#             nonMatchingDict[kpi] = details
#             print('not all matched ')
#
#     print('new pages:')
#     print(newPages)
#     print('matched pages:')
#     print(matchedPages)
#     print('not matched pages:')
#     print(notmatchedPAges)
#     print('expired template pages in database:')
#     print(expiredPages)
#     print('############## Diff delte vs inserted pages#############')
#     print('matching list')
#     print(matchingList)
#     print('non matching list')
#     print(nonMatchingDict)
#     print('base dictionary size: ' + str(len(baseDictionaryFromDatabase)))
#
# ###
# # TODO: Get the html difference of each new page with resepect a selected deleted page
# # TODO: Next, check whether this difference match with the one in the db 'differentPageDeleteVsInsert2'.
# # TODO: If matched they can be avoided and if not matched they can be further analyzed for information corresponding to action
#
# stop = timeit.default_timer()
# print('Time taken: ', stop - start)
