from numpy import argmax,argmin
import sortAndCut as sc
from numpy import transpose,bincount
from rootpy.interactive import wait
from rootpy.plotting import Canvas, Hist, Hist2D, Hist3D, Legend
from rootpy.io import root_open as ropen, DoesNotExist
from rootpy.plotting import HistStack
import ROOT
ROOT.gROOT.SetBatch(True)

__all__=['createHists','createHistsData','drawStack','readVarNamesXML','drawAllTrainStacks','drawAllTestStacks']

# store variables and hist max/ min values
histLimits = {}

def readVarNamesXML():
    """Read in all the variable names from the settingsPlot.xml file."""
    import xml.etree.ElementTree as ET
    xmlTree = ET.parse('settingsPlot.xml')
    root = xmlTree.getroot()
    names = []
    for child in root.findall('varName'):
        names.append(child.get('name'))
    return names

def readXML():
    """Read in the variable names and histogram limits froms the settingsPlot.xml file."""
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
    

def drawSigBkgDistrib(sample, classif, foundVariables):
    idx = 0
    c1 = Canvas()
    c1.cd()
    histidx = 0
    histSig = []
    histBkg = []

    classif, sample = sc.sortMultiple(classif,sample)
    sample2 = transpose(sample)
    binc = bincount(classif)
    numzero = binc[0]
    numone = binc[1]
    global histLimits
    print len(sample2)
    print sample2
    for x in sample2:
        x = transpose(x)
        variableName = foundVariables[histidx]
        histSig.append(Hist(50,int(histLimits[variableName][0]),int(histLimits[variableName][1])))
        histSig[histidx].fill_array(x[:numzero])
        histSig[histidx].scale(1.0/histSig[histidx].integral())

        histSig[histidx].fillcolor='red'
        histSig[histidx].SetFillStyle(3004)
        histSig[histidx].linecolor='red'
        
        histSig[histidx].GetXaxis().SetTitle(foundVariables[histidx])
        histSig[histidx].GetYaxis().SetTitle('# Events Normalised to 1')
        histSig[histidx].SetTitle('Background')
#        histSig[histidx].fillstyle='solid'
        histSig[histidx].SetStats(0)
        

        histBkg.append(Hist(50,int(histLimits[variableName][0]),int(histLimits[variableName][1])))
        histBkg[histidx].fill_array(x[numzero:])
        histBkg[histidx].scale(1.0/histBkg[histidx].integral())

        histBkg[histidx].fillcolor='blue'
        histBkg[histidx].linecolor='blue'
        histBkg[histidx].SetFillStyle(3005)
        
        histBkg[histidx].GetXaxis().SetTitle(foundVariables[histidx])
        histBkg[histidx].GetYaxis().SetTitle('# Events Normalised to 1')
        histBkg[histidx].SetTitle('Signal')
#        histBkg[histidx].fillstyle='solid'
        histBkg[histidx].SetStats(0)

        leg = Legend(2)
        leg.AddEntry(histBkg[histidx],'F')
        leg.AddEntry(histSig[histidx],'F')

        histBkg[histidx].draw('hist')
        histSig[histidx].draw('histsame')
        leg.Draw('same')
        c1.SaveAs(variableName+"SigBkgComparison.png")
        histidx+=1

