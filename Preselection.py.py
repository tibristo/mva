#!/usr/bin/env python

# Author:      T. Bristow (Edinburgh) <Timothy.Michael.Bristow@cern.ch>

# Usage:
#  python Preselection.py.py file1.root sampleType

import copy
import ROOT

from ROOT import *
import sys

import math
import warnings
import numpy as np
warnings.filterwarnings('ignore')
import readMethods as read
import cutsTypes as cut


cuts = [['mcTypeVeto',0],['looseLeptonMin1',0],['WHSignalLepton',0],['looseLeptonVeto',0],['Trigger',0],['TriggerMatched',0],['metVeto',0],['mTWlowCut',0],['mTWlt120',0],['jetMin2jets',0],['jetMin2Veto',0],['bJetMin1',0],['bJetExactly2',0],['jetVeto',0],['dRgt07ptWlt200',0],\
['dRlt34ptWlt90',0],['dRlt30ptWgt90_lt120',0],['dRlt23ptWgt120_lt160',0],['dRlt18ptWgt160_lt200',0],['dRlt14ptWgt200',0],['jet1pT',0],['pTWgt0_lt90',0],['pTWgt90_lt120',0],['pTWgt120_lt160',0],['pTWgt160_lt200',0],['pTWgt200',0],['pTWgt120',0]]

#define dataType as MC or DATA
if sys.argv[2].upper == 'DATA':
	dataType = 'data'
else:
	dataType = 'mc'

treename,branches,cutsTest = read.readXml(dataType)

print "sys.argv = ", sys.argv
if not len(sys.argv)>=2:  raise(Exception, "Must specify inputFiles as argument!")
channel = 'both'
if len(sys.argv) == 4:
	if 'EL' in str(sys.argv[3]).upper():
		channel = 'el'
	if 'MU' in str(sys.argv[3]).upper():
		channel = 'mu'
print 'channel ' + channel   
inputFiles = sys.argv[1].split(',')
print "inputFiles = ", inputFiles
ch = TChain(treename)
dict_pid = {}
for file in inputFiles:
    ch.Add(file)
    f = TFile(file)
    read.readPIDs(f, '', dict_pid)

nEntries = ch.GetEntries()
nEventsPassedSkim = 0
print "nEntries = ", nEntries

# All off first
ch.SetBranchStatus("*",0)
# Turn on just what we need
[ ch.SetBranchStatus(branchname, 1) for branchname in branches ]

# Write to new file
outFile_in = inputFiles[0].split('/')[-1]
outFile = "%s.root" % (treename+"_"+outFile_in[:outFile_in.find('.root')]+"_"+sys.argv[2]+"_"+channel)

newFile = TFile(outFile, "RECREATE")
h_n_events = ROOT.TH1D('h_n_events', '', 20, -0.5, 20.5)

maxEntries = -1
#maxEntries = 100

if (maxEntries!=-1 and nEntries>maxEntries):  nEntries = maxEntries
entryNtuple = TVectorD(1)
entryNtuple[0] = nEntries

ch_new = ch.CloneTree(0)
# need to figure out a way to do this from another module
gROOT.ProcessLine(\
    "struct Vars{\
    Float_t dRBB;\
    Float_t dEtaBB;\
    Float_t dPhiVBB;\
    Float_t dPhiLMET;\
    Float_t dPhiLBMin;\
    Float_t pTV;\
    Float_t mBB;\
    Float_t HT;\
    Float_t pTB1;\
    Float_t pTB2;\
    Float_t pTimbVH;\
    Float_t mTW;\
    Float_t pTL ;\
    Float_t MET;\
    Float_t mLL;\
    Float_t category;\
    Float_t xs;\
    Float_t xscorr1;\
    Float_t xscorr2;\
    Float_t final_xs;\
    Float_t label_code;\
    Float_t AllEntries;\
    };")


varStruct = Vars()

