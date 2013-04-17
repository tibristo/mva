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

#going to need another way of making sure that cuts gets passed through.... this isn't oop yet!



def addCut(cutNum, cuts):
	cuts[cutNum][1] = cuts[cutNum][1]+1
	return cuts

def writeCuts(treename, suffix, cuts):
	outCutFile = open("%s.txt" % (treename+suffix),'w')
	for i in cuts:
		outCutFile.write(i[0] + ': '+str(i[1])+'\n')
	outCutFile.close()
	

