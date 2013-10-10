#from multiprocessing import Process, Pipe
#import numpy
import adaBoost as ab
import pickle
import copy
from root_numpy import *
import sys
import createHists
import sortAndCut as sc
import Sample
import ROOT
ROOT.gROOT.SetBatch(True)

from IPython import parallel as p


rc=p.Client()
lview = rc.load_balanced_view()
lview.block = False

if len(sys.argv) < 1:
    print 'not enough arguments supplied, need argument for type of sample'
    sys.exit("not enough args supplied")

# read in samples and convert to numpy arrays
#sig = Sample.Sample('/Disk/speyside8/lhcb/atlas/tibristo/Ntuple120_sumet_sig12_FullCutflow.root','Ntuple','sig')
def createObjects(bkg_type, identity = ''):
    import numpy
    import root_numpy
    import sys
    import createHists
    import sortAndCut as sc
    import Sample
    import trainBDTs
    sig = Sample.Sample('/media/Acer/mvaFiles/trigger/Ntuple120_trigger_sig12_FullCutflow.root','Ntuple','sig')
    bkg = Sample.Sample('/media/Acer/mvaFiles/trigger/Ntuple120_trigger_bkg12.root','Ntuple','bkg')
    dataSample = Sample.Sample('/media/Acer/mvaFiles/trigger/Ntuple120_trigger_data12.root','Ntuple','data')

    print 'Finished reading in all samples'

# keep indices of variables we want
    varIdx = []
    varIdxBkg = []
    varIdxData = []
    varWIdx = []
    variablesNames = createHists.readVarNamesXML()
    varWeightsHash = {'xs':-1,'xscorr1':-1,'xscorr2':-1,'final_xs':-1,'label':-1,'label_code':-1,'name':-1,'name_code':-1,'AllEntries':-1, 'VpT_truth':-1, 'dPhiVBB': -1, 'weight_MC' : -1, 'weight_PU' : -1, 'weight_lepton1' : -1, 'weight_MET' : -1}
    varWeightsHashBkg = {'xs':-1,'xscorr1':-1,'xscorr2':-1,'final_xs':-1,'label':-1,'label_code':-1,'name':-1,'name_code':-1, 'AllEntries':-1, 'VpT_truth':-1, 'dPhiVBB': -1, 'weight_MC' : -1, 'weight_PU' : -1, 'weight_lepton1' : -1, 'weight_MET' : -1}
    foundVariables = []
    foundVariablesBkg = []
    foundVariablesData = []

# cut in half for training and testing, remove unwanted variables not for training
# set up testing and training samples for signal and background

    sig.getVariableNames(variablesNames, foundVariables, varIdx, varWeightsHash)
    bkg.getVariableNames(variablesNames, foundVariablesBkg, varIdxBkg, varWeightsHashBkg)
    dataSample.getVariableNames(variablesNames, foundVariablesData, varIdxData)

# create the training trees/ arrays
# TODO: these should be stored in the xml settings file
    #nEntries = 14443742.0
    nEntries = 13600000.0 + 82900.0

    lumi = 13000.00#20300.0
#lumi for 2011
#lumi = 4700.00
#lumi for 2012
#lumi = 20300.0
    labelCodes = sc.readInLabels()

    sig.getTrainingData(sig.returnFullLength(), 'A', nEntries, lumi, labelCodes)
    sig.getTrainingData(sig.returnFullLength(), 'B', nEntries, lumi, labelCodes)
    bkg.getTrainingData(bkg.returnFullLength(), 'A', nEntries, lumi, labelCodes)
    bkg.getTrainingData(bkg.returnFullLength(), 'B', nEntries, lumi, labelCodes)

    print 'Finished getting training data'
    
    sig.sortTrainSamples()
    bkg.sortTrainSamples()
    print 'Finished sorting training samples'

# Set up the testing samples
    sig.getTestingData(sig.returnFullLength(), 'A', nEntries, lumi, labelCodes)
    sig.getTestingData(sig.returnFullLength(), 'B', nEntries, lumi, labelCodes)
    bkg.getTestingData(bkg.returnFullLength(), 'A', nEntries, lumi, labelCodes)
    bkg.getTestingData(bkg.returnFullLength(), 'B', nEntries, lumi, labelCodes)
    dataSample.getTestingDataForData(nEntries, lumi)
    
    adas = trainBDTs.trainBDTs(bkg_type, sig, bkg, identity)

    return adas

