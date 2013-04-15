__all__ = ['readBkg','readAllLabels','readSig','readXml']

def readXml(dataType):

    import xml.etree.ElementTree as ET
    xmlTree = ET.parse('settings.xml')
    root = xmlTree.getroot()

    treename = ''
    branches = []
    for child in root.findall('sampleType'):
        if child.get('name') == dataType.upper():
            for grandchild in list(child):
                if grandchild.tag = 'treeName':
                    treename = grandchild.get('name')
                elif grandchild.tag = 'branch':
                    branches.append(grandchild.get('name'))
    return treename,branches

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