def createHists(sample, labelCodes, nameOfType, labelsForSample, weightsPerSample, foundVariables, allHistStack, allLegendStack, corrWeights, subset = 'TestA', createLog = False):
    """Create all of the histograms for each sample and save them to file.
    
    Keyword arguments:
    sample -- the sample from which the histograms are created
    labelCodes -- the codes for all of the labels (0 == W, for eg.)
    nameOfType -- signal or bkg (default bkg)
    labelsForSample -- the labels of all the entries in the sample
    weightsPerSample -- the XS weight
    foundVariables -- the variables in the order in which they were found
    allHistStack -- the histogram stack of all of the samples
    allLegendStack -- the legends for all samples and entries to go on the stack
    subset -- extra label for the output file (default A)
    createLog -- create a log for the output (default False)
    
    """
    global histLimits
    #TODO: These should really be read in from a settings file
    histDict = {'W':[],'Z':[],'WW':[],'ZZ':[],'st':[],'ttbar':[],'WZ':[],'WH125':[]}

    #coloursForStack = ['Green', 'Blue', 'Orange', 'Orange', 'Orange-2', 'Yellow', 'Pink', 'Red']
    coloursForStack = [3, 4, 800, 800, 795, 5, 6, 2]
    colourDict = {'W':0,'Z':1,'WW':2,'ZZ':3,'st':4,'ttbar':5,'WZ':6,'WH125':7}

    if nameOfType == 'signal':
        fillcol = 'blue'
    else:
        fillcol = 'red'
    hist = []
    histidx = 0

    log = open(nameOfType+subset+'.log','w')
    
    c1 = Canvas()
    c1.cd()
    log.write('########################### '+ nameOfType +' ###########################\n')
    for c in sample:
        variableName = foundVariables[histidx]
        #hist.append(Hist(50,int(histLimits[variableName][0]),int(histLimits[variableName][1])))
        hist.append(Hist(50,int(histLimits[variableName][0]),int(histLimits[variableName][1])))
        hist[histidx].fill_array(c)
        hist[histidx].scale(1.0/hist[histidx].integral())
        
        hist[histidx].fillcolor=fillcol
        hist[histidx].linecolor=fillcol
        
        hist[histidx].GetXaxis().SetTitle(foundVariables[histidx])
        hist[histidx].GetYaxis().SetTitle('# Events Normalised to 1')
        hist[histidx].SetTitle(nameOfType)
        hist[histidx].fillstyle='solid'
        hist[histidx].SetStats(0)
        lblcount = 0
        for k in histDict.iterkeys():
            #histDict[k].append(Hist(50,int(histLimits[variableName][0]),int(histLimits[variableName][1])))
            histDict[k].append(Hist(50,int(histLimits[variableName][0]),int(histLimits[variableName][1])))
            #histDict[k][histidx].fillcolor = coloursForStack[int(colourDict[k])]
            histDict[k][histidx].SetFillColor(int(coloursForStack[int(colourDict[k])]))
            histDict[k][histidx].fillstyle = 'solid'
            histDict[k][histidx].SetOption('hist')
            histDict[k][histidx].SetTitle(str(k))# + str(foundVariables[histidx]))
            histDict[k][histidx].SetStats(0)
            histDict[k][histidx].GetXaxis().SetTitle(foundVariables[histidx])
            histDict[k][histidx].GetYaxis().SetTitle('# Events')
        for i in c:
            lbl = labelCodes[int(labelsForSample[lblcount])]
            histDict[lbl][histidx].fill(i)
            lblcount += 1
      
        histidx+=1

    # create stacks and legends
    histStack = []
    legendStack = []
    if not allHistStack:
        initStack = True
    else:
        initStack = False
    for st in foundVariables:
        if initStack == True:
            allHistStack.append(HistStack(st,st))
            allLegendStack.append(Legend(7))
        histStack.append(HistStack(st,st))
        legendStack.append(Legend(7))
    rwcount_outer = 0
    for rw in histDict.iterkeys():
        log.write(rw + ' length: '+str(len(histDict[rw]))+'\n')
        for rwcount in xrange(0,len(histDict[rw])):
            if histDict[rw][rwcount].GetEntries() > 0:
                if rw in weightsPerSample:
                    histDict[rw][rwcount].scale(weightsPerSample[rw])
                    histDict[rw][rwcount].scale(corrWeights[rwcount_outer][rwcount])
                histStack[rwcount].Add(histDict[rw][rwcount].Clone())
                allHistStack[rwcount].Add(histDict[rw][rwcount].Clone())
                histStack[rwcount].Draw()
                allHistStack[rwcount].Draw()
                histDict[rw][rwcount].draw('hist')
                histStack[rwcount].GetXaxis().SetTitle(histDict[rw][rwcount].GetXaxis().GetTitle())
                histStack[rwcount].GetYaxis().SetTitle('# Events')
                allHistStack[rwcount].GetXaxis().SetTitle(histDict[rw][rwcount].GetXaxis().GetTitle())
                allHistStack[rwcount].GetYaxis().SetTitle('# Events')
                legendStack[rwcount].AddEntry( histDict[rw][rwcount], 'F')
                allLegendStack[rwcount].AddEntry( histDict[rw][rwcount], 'F')
                c1.SaveAs("histDict"+str(nameOfType)+str(subset)+str(rwcount)+".png")
                log.write(rw + '['+str(rwcount)+'] entries: ' + str(histDict[rw][rwcount].GetEntries())+'\n')
        rwcount_outer += 1
    log.close()

    return hist,histDict,histStack,legendStack

