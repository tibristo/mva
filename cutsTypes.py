__all__ = ['cuts','getIndexOfSample','dPhi','dR','enum','addCut','noEvent','writeCuts','leptonType']
import math

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
triggerBitMET = enum('EF_xe70_noMu','EF_xe80T_tclcw_loose','EF_xe80_tclcw','EF_xe80_tclcw_loose','trigger_met_bitset_max')
triggerBitEl = enum('EF_e20_medium','EF_e22_medium','EF_e22vh_medium1','EF_e24vhi_medium1','EF_e45_medium1','EF_e60_medium1','EF_2e12Tvh_loose1','EF_e24vh_medium1','trigger_el_bitset_max')
triggerBitMu = enum('EF_mu18_MG','EF_mu18_MG_medium','EF_mu24i_tight','EF_mu36_tight','EF_2mu13','EF_mu24_tight','trigger_mu_bitset_max')


def leptonType(ltype, trkIso, caloIso):
	isLoose   = bool( trkIso < 0.1 )
	isZHTight = bool( ltype & (1 << leptonTypes.ZHsignal ) )
	isWHTight = bool( ltype & (1 << leptonTypes.WHsignal ) )
	isWHMJ    = bool(bool( ltype & (1 << leptonTypes.WHsignal_MJ ) ) and ( trkIso >= 0.1 and trkIso < 0.6 and  caloIso < 0.14))
	type = [isLoose,isZHTight,isWHTight,isWHMJ]
	return type

def checkBit(flag, bit):#flag is short
	return bool( flag & (1<<bit) )

def getPeriodData2011(runNbr):
	if (runNbr >= 177986 and runNbr <= 178109):
		return 0 #period B
	elif (runNbr >= 179710 and runNbr <= 180481):
		return 1 #period D
	elif (runNbr >= 180614 and runNbr <= 180776):
		return 2 #period E
	elif (runNbr >= 182013 and runNbr <= 182519):
		return 3 #period F
	elif (runNbr >= 182726 and runNbr <= 183462): 
		return 4 #period G
	elif (runNbr >= 183544 and runNbr <= 184169):
		return 5 #period H
	elif (runNbr >= 185353 and runNbr <= 186493):
		return 6 #period I
	elif (runNbr >= 186516 and runNbr <= 186755):
		return 7 #period J
	elif (runNbr >= 186873 and runNbr <= 187815):
		return 8 #period K
	elif (runNbr >= 188902 and runNbr <= 190343):
		return 9 #period L
	elif (runNbr >= 190503 and runNbr <= 191933):
		return 10 #period M
	
	return -1

def matchTriggerElectron(trigger_el, el_triggermatched, channel, RunNumber):
	matchtrigger = False

	if channel==0:
		return False

	if(channel==1):
		if(RunNumber > 191933) : # 2012
    
			if( checkBit(trigger_el, triggerBitEl.EF_e24vhi_medium1) and checkBit( el_triggermatched,  triggerBitEl.EF_e24vhi_medium1) ):
				matchtrigger = True

			if( checkBit(trigger_el, triggerBitEl.EF_e60_medium1) and checkBit( el_triggermatched,  triggerBitEl.EF_e60_medium1) ):
				matchtrigger = True
		else:#  2011 data
      
			period = getPeriodData2011(RunNumber);
      
			if (period >= 0 and period <= 6) : #// B-I
				if( checkBit(trigger_el, triggerBitEl.EF_e20_medium) and checkBit( el_triggermatched,  triggerBitEl.EF_e20_medium) ):
					matchtrigger = True
			elif (period <= 8) : #// J-K
				if( checkBit(trigger_el, triggerBitEl.EF_e22_medium) and checkBit( el_triggermatched,  triggerBitEl.EF_e22_medium) ):
					matchtrigger = True
			elif (period <= 10) :# // L-M
				if( checkBit(trigger_el, triggerBitEl.EF_e22vh_medium1) and checkBit( el_triggermatched,  triggerBitEl.EF_e22vh_medium1) ):
					matchtrigger = True
				if( checkBit(trigger_el, triggerBitEl.EF_e45_medium1) and checkBit( el_triggermatched,  triggerBitEl.EF_e45_medium1) ):
					matchtrigger = True
			else:
				print "WARNING: 2011 RunNumber not found!"
	return matchtrigger

def matchTriggerMuon(trigger_mu, mu_triggermatched, channel, RunNumber): 

	matchtrigger = False

	if(channel == 0):
		return False


	if(channel == 1):
		if(RunNumber > 191933):#  2012
			
			if( checkBit(trigger_mu, triggerBitMu.EF_mu24i_tight) and checkBit( mu_triggermatched,  triggerBitMu.EF_mu24i_tight) ):
				matchtrigger = True

			if( checkBit(trigger_mu, triggerBitMu.EF_mu36_tight) and checkBit( mu_triggermatched,  triggerBitMu.EF_mu36_tight) ):
				matchtrigger = True

		else: #2011 data
      
			period = getPeriodData2011(RunNumber)
			
			if (period >= 0 and period <= 6): # B-I
				if( checkBit(trigger_mu, triggerBitMu.EF_mu18_MG ) and checkBit( mu_triggermatched,  triggerBitMu.EF_mu18_MG ) ):
					matchtrigger = True
			elif (period <= 8): # J-K
				if( checkBit(trigger_mu, triggerBitMu.EF_mu18_MG_medium) and checkBit( mu_triggermatched,  triggerBitMu.EF_mu18_MG_medium) ):
					matchtrigger = True
			elif (period <= 10): # L-M
				if( checkBit(trigger_mu, triggerBitMu.EF_mu18_MG_medium) and checkBit( mu_triggermatched,  triggerBitMu.EF_mu18_MG_medium) ):
					matchtrigger = True
			else:
				print "WARNING: 2011 RunNumber not found!"
	return matchtrigger


#def triggerMET(trigger_met):
#	passedTrigger = bool( and )
#	return type

def triggerEl(trigger_el, runNumber):
	passTrigger = bool(checkBit(trigger_el, triggerBitEl.EF_e24vhi_medium1) or checkBit(trigger_el, triggerBitEl.EF_e60_medium1) or runNumber <= 191933 )
	return passTrigger

def triggerMu(trigger_mu, runNumber = 0):
	passTrigger = bool(checkBit(trigger_mu, triggerBitMu.EF_mu24i_tight) or checkBit(trigger_mu, triggerBitMu.EF_mu36_tight)or runNumber <= 191933)
	return True

def noEvent(eventArr):
	eventBool = False
	for x in eventArr:
		if x == True:
			return False
	return True

#going to need another way of making sure that cuts gets passed through.... this isn't oop yet!



def addCut(cutNum, cuts):
	cuts[cutNum][1] = cuts[cutNum][1]+1
	return cuts

def writeCuts(treename, suffix, cuts):
	outCutFile = open("%s.txt" % (treename+suffix),'w')
	for i in cuts:
		outCutFile.write(i[0] + ': '+str(i[1])+'\n')
	outCutFile.close()
	

