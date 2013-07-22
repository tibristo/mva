__all__ = ['readBkg','readAllLabels','readSig','readXml']
import ROOT
def readPIDs(dirIn, pid, dict_pid):
    for key in dirIn.GetListOfKeys():
        entries = 0
        if key.GetName().find("pid") != -1:
            #print 'found pid'
            pid = key.GetName()
        cl_name = dirIn.Get(key.GetName()).ClassName()
        if cl_name == 'TDirectoryFile':
            readPIDs(dirIn.Get(key.GetName()),pid, dict_pid)
        elif (cl_name == 'TH1F' or cl_name == 'TH1D') and key.GetName().endswith('BaselineOneLepton'):
            hist = dirIn.Get(key.GetName())
            foundbin = False
            for lab in hist.GetXaxis().GetLabels():
                labname = lab.GetName()
                if labname.lower().find("all")!=-1:
                    bin = hist.GetXaxis().FindBin(labname)
                    bincont = hist.GetBinContent(bin)
                    if bincont >= 1.0 and bincont%int(bincont) == 0.0:
                        entries = int(bincont)
                        foundbin = True
                        continue
                    else:
                        entries = int(bincont)
            dict_pid[pid[4:]] = entries
            pid = ''
            
    return dict_pid


def readXml(dataType):

    import xml.etree.ElementTree as ET
    xmlTree = ET.parse('settings.xml')
    root = xmlTree.getroot()

    treename = ''
    branches = []
    for child in root.findall('sampleType'):
        if child.get('name') == dataType.upper():
            for grandchild in list(child):
                if grandchild.tag == 'treeName':
                    treename = grandchild.get('name')
                elif grandchild.tag == 'branch':
                    branches.append(grandchild.get('name'))
    cuts = []
    for child in root.findall('cuts'): # all cuts
        cuts.append([child.get('name'), 0])

    return treename,branches,cuts

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
				labelfile.write(label+','+str(labelcodes[label])+'\n')
			if (linearr[6] not in namescodes.keys()):
				name = linearr[6].strip()
				namescodes[name] = len(namescodes)
				namesfile.write(name+','+str(namescodes[name])+'\n')
		else:
			linearr = line.split(',')
			if linearr[5] == bkgFile:
				ids.append(linearr)
			if (linearr[5] not in labelcodes.keys()):
				label = linearr[5].strip()
				labelcodes[label] = len(labelcodes)
				labelfile.write(label+','+str(labelcodes[label])+'\n')
			if (linearr[6] not in namescodes.keys()):
				name = linearr[6].strip()
				namescodes[name] = len(namescodes)
				namesfile.write(name+','+str(namescodes[name])+'\n')
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
			labelfile.write(label+','+str(labelcodes[label])+'\n')
		if (linearr[6] not in namescodes.keys()):
			name = linearr[6].strip()
			namescodes[name] = len(namescodes)
			namesfile.write(name+','+str(namescodes[name])+'\n')
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
			labelfile.write(label+','+str(labelcodes[label])+'\n')
		if (linearr[6] not in namescodes.keys()):
			name = linearr[6].strip()
			namescodes[name] = len(namescodes)
			namesfile.write(name+','+str(namescodes[name])+'\n')
	f.close()
	labelfile.close()
	namesfile.close()
	return ids,labelcodes, namescodes