def drawStack(stack, legends, foundVariables, sampleType, subset = 'TestA', dataHist = {}):
    """Draw the given stack.
    
    Keyword arguments:
    stack -- the stack to be drawn
    legends -- the accompanying legends
    foundVariables -- the variables in the stack that are being drawn
    sampleType -- signal or bkg
    subset -- acts as extra identifier in the filename (default A)
    dataHist -- the data histograms (default [])
    
    """
    c2 = Canvas()
    c2.cd()
    xcount = 0
    # should create a ratio plot too!!! get teh scaling right...
    for x in stack:
        if dataHist:
            x.Draw()
            xmax = x.GetHistogram().GetMaximum()
            dmax = dataHist['data'][xcount].GetMaximum()
            x.SetMaximum(max(xmax,dmax)*1.1)
            x.Draw('hist')
            dataHist['data'][xcount].Draw('same')
        else:
            x.Draw('hist')
        
        legends[xcount].Draw('same')
        c2.SaveAs(foundVariables[xcount]+str(sampleType)+str(subset)+'Stack.png')
        c2.Write()
        xcount +=1 

def createHistsData(sample, foundVariables, allHistStack, allLegendStack, subset = 'TestA', createLog = False):
    """Create histograms for data.
    
    Keyword arguments:
    sample -- the input data sample
    foundVariables -- the variables in the sample, in order
    allHistStack -- the histogram stack for all other samples
    subset -- an extra identifier for the filename (default TestA)
    createLog -- create a log (default False)
    
    """
    histDict = {'data':[]}
    coloursForStack = ['blue', 'green', 'red', 'yellow', 'black', 'pink', 'magenta', 'cyan']
    global histLimits 
    fillcol = 'black'

    hist = []
    histidx = 0
    log = open('data'+str(subset)+'.log','w')
    
    c1 = Canvas()
    c1.cd()
    log.write('########################### DATA  ###########################\n')
    for c in sample:
        variableName = foundVariables[histidx]
        #hist.append(Hist(50,int(histLimits[variableName][0]),int(histLimits[variableName][1])))
        hist.append(Hist(50,int(histLimits[variableName][0]),int(histLimits[variableName][1])))
        hist[histidx].fill_array(c)
        hist[histidx].scale(1.0/hist[histidx].integral())
        
        hist[histidx].fillcolor=fillcol
        hist[histidx].linecolor=fillcol
        
        hist[histidx].GetXaxis().SetTitle(foundVariables[histidx])
        hist[histidx].GetYaxis().SetTitle('# Events Normalised to 1')
        hist[histidx].SetTitle('data')
        hist[histidx].fillstyle='solid'
        hist[histidx].SetStats(0)
        
        #histDict['data'].append(Hist(50,int(histLimits[variableName][0]),int(histLimits[variableName][1])))
        histDict['data'].append(Hist(50,int(histLimits[variableName][0]),int(histLimits[variableName][1])))
        histDict['data'][histidx].fillcolor=fillcol
        histDict['data'][histidx].linecolor=fillcol
        histDict['data'][histidx].SetOption('hist')
        histDict['data'][histidx].SetTitle('data')
        histDict['data'][histidx].GetXaxis().SetTitle(foundVariables[histidx])
        histDict['data'][histidx].GetYaxis().SetTitle("# Events")
        histDict['data'][histidx].SetStats(0)
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
                histStack[rwcount].Draw()
                histStack[rwcount].GetXaxis().SetTitle(histDict[rw][rwcount].GetXaxis().GetTitle())
                histStack[rwcount].GetYaxis().SetTitle('# Events')
                histDict[rw][rwcount].draw('hist')
                legendStack[rwcount].AddEntry( histDict[rw][rwcount], 'F')
                allLegendStack[rwcount].AddEntry(histDict[rw][rwcount], 'F')
                c1.SaveAs("histDictData"+str(subset)+str(rwcount)+".png")
                log.write(rw + '['+str(rwcount)+'] entries: ' + str(histDict[rw][rwcount].GetEntries())+'\n')
    log.close()

    return hist,histDict,histStack,legendStack

