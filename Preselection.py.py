#!/usr/bin/env python

# Author:      T. Bristow (Edinburgh) <Timothy.Michael.Bristow@cern.ch>

# Usage:
#  python Preselection.py.py file1.root sampleType

import copy
import ROOT
import math
import warnings
import numpy as np
warnings.filterwarnings('ignore')
#return iter->second.final_xsection*m_lumi/iter->second.nevents;
def readBkg(bkgFile):
	filename = 'SampleInfo'+bkgFile+'.csv'
	labelfilename = 'Labels'+bkgFile+'.txt'
	namesfilename = 'Names'+bkgFile+'.txt'
	labelfile = open(labelfilename,'w')
	namesfile = open(namesfilename,'w')
	f = open(filename)
	ids = []
	labelcodes = {}
	namescodes = {}
	genericBkg = (bkgFile == 'bkg')
	for line in f:
		if genericBkg:
			linearr = line.split(',')
			ids.append(linearr)
			if (linearr[5] not in labelcodes.keys()):
				label = linearr[5].strip()
				labelcodes[label] = len(labelcodes)
				labelfile.write(label+','+str(labelcodes[label]))
			if (linearr[6] not in namescodes.keys()):
				name = linearr[6].strip()
				namescodes[name] = len(namescodes)
				namesfile.write(name+','+str(namescodes[name]))
		else:
			linearr = line.split(',')
			if linearr[5] == bkgFile:
				ids.append(linearr)
			if (linearr[5] not in labelcodes.keys()):
				label = linearr[5].strip()
				labelcodes[label] = len(labelcodes)
				labelfile.write(label+','+str(labelcodes[label]))
			if (linearr[6] not in namescodes.keys()):
				name = linearr[6].strip()
				namescodes[name] = len(namescodes)
				namesfile.write(name+','+str(namescodes[name]))
	labelfile.close()
	namesfile.close()
	f.close()
	return ids, labelcodes, namescodes

def readAllLabels():
	f = open('SampleInfo.csv')
	labelfilename = 'Labels.txt'
	namesfilename = 'Names.txt'
	labelfile = open(labelfilename,'w')
	namesfile = open(namesfilename,'w')
	namescodes = {}
	labelcodes = {}
	for line in f:
		linearr = line.split(',')
		if (linearr[5] not in labelcodes.keys()):
			label = linearr[5].strip()
			labelcodes[label] = len(labelcodes)
			labelfile.write(label+','+str(labelcodes[label]))
		if (linearr[6] not in namescodes.keys()):
			name = linearr[6].strip()
			namescodes[name] = len(namescodes)
			namesfile.write(name+','+str(namescodes[name]))
	f.close()
	labelfile.close()
	namesfile.close()
	return labelcodes, namescodes


def readSig():
	f = open('SampleInfoSig.csv')
	labelfilename = 'LabelsSig.txt'
	namesfilename = 'NamesSig.txt'
	labelfile = open(labelfilename,'w')
	namesfile = open(namesfilename,'w')
	ids = []
	namescodes = {}
	labelcodes = {}
	for line in f:
		linearr = line.split(',')
		ids.append(linearr)
		if (linearr[5] not in labelcodes.keys()):
			label = linearr[5].strip()
			labelcodes[label] = len(labelcodes)
			labelfile.write(label+','+str(labelcodes[label]))
		if (linearr[6] not in namescodes.keys()):
			name = linearr[6].strip()
			namescodes[name] = len(namescodes)
			namesfile.write(name+','+str(namescodes[name]))
	f.close()
	labelfile.close()
	namesfile.close()
	return ids,labelcodes, namescodes

def getIndexOfSample(mc, sample):
	for x in xrange(0,len(sample)):
		#print int(sample[x][0])
		#print 'mc ' + str(mc)
		if int(sample[x][0]) == int(mc):
			#print 'found'
			return x
	return -1

def dPhi(phi1, phi2):
	if phi1 > math.pi:
		phi1 = phi1 - 2*math.pi
	if phi2 > math.pi:
		phi2 = phi2 - 2*math.pi
	dphi = math.fabs(phi1 - phi2)
	if (dphi > math.pi):
		dphi = 2*math.pi - dphi
	return dphi
	
def dR(eta1, phi1, eta2, phi2):
	dphi = dPhi(phi1, phi2)
	deta = math.fabs(eta1 - eta2)
	dr = math.sqrt(deta*deta + dphi*dphi)
	return dr
	
