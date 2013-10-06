from numpy import *
from rootpy.interactive import wait
from rootpy.plotting import Canvas, Hist, Hist2D, Hist3D, Legend
from rootpy.io import root_open as ropen, DoesNotExist
from rootpy.plotting import HistStack
import ROOT
import HistoTransform_ext as ht
print 'loading files from npy'
bdt_in = load('bdt_output_scores_A.npy')
classes = load('bdt_output_classes_A.npy')
bdt_in_B = load('bdt_output_scores_B.npy')
classes_B = load('bdt_output_classes_B.npy')
    #need to assign names that follow correct naming convention
names = [ 'bkg_2tag2jet_mva', 'WlvH125_2tag2jet_mva']
bdtx_inFile_name = "bdt_inFile.root"
bdtx_inFile = ropen('bdt_inFile.root','recreate')
#for j in xrange(2):
    #bdtx_inFile_name = "bdt_inFile_"+str(j)+"of2.root"
    #bdtx_inFile = ropen('bdt_inFile_'+str(j)+'of2.root','recreate')
bdtxarr = []
bdtxarr.append([])
bdtxarr.append([])
for i in xrange(2):
    for j in xrange(2):
        bdtxarr[i].append(Hist (1000,-1,1, name=str(names[i]+'_' +str(j) + 'of2'), title=str(names[i]+'_' +str(j) + 'of2')))
        bdtxarr[i][j].fill_array(bdt_in[classes == i])
        bdtxarr[i][j].Write()
        
bdtx_inFile.close()


for count in xrange(2):
    #bdtx_tx = ht.HistoTransform("bdt_inFile_"+str(count)+"of2.root", "bdt"+str(count)+"_outFile.root")
    bdtx_tx = ht.HistoTransform("bdt_inFile.root", "bdt"+str(count)+"_outFile.root")
    bdtx_tx.transformBkgBDTs = False
    bdtx_tx.doMergeKFolds = True
    bdtx_tx.doTransformBeforeMerging = True
    subDir = bdtx_tx.addSubDirectory("")
    if count == 1:
        bdtx_tx.transformAlgorithm = 5
        bdtx_tx.setSignal(subDir, 'WlvH125')
    else:
        bdtx_tx.transformAlgorithm = 1
    bdtx_tx.addBackground(subDir, "bkg");
    
    nFold = 2
    maxUncFactor = 1
    print 'starting first run'
    bdtx_tx.addRegion(subDir, "2tag2jet_mva", 0.05 * maxUncFactor, nFold);
    bdtx_tx.run()
    print 'done first run'
    