#@lview.parallel(block=False)
def runFits(ada):
    import pickle
    try:
        with open(ada,'r') as f:
            adax = pickle.load(f)
    #adax = copy.deepcopy(ada)
        adax.run()
        adaNew = ada[:len(ada)-7]+'_trained.pickle'
        with open(adaNew, 'w') as g:
            pickle.dump(adax, g)
        return adaNew
    except:
        return 'error doing adaBoost training!'
    

#need to multithread this
#sig_ref = p.Reference('sig')
#bkg_ref = p.Reference('bkg')

adas = []
labelCode_test = ['bkg','bkg']#,'bkg','bkg']#,'Wc']

if __name__ == '__main__':
    arlist = []
    count = 0
    #Need to add extra labelCode for full bkg#
    for x in labelCode_test:#labelCodes:
        #if not bkg.hasBkg(x):
        #    continue
        print 'begin process for ' + x

        arlist.append(lview.apply_async(createObjects, x, str(count)))#[x,sig,bkg]))
        count+=1

    print 'Waiting for processes to finish'
    lview.wait(arlist)
    for x in arlist:
        print 'Getting next process output'
        adas.append(x.get())
 
tx_list = []

#for r in rc:
#    r.clear()
print "save adaBoost objects to file"

for x in adas:
    with open(str(x[0].returnName()+'.pickle'),'w') as f:
        pickle.dump(x[0],f)
    with open(str(x[1].returnName()+'.pickle'),'w') as g:
        pickle.dump(x[1],g)


print 'Looping through adas to do fitting'
fit_list = []
#import runFits
names = []
for a in adas:
    names.append((a[0].returnName()+'.pickle'))
    names.append((a[1].returnName()+'.pickle'))
#for a in adas:
#    print a
try:
        #print 'Running for ' + a[0].returnName() + ' and ' + a[1].returnName()
#        print 'Running for ' + a[0] + ' and ' + a[1]
    fit = lview.map_async(runFits, names)
        #fit_list.append(lview.apply_async(runFits, str(a[0].returnName()+'.pickle')))
        #fit_list.append(lview.apply_async(runFits, str(a[1].returnName()+'.pickle')))
except:
    print 'Error starting async subprocess'

print 'Wait for fitting to complete'
lview.wait(fit)
#lview.wait(fit_list)

adas2 = []
fit_list2 = fit.get()
temp = []
for i,r in enumerate(fit_list2):
    with open(r,'r') as f:
        a1 = pickle.load(f)
    temp.append(a1)
    if len(temp)==2:
        adas2.append(copy.deepcopy(temp))
        temp = []
'''
for x in xrange(0,len(fit_list)):#,2):
    x1 = fit_list[x].get()
    x2 = fit_list[x+1].get()
    print x1
    print x2
    with open(x1,'r') as f:
        a1 = pickle.load(f)
    with open(x2,'r') as g:
        a2 = pickle.load(g)
    adas2.append([a1,a2])
    #adas2.append([x1,x2])
'''
bkg_name_dict = {}
print 'Looping through adas'
for a in adas2:
    print 'Time taken for fitting: ' + str(a[0].name) + ' ' +  str(a[0].elapsed)
    print 'Time taken for fitting: ' + str(a[1].name) + ' ' +  str(a[1].elapsed)
    print 'Doing plotting'
    #a[0].plotDecisionBoundaries()
    #a[1].plotDecisionBoundaries()
    roc_output = a[0].plotROC(True)  # pass True so that ROC curve data is returned, which allows both a[0] and a[1] plots to be overlaid
    a[1].plotROC(False, roc_output)
    a[0].plotBDTScores()
    a[1].plotBDTScores()
    #try:
    #    print 'Creating transformed BDT for ' + a[0].returnName() + ' and ' + a[1].returnName()
    #    tx_list.append(lview.apply_async(createHists.createTransformedBDT, a[0].twoclass_output, a[0].testingClasses, a[1].twoclass_output, a[1].testingClasses, a[0].returnName(), a[1].returnName(), a[0].bkg_name))
    #    bkg_name_dict[a[0].bkg_name]=[a[0].returnName(), a[1].returnName()]
    #except:
    #    print 'Error starting async subprocess'
print 'Wait for createTransformedBDT output'
#lview.wait(tx_list)
#for x in tx_list:
#    print x.get()
print 'done multiprocessing'
#raw_input()