def enum(*sequential, **named):
	enums = dict(zip(sequential, range(len(sequential))), **named)
	return type('Enum', (), enums)


leptonTypes = enum('Sign','WHsignal','ZHsignal','WHsignal_MJ','lepton_type_bitset_max')
	
def leptonType(ltype, trkIso, caloIso):
	isLoose   = bool( trkIso < 0.1 )
	isZHTight = bool( ltype & (1 << leptonTypes.ZHsignal ) )
	isWHTight = bool( ltype & (1 << leptonTypes.WHsignal ) )
	isWHMJ    = bool(bool( ltype & (1 << leptonTypes.WHsignal_MJ ) ) and ( trkIso >= 0.1 and trkIso < 0.6 and  caloIso < 0.14))
	type = [isLoose,isZHTight,isWHTight,isWHMJ]
	return type

def noEvent(eventArr):
	eventBool = False
	for x in eventArr:
		if x == True:
			return False
	return True

cuts = [['mcTypeVeto',0],['leptonVeto',0],['jetCuts',0],['pTveto1',0],['metVeto',0],['massVeto',0],['pTveto2',0]]

def addCut(cutNum):
	global cuts
	cuts[cutNum][1] = cuts[cutNum][1]+1

def writeCuts():
	global cuts
	outCutFile = open("%s.txt" % (treename+sys.argv[2]),'w')
	for i in cuts:
		outCutFile.write(i[0] + ': '+str(i[1])+'\n')
	outCutFile.close()



treename = 'Ntuple'
branches = [ # Run Information
    'EventNumber',
'datastream',
'VpT_truth',
'MET_et',
'MET_phi',
'MET_et_noMuon',
'MET_sumet',
'MET_Track_sumet',
'MET_Track_et',
'MET_Track_phi',
'Trigger',
'trigger_met',
'trigger_el',
'trigger_mu',
'RunNumber',
'vxp_n_selected',
'mu_pt',
'mu_eta',
'mu_phi',
'mu_type',
'mu_triggermatched',
'mu_trackIso',
'mu_caloIso',
'el_pt',
'el_eta',
'el_phi',
'el_type',
'el_triggermatched',
'el_trackIso',
'el_caloIso',
'jet_pt',
'jet_eta',
'jet_phi',
'jet_E',
'jet_corrected_pt',
'jet_corrected_eta',
'jet_corrected_phi',
'jet_corrected_E',
'jet_jvtxf',
'jet_flavor_weight_MV1',
'jet_flavor_truth_label',
'jet_flavor_truth_hadron_label',
'jetBTAGproperties',
'weight_total',
'weight_PU',
'weight_MC',
'weight_zvtx',
'weight_MET',
'weight_lepton1',
'weight_lepton2',
'weight_lepton1_var',
'weight_lepton2_var',
'weight1or2Tag',
'weight2Tag',
'weightbTagDT',
'mc_channel_number',

            ]


from ROOT import *
import sys

print "sys.argv = ", sys.argv
if not len(sys.argv)>=2:  raise(Exception, "Must specify inputFiles as argument!")
   
inputFiles = sys.argv[1].split(',')
print "inputFiles = ", inputFiles
ch = TChain(treename)
for file in inputFiles:
    ch.Add(file)

nEntries = ch.GetEntries()
nEventsPassedSkim = 0
print "nEntries = ", nEntries

# All off first
ch.SetBranchStatus("*",0)

# Turn on just what we need
[ ch.SetBranchStatus(branchname, 1) for branchname in branches ]

# Write to new file
outFile = "%s.root" % (treename+sys.argv[2])
#outFile = "/Users/katharine/Documents/Work/MSSMAtautau/Data/MSSMA200tautaulh.SlimmedD3PD.root"
newFile = TFile(outFile, "RECREATE")
h_n_events = ROOT.TH1D('h_n_events', '', 20, -0.5, 20.5)

maxEntries = -1
#maxEntries = 100

if (maxEntries!=-1 and nEntries>maxEntries):  nEntries = maxEntries
entryNtuple = TVectorD(1)
entryNtuple[0] = nEntries

ch_new = ch.CloneTree(0)
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
    };")