ch_new.Branch('dRBB',AddressOf(varStruct,'dRBB'),'dR(bb)')
ch_new.Branch('dEtaBB',AddressOf(varStruct,'dEtaBB'),'dEta(bb)')
ch_new.Branch('dPhiVBB',AddressOf(varStruct,'dPhiVBB'),'dPhi(V,bb)')
ch_new.Branch('dPhiLMET',AddressOf(varStruct,'dPhiLMET'),'dPhi(l,MET)')#1 lep only
ch_new.Branch('dPhiLBMin',AddressOf(varStruct,'dPhiLBMin'),'min dPhi(l,b)')#1 lep only, closest b
ch_new.Branch('pTV',AddressOf(varStruct,'pTV'),'pT(V)')
ch_new.Branch('mBB',AddressOf(varStruct,'mBB'),'mbb')
ch_new.Branch('HT',AddressOf(varStruct,'HT'),'HT')
ch_new.Branch('pTB1',AddressOf(varStruct,'pTB1'),'pT(b1)')
ch_new.Branch('pTB2',AddressOf(varStruct,'pTB2'),'pT(b2)')
ch_new.Branch('pTimbVH',AddressOf(varStruct,'pTimbVH'),'pT imbalance VH')#[pt(bb)-pT(V)]/[pT(bb)+pT(V)]
ch_new.Branch('mTW',AddressOf(varStruct,'mTW'),'mT(W)')#1 lep only
ch_new.Branch('pTL',AddressOf(varStruct,'pTL'),'pT(l)')#1 lep only
ch_new.Branch('MET',AddressOf(varStruct,'MET'),'MET')#same as pTV for 0 lep
ch_new.Branch('mLL',AddressOf(varStruct,'mLL'),'m(ll)')#2 lep only
ch_new.Branch('category',AddressOf(varStruct,'category'),'type of event')#0, 1 or 2 lep

data = (sys.argv[2] == 'data')
if (data == False):
	ch_new.Branch('xs',AddressOf(varStruct,'xs'),'Initial Cross-Section')
	ch_new.Branch('xscorr1',AddressOf(varStruct,'xscorr1'),'Cross-Section Corr 1')
	ch_new.Branch('xscorr2',AddressOf(varStruct,'xscorr2'),'Cross-Section Corr 2')
	ch_new.Branch('final_xs',AddressOf(varStruct,'final_xs'),'Final Cross-Section')
	#ch_new.Branch('label',AddressOf(varStruct,'label'),'Label')
	ch_new.Branch('label_code',AddressOf(varStruct,'label_code'),'Label Code')
	ch_new.Branch('AllEntries',AddressOf(varStruct,'AllEntries'),'All Entries')
	#ch_new.Branch('name',AddressOf(varStruct,'name'),'Name');
	#ch_new.Branch('name_code',AddressOf(varStruct,'name_code'),'Name Code');

typeCodes = [0,1,2]
if sys.argv[2] == 'bkg':
	samples,labelcodes,namecodes = read.readBkg('bkg')
elif sys.argv[2] == 'ttbar' or sys.argv[2] == 'test':
	samples,labelcodes,namecodes = read.readBkg('ttbar')
elif sys.argv[2] == 'top':
	samples,labelcodes,namecodes = read.readBkg('st')
elif sys.argv[2] == 'data':
	samples = []
	labelcodes = {}
	namecodes = {}
else:
	samples,labelcodes, namecodes = read.readSig()

labelcodesAll, namecodesAll = read.readAllLabels();


debug = False
print 'type of Sample: ' + sys.argv[2]
totalFound = 0
tightLeptons = 0
tightLeptonsPlusLoose = 0
log = open('presel'+sys.argv[2]+'_'+channel+'Log.txt','w')
entryNtuple.Write("numEntries")


print 'start looop'
cutNum = 0 #init here to stop wasting resources on reallocating memory
foundevent = False

# Turn on ttree cache: http://root.cern.ch/drupal/content/spin-little-disk-spin
#tree->SetCacheSize(10000000);
#tree->AddBranchToCache("*");
# branches here need to point to the tree branches, not just text!!!!!
branchDict = {}
ch.SetCacheSize(100000000)#100MB
cacheBranches = ['mc_channel_number','mu_type','el_type','mu_pt','mu_eta','mu_phi', 'mu_trackIso','mu_caloIso', 'mu_triggermatched', 'trigger_mu','el_pt','el_eta','el_phi', 'el_trackIso','el_caloIso','el_triggermatched','trigger_el','RunNumber']
for branchname in cacheBranches:
	branchDict[branchname] = ch.GetBranch(branchname)
	ch.AddBranchToCache(branchDict[branchname])

