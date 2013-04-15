__all__=['createHists','createHistsData','drawStack']
from numpy import argmax,argmin
from rootpy.interactive import wait
from rootpy.plotting import Canvas, Hist, Hist2D, Hist3D, Legend
from rootpy.io import root_open as ropen, DoesNotExist
from rootpy.plotting import HistStack
import ROOT
ROOT.gROOT.SetBatch(True)

# store variables and hist max/ min values
histLimits = {}

def readXML():
    global histLimits
    
    import xml.etree.ElementTree as ET
    xmlTree = ET.parse('settingsPlot.xml')
    root = xmlTree.getroot()

    varName = ''
    branches = []
    for child in root.findall('varName'):
        varName = child.get('name')
        maxV = float(child.find('maxValue').text)
        minV = float(child.find('minValue').text)
        histLimits[varName] = [minV,maxV]

readXML()
    

def createHists(sample, labelCodes, nameOfType, labelsForSample, weightsPerSample, foundVariables, allHistStack, allLegendStack, createLog = False):
    global histLimits
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

    log = open(nameOfType+'.log','w')
    
    c1 = Canvas()
    c1.cd()
    log.write('########################### '+ nameOfType +' ###########################\n')

    for c in sample:
        variableName = foundVariables[histidx]
        #maxi.append(c[argmax(c)])
        #mini.append(c[argmin(c)])
        #hist.append(Hist(20,mini[histidx],maxi[histidx]))
        hist.append(Hist(20,int(histLimits[variableName][0]),int(histLimits[variableName][1])))
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
            #histDict[k].append(Hist(20,mini[histidx],maxi[histidx]))
            histDict[k].append(Hist(20,int(histLimits[variableName][0]),int(histLimits[variableName][1])))
            histDict[k][histidx].fillcolor = coloursForStack[int(colourDict[k])]
            histDict[k][histidx].fillstyle = 'solid'
            histDict[k][histidx].SetOption('hist')
            histDict[k][histidx].SetTitle(str(k) + str(foundVariables[histidx]))
        for i in c:
            lbl = labelCodes[int(labelsForSample[lblcount])]
            histDict[lbl][histidx].fill(i)
            lblcount += 1
      
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
    #should create a ratio plot too!!! get teh scaling right...
    for x in stack:
        
        if len(dataHist) > 0:
            x.Draw()
            xmax = x.GetHistogram().GetMaximum()
            dmax = dataHist['data'][xcount].GetMaximum()
            tmax = max(xmax, dmax)
            x.SetMaximum(tmax*1.1)
            x.Draw('hist')
            dataHist['data'][xcount].Draw('same')
        else:
            x.Draw('hist')
        
        legends[xcount].Draw('same')
        
        c2.SaveAs(foundVariables[xcount]+str(sampleType)+'Stack.png')
        c2.Write()
        xcount +=1 



def createHistsData(sample, foundVariables, allHistStack, allLegendStack, createLog = False):
    histDict = {'data':[]}
    coloursForStack = ['blue', 'green', 'red', 'yellow', 'black', 'pink', 'magenta', 'cyan']
    global histLimits 
    fillcol = 'black'

    hist = []
    histidx = 0
    maxi = []
    mini = []
    log = open('data.log','w')
    
    c1 = Canvas()
    c1.cd()
    log.write('########################### DATA  ###########################\n')
    for c in sample:
        variableName = foundVariables[histidx]
        hist.append(Hist(20,int(histLimits[variableName][0]),int(histLimits[variableName][1])))
        hist[histidx].fill_array(c)
        hist[histidx].scale(1.0/hist[histidx].integral())
        
        hist[histidx].fillcolor=fillcol
        hist[histidx].linecolor=fillcol
        
        hist[histidx].GetXaxis().SetTitle(foundVariables[histidx])
        hist[histidx].GetYaxis().SetTitle('# Events Normalised to 1')
        hist[histidx].SetTitle('data')
        hist[histidx].fillstyle='solid'
        
        histDict['data'].append(Hist(20,int(histLimits[variableName][0]),int(histLimits[variableName][1])))
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

    for st in foundVariables:
        histStack.append(HistStack(st,st))
        legendStack.append(Legend(7))


    for rw in histDict.keys():
        log.write(rw + ' length: '+str(len(histDict[rw]))+'\n')
        for rwcount in xrange(0,len(histDict[rw])):
            if histDict[rw][rwcount].GetEntries() > 0:
                histStack[rwcount].Add(histDict[rw][rwcount].Clone())
                histDict[rw][rwcount].draw('hist')
                legendStack[rwcount].AddEntry( histDict[rw][rwcount], 'F')
                allLegendStack[rwcount].AddEntry(histDict[rw][rwcount], 'F')
                c1.SaveAs("histDictData"+str(rwcount)+".png")
                log.write(rw + '['+str(rwcount)+'] entries: ' + str(histDict[rw][rwcount].GetEntries())+'\n')
    log.close()
    return hist,histDict,histStack,legendStack