'''
dRBB = np.zeros(1, dtype=float)
dEtaBB = np.zeros(1, dtype=float)
dPhiVBB = np.zeros(1, dtype=float)
dPhiLMET = np.zeros(1, dtype=float)
dPhiLBMin = np.zeros(1, dtype=float)
pTV = np.zeros(1, dtype=float)
mBB = np.zeros(1, dtype=float)
HT = np.zeros(1, dtype=float)
pTB1 = np.zeros(1, dtype=float)
pTB2 = np.zeros(1, dtype=float)
pTimbVH = np.zeros(1, dtype=float)
mTW = np.zeros(1, dtype=float)
pTL  = np.zeros(1, dtype=float)
MET = np.zeros(1, dtype=float)
mLL = np.zeros(1, dtype=float)
category = np.zeros(1, dtype=float)
category[0] = -1
'''
varStruct = Vars()
'''
ch_new.Branch('dRBB',dRBB,'dR(bb)')
ch_new.Branch('dEtaBB',dEtaBB,'dEta(bb)')
ch_new.Branch('dPhiVBB',dPhiVBB,'dPhi(V,bb)')
ch_new.Branch('dPhiLMET',dPhiLMET,'dPhi(l,MET)')#1 lep only
ch_new.Branch('dPhiLBMin',dPhiLBMin,'min dPhi(l,b)')#1 lep only, closest b
ch_new.Branch('pTV',pTV,'pT(V)')
ch_new.Branch('mBB',mBB,'mbb')
ch_new.Branch('HT',HT,'HT')
ch_new.Branch('pTB1',pTB1,'pT(b1)')
ch_new.Branch('pTB2',pTB2,'pT(b2)')
ch_new.Branch('pTimbVH',pTimbVH,'pT imbalance VH')#[pt(bb)-pT(V)]/[pT(bb)+pT(V)]
ch_new.Branch('mTW',mTW,'mT(W)')#1 lep only
ch_new.Branch('pTL',pTL,'pT(l)')#1 lep only
ch_new.Branch('MET',MET,'MET')#same as pTV for 0 lep
ch_new.Branch('mLL',mLL,'m(ll)')#2 lep only
ch_new.Branch('category',category,'type of event')#0, 1 or 2 lep
'''
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
#if (data == False):
ch_new.Branch('xs',AddressOf(varStruct,'xs'),'Initial Cross-Section')
ch_new.Branch('xscorr1',AddressOf(varStruct,'xscorr1'),'Cross-Section Corr 1')
ch_new.Branch('xscorr2',AddressOf(varStruct,'xscorr2'),'Cross-Section Corr 2')
ch_new.Branch('final_xs',AddressOf(varStruct,'final_xs'),'Final Cross-Section')
	#ch_new.Branch('label',AddressOf(varStruct,'label'),'Label')
ch_new.Branch('label_code',AddressOf(varStruct,'label_code'),'Label Code')
	#ch_new.Branch('name',AddressOf(varStruct,'name'),'Name');
	#ch_new.Branch('name_code',AddressOf(varStruct,'name_code'),'Name Code');
print 'data is false'


typeCodes = [0,1,2]
if sys.argv[2] == 'bkg':
	samples,labelcodes,namecodes = readBkg('bkg')
elif sys.argv[2] == 'ttbar' or sys.argv[2] == 'test':
	samples,labelcodes,namecodes = readBkg('ttbar')
elif sys.argv[2] == 'top':
	samples,labelcodes,namecodes = readBkg('st')
elif sys.argv[2] == 'data':
	samples = []
	labelcodes = {}
	namecodes = {}
else:
	samples,labelcodes, namecodes = readSig()
labelcodesAll, namecodesAll = readAllLabels();