cut.createIndexDict(samples)

for i in range(nEntries):
	if i%1000==0:
		print "Processing event nr. %i of %i" % (i,nEntries)

	cutNum = 0	
	foundevent = False
        ch.LoadTree(i)			    
	#ch.GetEntry(i) # Need to change this to read in single branches at a time, first finalise names of branches though
        #look here http://root.cern.ch/phpBB3/viewtopic.php?f=14&t=12570
	branchDict['mc_channel_number'].GetEntry(i)
	mc_ch_num = ch.mc_channel_number
	
	if (data == False):
		okSample = cut.checkIndexOfSample(mc_ch_num)
		if not okSample:
			continue
	
	cut.addCut(cutNum,cuts)
	cutNum += 1

	h_n_events.Fill(0) # Count all events
	#count and select all leptons
	branchDict['mu_type'].GetEntry(i)
	branchDict['el_type'].GetEntry(i)
	numLep = len(ch.mu_type) + len(ch.el_type)
	numTypeMuons = [0,0,0,0]#loose, ZHmedium, WHmedium, tight
	lep1 = TLorentzVector()
	muonTLorentzMediumW = []
	muonTLorentzMediumZ = []
	muonTLorentzLoose = []
	muonTLorentzSignal = []
	lep2 = TLorentzVector()
	electronTLorentzMediumW = []
	electronTLorentzMediumZ = []
	electronTLorentzLoose = []
	electronTLorentzSignal = []
	branchDict['mu_pt'].GetEntry(i)
	numMuons = len(ch.mu_pt)
	el_triggerMatched = 0
	mu_triggerMatched = 0

	m = 0.1057
	muVec = TLorentzVector()
        branchDict['mu_trackIso'].GetEntry(i)
        branchDict['mu_caloIso'].GetEntry(i)
        branchDict['mu_eta'].GetEntry(i)
        branchDict['mu_phi'].GetEntry(i)
	branchDict['mu_triggermatched'].GetEntry(i)
	for x in xrange(0,numMuons):
		type = ch.mu_type[x]
		typeFull = cut.leptonType(type, ch.mu_trackIso[x], ch.mu_caloIso[x])
		pt = ch.mu_pt[x]/1000.0
		eta = ch.mu_eta[x]
		phi = ch.mu_phi[x]
		muVec.SetPtEtaPhiM(pt, eta, phi, m)
		if (typeFull[0]): #loose lepton
			numTypeMuons[0] += 1
			muonTLorentzLoose.append(muVec.Clone())
		if (typeFull[1]):#ZHmedium lepton
			numTypeMuons[1] += 1
			muonTLorentzMediumZ.append(muVec.Clone())
		if (typeFull[2]):#WHmedium lepton
			numTypeMuons[2] += 1
			muonTLorentzMediumW.append(muVec.Clone())
			mu_triggerMatched = ch.mu_triggermatched[x]
		if typeFull[3]:#tight lepton
			numTypeMuons[3] += 1
			muonTLorentzSignal.append(muVec.Clone())
			
	numTypeElectrons = [0,0,0,0]#loose, ZHsignal, WHsignal, WHMJ
        branchDict['el_pt'].GetEntry(i)
	numElectrons = len(ch.el_pt)
	m = 0.511/1000.0
	elVec = TLorentzVector()
	#get all electrons
        branchDict['el_trackIso'].GetEntry(i)
        branchDict['el_caloIso'].GetEntry(i)
        branchDict['el_eta'].GetEntry(i)
        branchDict['el_phi'].GetEntry(i)
        branchDict['el_triggermatched'].GetEntry(i)
	for x in xrange(0,numElectrons):
		type = ch.el_type[x]
		typeFull = cut.leptonType(type, ch.el_trackIso[x], ch.el_caloIso[x])
		pt = ch.el_pt[x]/1000.0
		eta = ch.el_eta[x]
		phi = ch.el_phi[x]
		elVec.SetPtEtaPhiM(pt,eta,phi,m)
		if (typeFull[0]):#loose lepton
			numTypeElectrons[0] += 1
			electronTLorentzLoose.append(elVec.Clone())
		if (typeFull[1]):#ZHmedium lepton
			numTypeElectrons[1] += 1
			electronTLorentzMediumZ.append(elVec.Clone())
		if (typeFull[2]):#WHmedium lepton
			numTypeElectrons[2] += 1
			electronTLorentzMediumW.append(elVec.Clone())
			el_triggerMatched = ch.el_triggermatched[x]
		if typeFull[3]:#tight lepton
			electronTLorentzSignal.append(elVec.Clone())
			numTypeElectrons[3] += 1
	
	
	eventType = [False,False,False]#0 lepton, 1 lepton, 2 lepton

	# check at least 1 loose lepton (for cutflow comparison)
	if (numTypeMuons[0] + numTypeElectrons[0] >= 1) or (numTypeMuons[2] + numTypeElectrons[2] >=1 ):
		cut.addCut(cutNum, cuts)
		cutNum += 1
	else:
		continue
	# check exactly 1 WH signal lepton (for cutflow comparison)
	# Do we use [2] or [3] for signal lepton?!
	if (numTypeMuons[2] + numTypeElectrons[2] == 1):
		cut.addCut(cutNum, cuts)
		cutNum += 1
	else:
		continue

	if (numTypeMuons[0] + numTypeElectrons[0])  == 0:#goodElectrons + goodMuons == 1:#1 tight, 0 loose
                #TODO:  check that this is right... should require exactly 1 loose lepton, is this just for stats?
		# commenting this out for now, check that eventType[1] is True
		eventType[1] = True
		if numTypeElectrons[2] == 1:
			lep1 = electronTLorentzMediumW[0]
		else:
			lep1 = muonTLorentzMediumW[0]
		# lep2 = (0,0,0,0)
	elif (numTypeMuons[0] + numTypeElectrons[0]) == 1:
		eventType[1] = True
		if numTypeElectrons[2]== 1:
			lep1 = electronTLorentzMediumW[0]
		else:
			lep1 = muonTLorentzMediumW[0]
	# check exactly 1 WH signal lepton and exactly 1 loose lepton (for cutflow comparison)
	if eventType[1] and channel == 'both':
		cut.addCut(cutNum, cuts)
		cutNum += 1
	elif eventType[1] and channel == 'el' and numTypeElectrons[2] == 1:# and numTypeMuons[0] == 0:
		cut.addCut(cutNum, cuts)
		cutNum += 1
	elif eventType[1] and channel == 'mu' and numTypeMuons[2] == 1:
		cut.addCut(cutNum, cuts)
		cutNum += 1
	# add the else here for the cutflow comparison
	else:
		continue

	if (numTypeMuons[3] + numTypeElectrons[3]) >= 1:
		tightLeptons += 1
	if (numTypeMuons[3] == 1 or numTypeElectrons[3] == 1) and numTypeElectrons[0]+numTypeMuons[0] == 0:
		tightLeptonsPlusLoose += 1
	
	if cut.noEvent(eventType):
		continue

	# *************************** Trigger *********************************
	passTrigger = False
        branchDict['RunNumber'].GetEntry(i)
	runNumber = ch.RunNumber
	if (numTypeElectrons[2] == 1):
                branchDict['trigger_el'].GetEntry(i)
		passTrigger = cut.triggerEl(ch.trigger_el, runNumber)
	else:
                branchDict['trigger_mu'].GetEntry(i)
		passTrigger = cut.triggerMu(ch.trigger_mu, runNumber)
	if passTrigger:
		cut.addCut(cutNum, cuts)
		cutNum += 1
	else:
		continue
	# *************************** Trigger Matching ************************
	passTriggerMatch = False
	if (numTypeElectrons[2] == 1):
		passTriggerMatch = cut.matchTriggerElectron(ch.trigger_el, el_triggerMatched, 1, runNumber)
	else:
		passTriggerMatch = cut.matchTriggerMuon(ch.trigger_mu, mu_triggerMatched, 1, runNumber)

	if passTriggerMatch or data:
		cut.addCut(cutNum, cuts)
		cutNum += 1
	else:
		continue
	
	# *************************** Reconstruct the jets ********************
        ch.GetEntry(i)
	numJets = len(ch.jet_pt)
	numSignalJets = 0
	numOtherJets = 0
	numOtherbJets = 0
	jet45 = False
	jet1 = TLorentzVector()
	jet2 = TLorentzVector()
	totalJetPx = 0
	totalJetPy = 0
	addJet = TLorentzVector()
	numRecoJets = 0
	if debug == True:
		print 'numJets: ' +str(numJets)
	for j in xrange(0,numJets):
		isTagged = False
		isSignal = False
		jetpt = ch.jet_pt[j]/1000.0
		jeteta = ch.jet_eta[j]
		jetphi = ch.jet_phi[j]
		jetE = ch.jet_E[j]/1000.0

		if jetpt <= 25 or math.fabs(jeteta) >= 4.5:			
			continue
		if ch.jet_flavor_weight_MV1[j] > 0.795: #
			isTagged = True

		jetVector = TLorentzVector()
		jetVector.SetPtEtaPhiM(jetpt, jeteta, jetphi, jetE)		

		if isTagged and math.fabs(jeteta) < 2.5:
			numSignalJets += 1
			isSignal = True
			if jetpt > jet1.Pt():
				jet2.SetPtEtaPhiE(jet1.Pt(), jet1.Eta(), jet1.Phi(), jet1.E())
				jet1.SetPtEtaPhiE(jetpt, jeteta, jetphi, jetE)
			elif jetpt > jet2.Pt():
				jet2.SetPtEtaPhiE(jetpt, jeteta, jetphi, jetE)

		if isTagged:
			numOtherbJets += 1		
		else:
			numOtherJets += 1

		numRecoJets += 1
		addJet = addJet+jetVector.Clone()
		totalJetPx = totalJetPx + jetVector.Px()
		totalJetPy = totalJetPy + jetVector.Py()

	if debug:
		print 'jet1 pt: ' + str(jet1.Pt())
		print 'jet2 pt: ' + str(jet2.Pt())
		print 'numsignal jets: ' + str(numSignalJets)

	# ********************** check MET *********************************
	met = ch.MET_et/1000.0
	pxmiss = -(totalJetPx + lep1.Px() + lep2.Px())
	pymiss = -(totalJetPy + lep1.Py() + lep2.Py())
	ptmiss = math.sqrt(pxmiss*pxmiss + pymiss*pymiss)
	ptmiss_phi = TMath.ATan2(pymiss, pxmiss)
	dphi_met_ptmiss = cut.dPhi(ch.MET_phi, ptmiss_phi)
	dphi_met_jet1 = cut.dPhi(ch.MET_phi, jet1.Phi())
	dphi_met_jet2 = cut.dPhi(ch.MET_phi, jet2.Phi())

	if eventType[1] and met <= 25:
		eventType[1] = False

	if cut.noEvent(eventType):
		continue
	cut.addCut(cutNum,cuts)
	cutNum = cutNum + 1

	# ********************* V variables calculation ******************

	metPhi = ch.MET_phi
	metX = (met)*math.cos(metPhi)
	metY = (met)*math.sin(metPhi)
	m_Wpt = 0
	m_Wmass = 0
	metVec = TLorentzVector()
	metVec.SetPtEtaPhiM(met, 0, metPhi, 0)
	lepVec = TLorentzVector()
	lepVec.SetPtEtaPhiM(lep1.Pt(),0,lep1.Eta(),0)
	if eventType[1]:
		m_Wet  = lep1.Et() + met
		m_Wpx  = lep1.Px() + metX
		m_Wpy  = lep1.Py() + metY
		m_Wpt  = math.sqrt(m_Wpx*m_Wpx+m_Wpy*m_Wpy)
		m_Wmass = math.sqrt(m_Wet*m_Wet-m_Wpt*m_Wpt)
		m_Wphi = TMath.ATan2(m_Wpy, m_Wpx)
		m_Wmass = (metVec+lepVec).M() # Taken from Freiburg code
		misset = TVector2()
		misset.SetMagPhi(met, metPhi)
		lepv2 = TVector2()
		lepv2.SetMagPhi(lep1.Pt(), lep1.Phi())
		m_Wpt = (misset+lepv2).Mod() # Taken from Freiburg code

	ptvArr = [met, m_Wpt, -999]#m_Zpt]
	# ********************** calculate mTW *****************************
	ptv = met
	if eventType[1]:#check mTW
		mtw = m_Wmass
		ptv = m_Wpt
		#next two if statements for cutflow comparison only
		if True:#mtw > 40:# or m_Wpt > 160:
			cut.addCut(cutNum,cuts)
			cutNum += 1
		else:
			continue
		if True: #mtw < 120: #m_Wpt > 120:
			cut.addCut(cutNum,cuts)
			cutNum += 1
		else:
			continue
		if m_Wpt < 120:
			eventType[1] = False
			# continue here for cutflow comparison
			continue
	else: # else here for cutflow comparison
		continue

        #Check jets are cool
	# The numRecoJets >= 2 and == 2 are only here for cutflow comparison
	if numRecoJets >= 2:
		cut.addCut(cutNum, cuts)
		cutNum+=1
	else:
		continue
	if numRecoJets == 2:
		cut.addCut(cutNum, cuts)
		cutNum+=1
	else:
		continue

	if numSignalJets >= 1:
		cut.addCut(cutNum, cuts)
		cutNum+=1
	else:
		continue

