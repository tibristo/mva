__all__=['createHists','createHistsData','drawStack']
from numpy import argmax,argmin
from rootpy.interactive import wait
from rootpy.plotting import Canvas, Hist, Hist2D, Hist3D, Legend
from rootpy.io import root_open as ropen, DoesNotExist
from rootpy.plotting import HistStack
import ROOT
ROOT.gROOT.SetBatch(True)



def createHists(sample, labelCodes, nameOfType, labelsForSample, weightsPerSample, foundVariables, allHistStack, allLegendStack, createLog = False):

    #TODO: These should really be read in from a settings file
    histDict = {'W':[],'Z':[],'WW':[],'ZZ':[],'st':[],'ttbar':[],'WZ':[],'WH125':[]}

    coloursForStack = ['blue', 'green', 'red', 'yellow', 'black', 'pink', 'magenta', 'cyan']
    colourDict = {'W':0,'Z':1,'WW':2,'ZZ':3,'st':4,'ttbar':5,'WZ':6,'WH125':7}

    if nameOfType == 'signal':
        fillcol = 'blue'
    else:
        fillcol = 'red'
    hist = []
    histidx = 0
    maxi = []
    mini = []
#    if createLog == True:
    log = open(nameOfType+'.log','w')
    
    c1 = Canvas()
    c1.cd()
    log.write('########################### '+ nameOfType +' ###########################\n')
#    for c in sample:
    for c in sample:
        maxi.append(c[argmax(c)])
        mini.append(c[argmin(c)])
        hist.append(Hist(20,mini[histidx],maxi[histidx]))
        hist[histidx].fill_array(c)
        

        hist[histidx].scale(1.0/hist[histidx].integral())
        
        hist[histidx].fillcolor=fillcol
        hist[histidx].linecolor=fillcol
        
        hist[histidx].GetXaxis().SetTitle(foundVariables[histidx])
        hist[histidx].GetYaxis().SetTitle('# Events Normalised to 1')
        hist[histidx].SetTitle(nameOfType)
        hist[histidx].fillstyle='solid'
        lblcount = 0
        for k in histDict.iterkeys():
            histDict[k].append(Hist(20,mini[histidx],maxi[histidx]))
            histDict[k][histidx].fillcolor = coloursForStack[int(colourDict[k])]
            histDict[k][histidx].fillstyle = 'solid'
            histDict[k][histidx].SetOption('hist')
            histDict[k][histidx].SetTitle(str(k) + str(foundVariables[histidx]))
        for i in c:
            lbl = labelCodes[int(labelsForSample[lblcount])]
        #if len(histDict[lbl]) >= histidx and histDict[lbl][histidx] == []:
        # weight i
            weighted_i = i
            histDict[lbl][histidx].fill(weighted_i)
            lblcount += 1
        #log.write(lbl + '['+str(histidx)+']: '+str(weighted_i)+'\n')
    
        histidx+=1

# create stacks and legends
    histStack = []
    legendStack = []
    if len(allHistStack) == 0:
        initStack = True
    else:
        initStack = False
    for st in foundVariables:
        if initStack == True:
            allHistStack.append(HistStack(st,st))
            allLegendStack.append(Legend(7))
        histStack.append(HistStack(st,st))
        legendStack.append(Legend(7))


    for rw in histDict.iterkeys():
        log.write(rw + ' length: '+str(len(histDict[rw]))+'\n')
        for rwcount in xrange(0,len(histDict[rw])):
            if histDict[rw][rwcount].GetEntries() > 0:
                if rw in weightsPerSample:
                    histDict[rw][rwcount].scale(weightsPerSample[rw])
                histStack[rwcount].Add(histDict[rw][rwcount].Clone())
                allHistStack[rwcount].Add(histDict[rw][rwcount].Clone())
                histDict[rw][rwcount].draw('hist')
                legendStack[rwcount].AddEntry( histDict[rw][rwcount], 'F')
                allLegendStack[rwcount].AddEntry( histDict[rw][rwcount], 'F')
                c1.SaveAs("histDict"+str(nameOfType)+str(rwcount)+".png")
                log.write(rw + '['+str(rwcount)+'] entries: ' + str(histDict[rw][rwcount].GetEntries())+'\n')
    log.close()
    return hist,histDict,histStack,legendStack

def drawStack(stack, legends, foundVariables, sampleType,  dataHist = []):
    c2 = Canvas()
    c2.cd()
    xcount = 0
    for x in stack:
        x.Draw('hist')
        if len(dataHist) > 0:
            dataHist['data'][xcount].Draw('same')
        legends[xcount].Draw('same')
        
        #x.Write()
        c2.SaveAs(foundVariables[xcount]+str(sampleType)+'Stack.png')
        c2.Write()
        xcount +=1 



def createHistsData(sample, foundVariables, allHistStack, allLegendStack, createLog = False):
    histDict = {'data':[]}
    coloursForStack = ['blue', 'green', 'red', 'yellow', 'black', 'pink', 'magenta', 'cyan']
    
    fillcol = 'black'

    hist = []
    histidx = 0
    maxi = []
    mini = []
#    if createLog == True:
    log = open('data.log','w')
    
    c1 = Canvas()
    c1.cd()
    log.write('########################### DATA  ###########################\n')
    for c in sample:
        maxi.append(c[argmax(c)])
        mini.append(c[argmin(c)])
        hist.append(Hist(20,mini[histidx],maxi[histidx]))
        hist[histidx].fill_array(c)
        hist[histidx].scale(1.0/hist[histidx].integral())
        
        hist[histidx].fillcolor=fillcol
        hist[histidx].linecolor=fillcol
        
        hist[histidx].GetXaxis().SetTitle(foundVariables[histidx])
        hist[histidx].GetYaxis().SetTitle('# Events Normalised to 1')
        hist[histidx].SetTitle('data')
        hist[histidx].fillstyle='solid'
        
        histDict['data'].append(Hist(20,mini[histidx],maxi[histidx]))
        histDict['data'][histidx].fillcolor=fillcol
        histDict['data'][histidx].linecolor=fillcol
        histDict['data'][histidx].SetOption('hist')
        histDict['data'][histidx].SetTitle('data ' + foundVariables[histidx])
        for i in c:
            histDict['data'][histidx].fill(i)
    
        histidx+=1

    # create stacks and legends
    histStack = []
    legendStack = []
    if len(allHistStack) == 0:
        initStack = True
    else:
        initStack = False
    for st in foundVariables:
        #if initStack == True:
        #allHistStack.append(HistStack(st,st))
        #allLegendStack.append(Legend(7))
        histStack.append(HistStack(st,st))
        legendStack.append(Legend(7))


    for rw in histDict.keys():
        log.write(rw + ' length: '+str(len(histDict[rw]))+'\n')
        for rwcount in xrange(0,len(histDict[rw])):
            if histDict[rw][rwcount].GetEntries() > 0:
                histStack[rwcount].Add(histDict[rw][rwcount].Clone())
                # don't want to add data to stack with stack option

                histDict[rw][rwcount].draw('hist')
                legendStack[rwcount].AddEntry( histDict[rw][rwcount], 'F')

                c1.SaveAs("histDictData"+str(rwcount)+".png")
                log.write(rw + '['+str(rwcount)+'] entries: ' + str(histDict[rw][rwcount].GetEntries())+'\n')
    log.close()
    return hist,histDict,histStack,legendStack