#print samples
debug = False
print 'type of Sample: ' + sys.argv[2]
totalFound = 0
tightLeptons = 0
tightLeptonsPlusLoose = 0
log = open('presel'+sys.argv[2]+'Log.txt','w')
entryNtuple.Write("numEntries")
print 'start looop'
for i in range(nEntries):
	foundevent = False
	ch.GetEntry(i)
	
	cutNum = 0
	if (data == False):
		ind = getIndexOfSample(ch.mc_channel_number, samples)
		
		if ind == -1:
			continue
	
	addCut(cutNum)
	cutNum = cutNum + 1
	if i%1000==0:
		print "Processing event nr. %i of %i" % (i,nEntries)

	h_n_events.Fill(0) # Count all events
	#count and select all leptons
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
	numMuons = len(ch.mu_pt)
	goodMuons = 0
	#if debug == True:
	#	print 'numMuons: ' +str(numMuons)
	#get all muons
	for x in xrange(0,numMuons):
		type = ch.mu_type[x]
		typeFull = leptonType(type, ch.mu_trackIso[x], ch.mu_caloIso[x])
		pt = ch.mu_pt[x]/1000.0
		eta = ch.mu_eta[x]
		phi = ch.mu_phi[x]
		m = 0.1057
		muVec = TLorentzVector()
		muVec.SetPtEtaPhiM(pt, eta, phi, m)
		if (typeFull[0]): #loose lepton
			numTypeMuons[0] = numTypeMuons[0] + 1
			muonTLorentzLoose.append(muVec.Clone())
			goodMuons = goodMuons+1
		if (typeFull[1]):#ZHmedium lepton
			numTypeMuons[1] = numTypeMuons[1] + 1
			muonTLorentzMediumZ.append(muVec.Clone())
			goodMuons = goodMuons+1
		if (typeFull[2]):#WHmedium lepton
			numTypeMuons[2] = numTypeMuons[2] + 1
			muonTLorentzMediumW.append(muVec.Clone())
			goodMuons = goodMuons+1
		if typeFull[3]:#tight lepton
			numTypeMuons[3] = numTypeMuons[3] + 1
			muonTLorentzSignal.append(muVec.Clone())
			goodMuons = goodMuons+1
			
	numTypeElectrons = [0,0,0,0]#loose, ZHmedium, WHmedium, tight

	numElectrons = len(ch.el_pt)
	#if debug == True:
	#	print 'numElectrons: ' +str(numElectrons)
	goodElectrons = 0
	#get all electrons
	for x in xrange(0,numElectrons):
		type = ch.el_type[x]
		typeFull = leptonType(type, ch.el_trackIso[x], ch.el_caloIso[x])
		#print 'typeFullElectrons ' + str(typeFull)
		pt = ch.el_pt[x]/1000.0
		#print 'pt: ' + str(pt)
		eta = ch.el_eta[x]
		phi = ch.el_phi[x]
		m = 0.511/1000.0
		elVec = TLorentzVector()
		elVec.SetPtEtaPhiM(pt,eta,phi,m)
		if (typeFull[0]):#loose lepton
			numTypeElectrons[0] = numTypeElectrons[0] + 1
			electronTLorentzLoose.append(elVec.Clone())
			goodElectrons = goodElectrons + 1
		if (typeFull[1]):#medium lepton
			numTypeElectrons[1] = numTypeElectrons[1] + 1
			electronTLorentzMediumZ.append(elVec.Clone())
			goodElectrons = goodElectrons + 1
		if (typeFull[2]):#medium lepton
			numTypeElectrons[2] = numTypeElectrons[2] + 1
			electronTLorentzMediumW.append(elVec.Clone())
			goodElectrons = goodElectrons + 1
		if typeFull[3]:#tight lepton
			electronTLorentzSignal.append(elVec.Clone())
			numTypeElectrons[3] = numTypeElectrons[3] + 1
			goodElectrons = goodElectrons + 1
	
	
	eventType = [False,False,False]#0 lepton, 1 lepton, 2 lepton
	#check 0 lep
	
	# but can this not be 0 lep and 1 lep?
	'''
	if debug:
		print 'numLooseLeptons: ' + str(numTypeElectrons[0] + numTypeMuons[0])
		print 'numMediumZLeptons: ' + str(numTypeElectrons[1] + numTypeMuons[1])
		print 'numMediumWLeptons: ' + str(numTypeElectrons[2] + numTypeMuons[2])
		print 'numTightLeptons: ' + str(numTypeElectrons[3] + numTypeMuons[3])
	'''
	# not looking for eventType[0] or [2] right now..... stop if statements for now
	#f numTypeMuons[0] + numTypeElectrons[0]  == 0 and goodElectrons + goodMuons == 0:#no loose leptons
	#	eventType[0] = True
	if (numTypeMuons[3] + numTypeElectrons[3])  == 1 and  (numTypeMuons[0] + numTypeElectrons[0])  == 0:#goodElectrons + goodMuons == 1:#1 tight, 0 loose
		eventType[1] = True
		if numTypeElectrons[3] == 1:
			lep1 = electronTLorentzSignal[0]
		else:
			lep1 = muonTLorentzSignal[0]
		# lep2 = (0,0,0,0)
	if (numTypeMuons[2] + numTypeElectrons[2]) == 1 and (numTypeMuons[0] + numTypeElectrons[0]) == 1:
		eventType[1] = True
		if numTypeElectrons[2]== 1:
			lep1 = electronTLorentzMediumW[0]
		else:
			lep1 = muonTLorentzMediumW[0]
	'''
	if numTypeMuons[1] + numTypeMuons[0]  == 2 and numTypeMuons[1] == 1 and goodElectrons + goodMuons == 2:# 1 medium, 1 loose
	 	eventType[2] = True
		lep1 = muonTLorentzMediumZ[0]
		lep2 = muonTLorentzLoose[0]
	elif numTypeElectrons[1] + numTypeElectrons[0]  == 2 and numTypeElectrons[1] == 1 and goodElectrons + goodMuons == 2:# 1 medium, 1 loose
		eventType[2] = True
		lep1 = electronTLorentzMediumZ[0]
		lep2 = electronTLorentzLoose[0]
	'''
	if (numTypeMuons[3] + numTypeElectrons[3]) >= 1:
		tightLeptons = tightLeptons + 1
	if (numTypeMuons[3] == 1 or numTypeElectrons[3] == 1) and numTypeElectrons[0]+numTypeMuons[0] == 0:
		tightLeptonsPlusLoose = tightLeptonsPlusLoose + 1
	

	# not interested in 0 or 2 lep right now, set these to false:
	eventType[0] = False
	eventType[2] = False


	if noEvent(eventType):
		continue
	addCut(cutNum)
	cutNum = cutNum + 1
	if debug:
		print 'passed lepton veto'
		print '0lep : ' + str(eventType[0])
		print '1lep : ' + str(eventType[1])
		print '2lep : ' + str(eventType[2])
	
	#print 'passed lepton veto'
	#check jets are cool
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
	if debug == True:
		print 'numJets: ' +str(numJets)
	for j in xrange(0,numJets):
		isTagged = False
		isSignal = False
		jetpt = ch.jet_corrected_pt[j]/1000.0
		jeteta = ch.jet_corrected_eta[j]
		jetphi = ch.jet_corrected_phi[j]
		jetE = ch.jet_corrected_E[j]/1000.0
		jetVector = TLorentzVector()
		jetVector.SetPtEtaPhiM(jetpt, jeteta, jetphi, jetE)
		if jetpt <= 25 or math.fabs(jeteta) >= 4.5:			
			continue
		if ch.jet_flavor_weight_MV1[j] > 0.795: #
			isTagged = True
		
		if isTagged and math.fabs(jeteta) < 2.5:
			numSignalJets = numSignalJets + 1
			isSignal = True
			if jetpt > jet1.Pt():
				jet2.SetPtEtaPhiE(jet1.Pt(), jet1.Eta(), jet1.Phi(), jet1.E())
				jet1.SetPtEtaPhiE(jetpt, jeteta, jetphi, jetE)
			elif jetpt > jet2.Pt():
				jet2.SetPtEtaPhiE(jetpt, jeteta, jetphi, jetE)

		if isTagged:
			numOtherbJets = numOtherbJets + 1
		
		else:
			numOtherJets = numOtherJets + 1
		addJet = addJet+jetVector.Clone()
		totalJetPx = totalJetPx + jetVector.Px()
		totalJetPy = totalJetPy + jetVector.Py()

	if debug:
		print 'jet1 pt: ' + str(jet1.Pt())
		print 'jet2 pt: ' + str(jet2.Pt())
		print 'numsignal jets: ' + str(numSignalJets)
	if jet1.Pt() < 45 or numSignalJets < 2:
		eventType[0] = False
		eventType[1] = False
		eventType[2] = False