import Sample

DEFAULT = ones((1,1))

def drawAllTestStacks(signal, bkg, data, labelCodes, weightsPerSampleA, weightsPerSampleB, onlyOne = 'N', corrWeightsA = DEFAULT, corrWeightsB = DEFAULT):
    """Draw all test stacks for signal, bkg and data at once.

    Keyword arguments:
    signal -- the signal sample
    bkg -- the background sample
    data -- the data sample
    labelCodes -- the label codes for the type of sample (W, Z for eg.)
    weightsPerSampleA -- the XS weight for subset A
    weightsPerSampleB -- the XS weight for subset B
    
    """
    if corrWeightsA is DEFAULT:
        corrWeightsA = hstack(signal.returnTestCorrectionWeights('A'), bkg.returnTestCorrectionWeights('A'))
    if corrWeightsB is DEFAULT:
        corrWeightsB = hstack(signal.returnTestCorrectionWeights('B'), bkg.returnTestCorrectionWeights('B'))
    # store all histograms in output.root
    for x in xrange (0, len(signal.test)):
        if x == 0:
            subset = 'A'
            weightsPerSample = weightsPerSampleA
            corrWeights = corrWeightsA
        else:
            subset = 'B'
            weightsPerSample = weightsPerSampleB
            corrWeights = corrWeightsB
        f = ropen('outputTest'+str(subset)+'.root','recreate')
        c1 = Canvas()
        c1.cd()

        allStack = []
        legendAllStack = []
        # get sigA histograms
        hist, histDictSigA, testAStack, legendSigStack = createHists(signal.returnTestSample(subset), labelCodes, 'signal', signal.returnTestSampleLabels(subset), weightsPerSample[0], signal.returnFoundVariables(), allStack, legendAllStack, corrWeights,str('Test'+subset), True)
        # get bkgA histograms
        # how to fix legends????
        hist2, histDictBkgA, testAStackBkg,legendBkgStack  = createHists(bkg.returnTestSample(subset), labelCodes, 'bkg', bkg.returnTestSampleLabels(subset), weightsPerSample[1], bkg.returnFoundVariables(), allStack, legendAllStack, corrWeights, str('Test'+subset), True)
        # get data histograms
        histData, histDictDataA, testAStackData, legendDataStack = createHistsData(data.returnTestSample(), data.returnFoundVariables(), allStack, legendAllStack, str('Test'+subset), True)
    
        for hist2idx in xrange(0,len(hist)):
            legend = Legend(3)
            legend.AddEntry(hist[hist2idx],'F')
            legend.AddEntry(hist2[hist2idx],'F')
            legend.AddEntry(histData[hist2idx],'F')
            
            hist[hist2idx].draw('hist')
            hist[hist2idx].Write()
            hist2[hist2idx].draw('histsame')
            hist2[hist2idx].Write()
            histDictDataA['data'][hist2idx].draw('same')
            histDictDataA['data'][hist2idx].Write()
            
            legend.Draw('same')
            c1.Write()
            c1.SaveAs(signal.returnFoundVariables()[hist2idx]+".png")
            hist2idx+=1
        
        drawStack(testAStack, legendSigStack, signal.returnFoundVariables(), 'Sig', str('Test'+subset)) # draw histograms
        drawStack(testAStackBkg, legendBkgStack, bkg.returnFoundVariables(), 'Bkg', str('Test'+subset))
        drawStack(allStack, legendAllStack, data.returnFoundVariables(), 'Data', str('Test'+subset), histDictDataA)
        drawStack(allStack, legendAllStack, signal.returnFoundVariables(), 'All', str('Test' + subset))
        
    f.close()