#does this jet1,Pt<45 cut need to be in here now?  Moved to after dR cuts
	if numSignalJets == 2:
		cut.addCut(cutNum, cuts)
		cutNum+=1
	else:
		eventType[0] = False
		eventType[1] = False
		eventType[2] = False
		continue
	if numSignalJets == 2 and numRecoJets == 2:
		cut.addCut(cutNum, cuts)
		cutNum += 1
	else:
		continue

	# ********************** jet dR *****************************
	jetdR = cut.dR(jet1.Eta(), jet1.Phi(), jet2.Eta(), jet2.Phi())
	if (eventType[1]):
		if ptvArr[1] <= 200 and jetdR <= 0.7:
			eventType[1] = False
			
	if cut.noEvent(eventType):
		continue
	cut.addCut(cutNum,cuts)
	cutNum += 1

	if debug:
		print 'passed dR cuts'

	# *************** Following is for binned W pT analysis of lnubb Signal Region ********
		# ******* Mostly for cutflow comparison, might be useful to keep *********
	if (jetdR > 0.7 and jetdR < 3.4) and m_Wpt < 90:
		cut.addCut(cutNum, cuts)
	elif jetdR < 3.0 and (m_Wpt >= 90 and m_Wpt < 120):
		cut.addCut(cutNum+1, cuts)
	elif jetdR < 2.3 and (m_Wpt >= 120 and m_Wpt < 160):
		cut.addCut(cutNum+2, cuts)
	elif jetdR < 1.8 and (m_Wpt >= 160 and m_Wpt < 200):
		cut.addCut(cutNum+3, cuts)
	elif jetdR < 1.4 and m_Wpt >= 200:
		cut.addCut(cutNum+4, cuts)
	elif jetdR > 0.7 and m_Wpt < 200:
		removethiswhendonecheckingcutflow = 'okay'
	else:
		continue
	cutNum +=5


	# ****************** Jet PT cut **************************
	if jet1.Pt() > 45:
		cut.addCut(cutNum, cuts)
		cutNum +=1 
	else:
		continue


	# ****************** pT W cuts **************************

	if m_Wpt > 0 and m_Wpt < 60:
		cut.addCut (cutNum, cuts)
	elif m_Wpt >= 60 and m_Wpt < 120:
		cut.addCut (cutNum+1, cuts)
	elif m_Wpt >= 120 and m_Wpt < 160:
		cut.addCut (cutNum+2, cuts)
	elif m_Wpt >= 160 and m_Wpt < 200:
		cut.addCut (cutNum+3, cuts)
	elif m_Wpt >= 200:
		cut.addCut (cutNum+4, cuts)
	else:
		continue
	cutNum += 5

	if ptvArr[1] < 120:
		eventType[1] = False
		
	if cut.noEvent(eventType):
		continue
	cut.addCut(cutNum,cuts)
	cutNum = cutNum + 1
	if debug:
		print 'passed jet cuts'
	
	if eventType[1]:
		foundevent = True

	if eventType[1]:
		varStruct.category = 1.0
		ptv = ptvArr[1]
	else:
		varStruct.category = -1.0
		ptv = 0
		
	if cut.noEvent(eventType):
		continue