#	if numSignalJets < 2:
#		#print 'not enough signal jets'
#		continue
	
	if numOtherJets > 0:
		#print 'too many other jets'
		r =1
		#eventType[0] = False
		#eventType[1] = False
	if (numOtherbJets - numSignalJets) > 0:
		#print 'too many other b-jets'
		r= 2
		#eventType[2] = False


	if noEvent(eventType):
		continue
	addCut(cutNum)
	cutNum = cutNum + 1
	if debug:
		print 'passed jet cuts'
	#W variables calculation
	met = ch.MET_et/1000.0
	metPhi = ch.MET_phi
	metX = (met)*math.cos(metPhi)
	metY = (met)*math.sin(metPhi)
	m_Wpt = 0
	m_Wmass = 0
	if eventType[1]:
		m_Wet  = lep1.Et() + met
		m_Wpx  = lep1.Px() + metX
		m_Wpy  = lep1.Py() + metY
		m_Wpt  = math.sqrt(m_Wpx*m_Wpx+m_Wpy*m_Wpy)
		m_Wmass = math.sqrt(m_Wet*m_Wet-m_Wpt*m_Wpt)
		m_Wphi = TMath.ATan2(m_Wpy, m_Wpx)
	#Z variables calculation
	m_Zpt = 0
	if eventType[2]:
		m_Zet = lep1.Et() + lep2.Et() + met
		m_Zpx = lep1.Px() + lep2.Px() + metX
		m_Zpy = lep1.Py() + lep2.Py() + metY
		m_Zpt = math.sqrt(m_Zpx*m_Zpx + m_Zpy*m_Zpy)
		m_Zmass = math.sqrt(m_Zet*m_Zet-m_Zpt*m_Zpt)
		m_Zphi = TMath.ATan2(m_Zpy, m_Zpx)
	# check the dR for pTV < 200 GeV
	#ptv = ch.VpT_truth
	# is ptv for 0 lep case correct????
	ptvArr = [met, m_Wpt, m_Zpt]

	jetdR = dR(jet1.Eta(), jet1.Phi(), jet2.Eta(), jet2.Phi())
	for pti in xrange(1,2):
		if (eventType[pti]):
			if ptvArr[pti] <= 200 and jetdR <= 0.7:
				eventType[pti] = False
	if eventType[0] and met <= 200 and jetdR <= 0.7:
		eventType[0] = False


	if noEvent(eventType):
		continue
	addCut(cutNum)
	cutNum = cutNum + 1
	if debug:
		print 'passed dR cuts'
	#check MET:
	pxmiss = -(totalJetPx + lep1.Px() + lep2.Px())
	pymiss = -(totalJetPy + lep1.Py() + lep2.Py())
	ptmiss = math.sqrt(pxmiss*pxmiss + pymiss*pymiss)
	ptmiss_phi = TMath.ATan2(pymiss, pxmiss)
	dphi_met_ptmiss = dPhi(ch.MET_phi, ptmiss_phi)
	dphi_met_jet1 = dPhi(ch.MET_phi, jet1.Phi())
	dphi_met_jet2 = dPhi(ch.MET_phi, jet2.Phi())
	if eventType[0] and (met <= 120 or ptmiss <= 30 or dphi_met_ptmiss >= math.pi or min(dphi_met_jet1, dphi_met_jet2 )< 1.5):
		eventType[0] = False
	if eventType[1] and met <= 25:
		eventType[1] = False



	if noEvent(eventType):
		continue
	addCut(cutNum)
	cutNum = cutNum + 1
	if debug:
		print 'passed dphi cuts'
	
	# check vector boson cuts
	# calculate mTW
	
	
  

	ptv = met
	if eventType[1]:#check mTW
		mtw = m_Wmass
		ptv = m_Wpt
		if m_Wpt < 120 and mtw < 40:
			eventType[1] = False
	if eventType[2]:
		mll = (lep1 + lep2).M()
		if mll <= 71 or mll >= 121:
			eventType[2] = False

	if noEvent(eventType):
		continue
	addCut(cutNum)
	cutNum = cutNum + 1

	if debug:
		print 'passed m_Wpt or mll'
	countpt = 0
	for pt in ptvArr:
		if pt > 120:
			eventType[countpt] = False
		countpt = countpt + 1
	
	if eventType[0] or eventType[1] or eventType[2]:
		foundevent = True
	if eventType[0]:
		varStruct.category = 0.0
		ptv = ptvArr[0]
	elif eventType[1]:
		varStruct.category = 1.0
		ptv = ptvArr[1]
	elif eventType[2]:
		varStruct.category = 2.0
		ptv = ptvArr[2]
	else:
		varStruct.category = -1.0
		ptv = 0
		
	if noEvent(eventType):
		continue
	addCut(cutNum)
	cutNum = cutNum + 1
	if debug:
		print 'should be an event!!!!!!'

	varStruct.dRBB = dR(jet1.Eta(),jet1.Phi(),jet2.Eta(),jet2.Phi())
	if debug:
		print 'set drBB'
	varStruct.dEtaBB = math.fabs(jet1.Eta()-jet2.Eta())
	bb_phi = (jet1+jet2).Phi()
	# do we use MET_phi for vbb for 0 lepton???
	if eventType[0]:
		varStruct.dPhiVBB = dPhi(MET_phi,bb_phi)
	elif eventType[1]:
		varStruct.dPhiVBB = dPhi(m_Wphi,bb_phi)
	elif eventType[2]:
		varStruct.dPhiVBB = dPhi(m_Zphi,bb_phi)
	else:
		varStruct.dPhiVBB= -9999
	if eventType[1]:
		varStruct.dPhiLMET = dPhi(lep1.Phi(),ch.MET_phi)
		dPhiLB1 = dPhi(lep1.Phi(),jet1.Phi())
		dPhiLB2 = dPhi(lep1.Phi(),jet2.Phi())
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
	if eventType[0]:
		varStruct.HT = (addJet).Et()+met
	elif eventType[1]:
		varStruct.HT = (addJet+lep1).Et() + met
	elif eventType[2]:
		varStruct.HT = (lep1+lep2+addJet).Et() + met
	varStruct.pTB1 = jet1.Pt()
	varStruct.pTB2 = jet2.Pt()
	pTBB = (jet1+jet2).Pt()
	varStruct.pTimbVH = (pTBB-ptv)/(pTBB+ptv)
	if debug:
		print 'set pTimbVH'
	varStruct.MET = met
	if eventType[2]:
		varStruct.mLL = mll
	else:
		varStruct.mLL = -9999
	'''
	if eventType[0]:
		category[0] = 0	
	elif eventType[1]:
		category[0] = 1	
	elif eventType[2]:
		category[0] = 2	
	else:
		category[0] = -1
        '''
	#print samples[ind][1]
	#if (data == False):
	varStruct.xs = float(samples[ind][1])
	varStruct.xscorr1 = float(samples[ind][2])
	varStruct.xscorr2 = float(samples[ind][3])
	varStruct.final_xs = float(samples[ind][4])
	label = copy.deepcopy(samples[ind][5])
		#varStruct.label = label
		#print 'samples[ind][5].strip():' + label
	label_code = float(labelcodesAll[label])
	varStruct.label_code = copy.deepcopy(label_code)
		#print 'labelcodesAll[samples[ind][5].strip()]: ' + str(labelcodesAll[samples[ind][5]])
		#print str(varStruct.label_code)
		#varStruct.name = samples[ind][6].strip()
		#varStruct.name_code = namecodesAll[samples[ind][6].strip()]
	if eventType[0] or eventType[2]:
		if debug:
			print '0 or 1 lep event found ***********************************************'
	if eventType[1]:
		foundevent = True
		if debug:
			print 'found event!'
	else:
		foundevent = False
	if(foundevent==True):
		#print 'found eventType[1]'
		nEventsPassedSkim = nEventsPassedSkim + 1
		totalFound = totalFound + 1
		log.write(label+' ' +str(varStruct.label_code)+'\n')
		ch_new.Fill()
log.close()
	#print 'passed event!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'

#    # Check to see if it passes the vertex requirements
#    pass_vertex = False
#    for i_vertex in xrange(ch.vxp_n):
#        if ch.vxp_nTracks[i_vertex] >= 3 and abs(ch.vxp_z[i_vertex]) < 150.0 :
#            pass_vertex = True
#            break

#    # Fill histograms recording cuts
#    if pass_trigger == True :
#        h_n_events.Fill(1)

#        if pass_vertex == True :
#            h_n_events.Fill(2)

#            # Record information for events which pass all the cuts so far   
#            nEventsPassedSkim = nEventsPassedSkim + 1
#            ch_new.Fill()
    

# Print the contents
#ch_new.Print()

# use GetCurrentFile just in case we went over the (customizable) maximum file size
ch_new.GetCurrentFile().Write()
ch_new.GetCurrentFile().Close()
writeCuts()

print 'nEntries: ' + str(nEntries)
print 'totalFound: ' + str(totalFound)
print 'tightLeptons: ' + str(tightLeptons)
print 'tightLeptonsPlusLoose: ' + str(tightLeptonsPlusLoose)