def drawAllTrainStacks(signal, bkg, data, labelCodes, weightsPerSampleA, weightsPerSampleB, corrWeightsA = DEFAULT, corrWeightsB = DEFAULT, subset = 'TrainA'):
    """Draw all train stacks for signal and bkg at once.

    Keyword arguments:
    signal -- the signal sample
    bkg -- the background sample
    labelCodes -- the label codes for the type of sample (W, Z for eg.)
    weightsPerSample -- the XS weight
    subset -- extra identifier for the filename (default TrainA)
    
    """
    if corrWeightsA is DEFAULT:
        corrWeightsA = hstack(signal.returnTestCorrectionWeights('A'), bkg.returnTestCorrectionWeights('A'))
    if corrWeightsB is DEFAULT:
        corrWeightsB = hstack(signal.returnTestCorrectionWeights('B'), bkg.returnTestCorrectionWeights('B'))
    # store all histograms in output.root

    for x in xrange (0, len(signal.train)):
        if x == 0:
            subset = 'A'
            weightsPerSample = weightsPerSampleA
            corrWeights = corrWeightsA
        else:
            subset = 'B'
            weightsPerSample = weightsPerSampleB
            corrWeights = corrWeightsB
        f = ropen('outputTrain'+str(subset)+'.root','recreate')
        print subset
        c1 = Canvas()
        c1.cd()

        allStack = []
        legendAllStack = []
        # get sigA histograms
        hist, histDictSigA, testAStack, legendSigStack = createHists(signal.returnTrainSample(subset), labelCodes, 'signal', signal.returnTrainSampleLabels(subset), weightsPerSample[0], signal.returnFoundVariables(), allStack, legendAllStack, corrWeights, str('Train'+subset), True)
        # get bkgA histograms
        # how to fix legends????
        hist2, histDictBkgA, testAStackBkg, legendBkgStack  = createHists(bkg.returnTrainSample(subset), labelCodes, 'bkg', bkg.returnTrainSampleLabels(subset), weightsPerSample[1], bkg.returnFoundVariables(), allStack, legendAllStack, corrWeights, str('Train'+subset), True)

        for hist2idx in xrange(0,len(hist)):
            legend = Legend(3)
            legend.AddEntry(hist[hist2idx],'F')
            legend.AddEntry(hist2[hist2idx],'F')
            
            hist[hist2idx].draw('hist')
            hist[hist2idx].Write()
            hist2[hist2idx].draw('histsame')
            hist2[hist2idx].Write()
            
            legend.Draw('same')
            c1.Write()
            c1.SaveAs(signal.returnFoundVariables()[hist2idx]+".png")
            hist2idx+=1
        
        drawStack(testAStack, legendSigStack, signal.returnFoundVariables(), 'Sig', str('Train'+subset)) # draw histograms
        drawStack(testAStackBkg, legendBkgStack, bkg.returnFoundVariables(), 'Bkg', str('Train'+subset))
        drawStack(allStack, legendAllStack, signal.returnFoundVariables(), 'All', str('Train' + subset))
        
    f.close()