#	cut.addCut(cutNum,cuts)
#	cutNum = cutNum + 1
	if debug:
		print 'should be an event!!!!!!'

	varStruct.dRBB = cut.dR(jet1.Eta(),jet1.Phi(),jet2.Eta(),jet2.Phi())
	if debug:
		print 'set drBB'
	varStruct.dEtaBB = math.fabs(jet1.Eta()-jet2.Eta())
	bb_phi = (jet1+jet2).Phi()
	# do we use MET_phi for vbb for 0 lepton???

	if eventType[1]:
		varStruct.dPhiVBB = cut.dPhi(m_Wphi,bb_phi)
	else:
		varStruct.dPhiVBB= -9999

	if eventType[1]:
		varStruct.dPhiLMET = cut.dPhi(lep1.Phi(),ch.MET_phi)
		dPhiLB1 = cut.dPhi(lep1.Phi(),jet1.Phi())
		dPhiLB2 = cut.dPhi(lep1.Phi(),jet2.Phi())
		varStruct.dPhiLBMin = min(dPhiLB1, dPhiLB2)
		varStruct.mTW = mtw
		varStruct.pTL  = lep1.Pt()
	else:
		varStruct.dPhiLBMin = -9999
		varStruct.dPhiLMET = -9999
		varStruct.mTW = -9999
		varStruct.pTL = -9999
	varStruct.pTV = ptv
	varStruct.mBB = (jet1+jet2).M()
	varStruct.HT = 0
	if False:#eventType[0]:
		varStruct.HT = (addJet).Et()+met
	elif eventType[1]:
		varStruct.HT = math.fabs(jet1.Pt())+math.fabs(jet2.Pt())+math.fabs(lep1.Pt()) + met

	varStruct.pTB1 = max(jet1.Pt(),jet2.Pt())
	varStruct.pTB2 = min(jet1.Pt(),jet2.Pt())
	pTBB = (jet1+jet2).Pt()
	varStruct.pTimbVH = math.fabs(pTBB-ptv)/(pTBB+ptv)
	if debug:
		print 'set pTimbVH'
	varStruct.MET = met
	if eventType[2]:
		varStruct.mLL = mll
	else:
		varStruct.mLL = -9999

	label = ''
	if (data == False):


	if (data == False):
		ind = cut.getIndexOfSample(mc_ch_num, samples)
		if ind == -1:
			continue
		varStruct.xs = float(samples[ind][1])
		varStruct.xscorr1 = float(samples[ind][2])
		varStruct.xscorr2 = float(samples[ind][3])
		varStruct.final_xs = float(samples[ind][4])
		label = copy.deepcopy(samples[ind][5])
		label_code = float(labelcodesAll[label])
		varStruct.label_code = copy.deepcopy(label_code)
		varStruct.AllEntries = float(dict_pid[str(mc_ch_num)])

	if eventType[1] and debug:
		print 'found event!'

	if(foundevent==True):
		#print 'found eventType[1]'
		nEventsPassedSkim += 1
		totalFound += 1
		log.write(label+' ' +str(varStruct.label_code)+'\n')
		ch_new.Fill()

log.close()
# use GetCurrentFile just in case we went over the (customizable) maximum file size
ch_new.GetCurrentFile().Write()
ch_new.GetCurrentFile().Close()
cut.writeCuts(treename, '_'+outFile_in[:outFile_in.find('.root')]+'_'+sys.argv[2]+'_'+channel, cuts)

final_log = open('presel'+sys.argv[2]+'_'+channel+'_Final_Log.txt','w')
final_log.write('nEntries: ' + str(nEntries)+'\n')
final_log.write('totalFound: ' + str(totalFound)+'\n')
final_log.write('tightLeptons: ' + str(tightLeptons)+'\n')
final_log.write('tightLeptonsPlusLoose: ' + str(tightLeptonsPlusLoose))
final_log.close()
