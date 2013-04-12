__all__=['createHists','createHistsData','drawStack']

from rootpy.interactive import wait
from rootpy.plotting import Canvas, Hist, Hist2D, Hist3D, Legend
from rootpy.io import root_open as ropen, DoesNotExist
from rootpy.plotting import HistStack
import ROOT
ROOT.gROOT.SetBatch(True)



def createHists(sample, labelCodes, nameOfType, labelsForSample, weightsPerSample, foundVariables, allHistStack, createLog = False):

    #TODO: These should really be read in from a settings file
    histDict = {'W':[],'Z':[],'WW':[],'ZZ':[],'st':[],'ttbar':[],'WZ':[],'WH125':[]}

    coloursForStack = ['blue', 'green', 'red', 'yellow', 'black', 'pink', 'magenta', 'cyan']
    colourDict = {'W':0,'Z':1,'WW':2,'ZZ':3,'st':4,'ttbar':5,'WZ':6,'WH125':7}

    fillcol = (nameOfType == 'signal' ? 'blue': 'red')

    hist = []
    histidx = 0
    maxi = []
    mini = []
#    if createLog == True:
    log = open(nameOfType+'.log')
    
    c1 = Canvas()
    c1.cd()
    log.write('########################### '+ nameOfType +' ###########################\n')
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
        for k in histDict.keys():
            histDict[k].append(Hist(20,mini[histidx],maxi[histidx]))
            histDict[k][histidx].fillcolor = coloursForStack[int(colourDict[k])]
            histDict[k][histidx].fillstyle = 'solid'
            histDict[k][histidx].SetOption('hist')
            histDict[k][histidx].SetTitle(k)
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

    for st in foundVariables:
        histStack.append(HistStack(st,st))
        allHistStack.append(HistStack(st,st))
        legendStack.append(Legend(7))
        allLegendStack.append(Legend(7))

    for rw in histDict.keys():
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
    return hist,histDict,histStack,allHistStack,legendStack,allLegendStack

def drawStack(stack, legends, sampleType, dataHist = []):
    c2 = Canvas()
    c2.cd()
    xcount = 0
    for x in stack:
        x.Draw('hist')
        dataHist[xcount].Draw('same')
        legends[xcount].Draw('same')
        
        #x.Write()
        c2.SaveAs(foundVariables[xcount]+str(sampeType)+'Stack.png')
        c2.Write()
        xcount +=1 



def createHistsData(sample, foundVariables, allHistStack, createLog = False):
    histDict = {'data':[]}
    coloursForStack = ['blue', 'green', 'red', 'yellow', 'black', 'pink', 'magenta', 'cyan']
    
    fillcol = 'black'

    hist = []
    histidx = 0
    maxi = []
    mini = []
#    if createLog == True:
    log = open('data.log')
    
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
        
        histDict[k].append(Hist(20,mini[histidx],maxi[histidx]))
        histDict['data'][histidx].fillcolor=fillcol
        histDict['data'][histidx].linecolor=fillcol
        histDict['data'][histidx].SetOption('hist')
        histDict['data'][histidx].SetTitle(k)
        for i in c:
            histDict['data'][histidx].fill(i)
    
        histidx+=1

# create stacks and legends
    histStack = []
    legendStack = []

    for st in foundVariables:
        histStack.append(HistStack(st,st))
        allHistStack.append(HistStack(st,st))
        legendStack.append(Legend(7))
        allLegendStack.append(Legend(7))

    for rw in histDict.keys():
        log.write(rw + ' length: '+str(len(histDict[rw]))+'\n')
        for rwcount in xrange(0,len(histDict[rw])):
            if histDict[rw][rwcount].GetEntries() > 0:
                if rw in weightsPerSample:
                    histDict[rw][rwcount].scale(weightsPerSample[rw])
                histStack[rwcount].Add(histDict[rw][rwcount].Clone())
                # don't want to add data to stack with stack option
                #allHistStack[rwcount].Add(histDict[rw][rwcount].Clone())
                histDict[rw][rwcount].draw('hist')
                legendStack[rwcount].AddEntry( histDict[rw][rwcount], 'F')
                #allLegendStack[rwcount].AddEntry( histDict[rw][rwcount], 'F')
                c1.SaveAs("histDictData"+str(rwcount)+".png")
                log.write(rw + '['+str(rwcount)+'] entries: ' + str(histDict[rw][rwcount].GetEntries())+'\n')
    log.close()
    return hist,histDict,histStack,legendStack
