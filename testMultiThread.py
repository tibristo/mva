#from multiprocessing import Process, Pipe
#import numpy
import adaBoost as ab
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



def trainBDTs(bkg_type, sig, bkg):
    #global sig,bkg
    import numpy, sortAndCut, adaBoost
    # sometimes -1 can be returned!
    # nEntries is part of the relative weighting of events, used to be included in the the XS reweighting
    nEntriesSA = 1.0/(float((sig.returnLengthTrain('A')))/float(sig.returnFullLength()))
    nEntriesSB = 1.0/(float((sig.returnLengthTrain('B')))/float(sig.returnFullLength()))
    nEntriesBA = 1.0/(float((bkg.returnTrainingBkgLength('A',bkg_type)))/float(bkg.returnTrainingFullBkgLength(bkg_type)))
    nEntriesBB = 1.0/(float((bkg.returnTrainingBkgLength('B',bkg_type)))/float(bkg.returnTrainingFullBkgLength(bkg_type)))

    # Weights here used as ratio for BDT training weights
    if bkg_type == 'bkg':
        bkg_is_nparray = False
    else:
        bkg_is_nparray = True
    try: 
        x_A, y_A, weights_A = sortAndCut.combineWeights(sig, bkg, 'A', bkg_type, True, bkg_is_nparray)
        x_B, y_B, weights_B = sortAndCut.combineWeights(sig, bkg, 'B', bkg_type, True, bkg_is_nparray)
    except:
        error = 'Caught exception whilst running combineWeights on training data'
        error += ' Bkg_type: ' + str(bkg_type)
        print error
        return error
    try:
        xtA, ytA, weightstA = sortAndCut.combineWeights(sig, bkg, 'A', bkg_type, False, bkg_is_nparray)
        xtB, ytB, weightstB = sortAndCut.combineWeights(sig, bkg, 'B', bkg_type, False, bkg_is_nparray)
    except:
        error = 'Caught exception whilst running combineWeights on testing data'
        error += ' Bkg_type: ' + str(bkg_type)
        print error
        return error
    trainWeights_A = numpy.hstack((sig.returnTrainWeights('A'), bkg.returnTrainWeights('A', bkg_type)))
    weights_A =numpy.multiply(weights_A,trainWeights_A)
    for xi in xrange(0, len(sig.returnTrainingSample('A'))):
        weights_A[xi] = 1.0*nEntriesSA
    for xii in xrange(len(sig.returnTrainingSample('A')), trainWeights_A.shape[0]):
        weights_A[xii] *= nEntriesBA

    trainWeights_B = numpy.hstack((sig.returnTrainWeights('B'), bkg.returnTrainWeights('B', bkg_type)))
    weights_B =numpy.multiply(weights_B,trainWeights_B)
    for xi in xrange(0, len(sig.returnTrainingSample('B'))):
        weights_B[xi] = 1.0*nEntriesSB
    for xii in xrange(len(sig.returnTrainingSample('B')), trainWeights_B.shape[0]):
        weights_B[xii] *= nEntriesBB
    ada1_name = bkg_type+str('_A')
    ada2_name = bkg_type+str('_A')
    ada1 = adaBoost.adaBoost(sig.returnFoundVariables(), x_A, y_A, weights_A, xtA, ytA, ada1_name, bkg_type)
    ada2 = adaBoost.adaBoost(sig.returnFoundVariables(), x_B, y_B, weights_B, xtB, ytB, ada2_name, bkg_type)
    return [ada1,ada2]
    #conn.send([ada1,ada2])
    #conn.close()


# read in samples and convert to numpy arrays
#sig = Sample.Sample('/Disk/speyside8/lhcb/atlas/tibristo/Ntuple120_sumet_sig12_FullCutflow.root','Ntuple','sig')
def createObjects(bkg_type):
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
    
    adas = trainBDTs.trainBDTs(bkg_type, sig, bkg)
    '''
    for x in adas:
        print 'running ada ' + x.name
        try:
            x.run()
        except:
            print 'run failed!'
        print 'done run'
    '''
    return adas

#@lview.parallel(block=False)

#need to multithread this
#sig_ref = p.Reference('sig')
#bkg_ref = p.Reference('bkg')

#for r in rc:
#    r['sig'] = sig
#    r['bkg'] = bkg
    #with r.sync_imports():
    #    import numpy
    #    import sortAndCut        
adas = []
labelCode_test = ['bkg']

if __name__ == '__main__':
    arlist = []
    #Need to add extra labelCode for full bkg#
    for x in labelCode_test:#labelCodes:
        #if not bkg.hasBkg(x):
        #    continue
        print 'begin process for ' + x

        arlist.append(lview.apply_async(createObjects, x))#[x,sig,bkg]))


        #parent_conn, child_conn = Pipe()
        #p = Process(target=trainBDTs, args=(child_conn,x))
        #p.start()
        #parent_conns.append(parent_conn)
        #procs.append(p)
        #child_conn.close()
    print 'Waiting for processes to finish'
    lview.wait(arlist)
    for x in arlist:
        print 'Getting next process output'
        adas.append(x.get())
    #pollVal = False
    #while not pollVal:
     #   c.poll
    #for b,c in zip(procs,parent_conns):
        #pollVal = False
        #while not pollVal:
        #    c.poll()
        #adas.append(c.recv())
        #b.join()
tx_list = []

#for r in rc:
#    r.clear()
print "save adaBoost objects to file"
import pickle
for x in adas:
    with open(str(x[0].returnName()+'_A.pickle'),'w') as f:
        pickle.dump(x[0],f)
    with open(str(x[1].returnName()+'_B.pickle'),'w') as g:
        pickle.dump(x[1],g)


print 'Looping through adas to do fitting'
fit_list = []
import runFits
for a in adas:
    print a
    try:
        print 'Running for ' + a[0].returnName() + ' and ' + a[1].returnName()
        fit_list.append(lview.apply_async(runFits.runFits, str(a[0].returnName()+'_A.pickle')))
        fit_list.append(lview.apply_async(runFits.runFits, str(a[1].returnName()+'_B.pickle')))
    except:
        print 'Error starting async subprocess'

print 'Wait for fitting to complete'
lview.wait(fit_list)

adas2 = []
for x in xrange(0,len(fit_list),2):
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
bkg_name_dict = {}
print 'Looping through adas'
for a in adas2:
    print 'Time taken for fitting: ' + str(a[0].name) + ' ' +  str(a[0].elapsed)
    print 'Time taken for fitting: ' + str(a[1].name) + ' ' +  str(a[1].elapsed)
    #print 'Time taken for fitting B: ' + str(a[1].elapsed)
    try:
        print 'Creating transformed BDT for ' + a[0].returnName() + ' and ' + a[1].returnName()
        tx_list.append(lview.apply_async(createHists.createTransformedBDT, a[0].twoclass_output, a[0].testingClasses, a[1].twoclass_output, a[1].testingClasses, a[0].returnName(), a[1].returnName(), a[0].bkg_name))
        bkg_name_dict[a[0].bkg_name]=[a[0].returnName(), a[1].returnName()]
    except:
        print 'Error starting async subprocess'
print 'Wait for createTransformedBDT output'
lview.wait(tx_list)
for x in tx_list:
    print x.get()
print 'done multiprocessing'
#raw_input()
