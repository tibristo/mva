import ROOT,sys,copy
selectedFolders = ['SelectedPosMuTrig','SelectedNegMuTrig', 'SelectedPosElTrig', 'SelectedNegElTrig']

log = open(sys.argv[1]+'_slimmed_log.txt','w')
inFile = ROOT.TFile(sys.argv[1],'READ')
inFile_curr = ''
outFile = ROOT.TFile(str(sys.argv[1]+'_slimmed.root'),'RECREATE')
all_xsec = {}
ROOT.gROOT.ProcessLine(\
    "struct Vars{\
    Float_t xsec;\
    Int_t pid;\
    };")
allTrees = []
createFullSample = False

def readXml(dataType):
    '''
    Get the settings for which PIDs to combine in the combined root file.  The one to run is specified at run time and given as an arg.
    Keyword arguments:
    dataType --- The type of sample to run, AllBkg or Signal, for eg. Set PIDs for each in settings_slimming.xml

    returns a list of pids
    '''
    import xml.etree.ElementTree as ET
    xmlTree = ET.parse('settings_slimming.xml')
    root = xmlTree.getroot()

    pids = []
    for child in root.findall('sampleType'):
        if child.get('name') == dataType.upper():
            for grandchild in list(child):
                if grandchild.tag == 'pid':
                    pids.append(grandchild.get('name'))
    return pids

def stripPID(pid):
    '''
    Strip the PID identifier of any non-integer characters.
    Keyword arguments:
    pid --- The pid identifier
    
    returns stripped pid
    '''
    if pid.isdigit():
        return pid
    new_pid = ''
    for x in pid:
        if x.isdigit():
            new_pid+=x
    return new_pid

def getXSec(pid):
    '''
    Get the cross section for the sample based on the pid identifier.  The cross sections are based on the PID and come from 2012_hcp_cross_sections.txt.
    Keyword arguments:
    pid -- the PID, not necessarily only integers at this point.

    returns dictionary with stripped pid as key, list containing [Process, Generator, cross-section*BR, k-factor, name]
    '''
    #strip non-integer parts off pid
    new_pid = stripPID(pid)
    global all_xsec
    if all_xsec: #don't do it again if it's already been done!
        if new_pid in all_xsec.keys():
            return all_xsec[new_pid]
        else:
            log.write("No xsec available for "+ new_pid)
            return ['NONE','NONE',1,1,1,'NONE']
    f = open('2012_hcp_cross_sections.txt','r')
    for line in f:
        line_arr = line.split('|')
        if len(line_arr) == 7:
            for i in xrange(len(line_arr)):
                line_arr[i] = line_arr[i].strip()
            all_xsec[str(line_arr[0]).strip()] = line_arr[1:]
    f.close()
    if new_pid in all_xsec.keys():
        return all_xsec[new_pid]
    else:
        log.write("No xsec available for "+ new_pid)
        return ['NONE','NONE',1,1,1,'NONE']

def getAllEntries(dirIn, key):
    global log
    hist = dirIn.Get(key.GetName())
    entries = -1
    for lab in hist.GetXaxis().GetLabels():
        labname = lab.GetName()
        if labname.lower().find("all")!=-1:
            bin = hist.GetXaxis().FindBin(labname)
            bincont = hist.GetBinContent(bin)
            if bincont >= 1.0 and bincont%int(bincont) == 0.0:
                entries = int(bincont)
                continue
            else:
                entries = int(bincont)
    log.write(str(key.GetName()) + ' ' + str(entries))
    #return entries

def combineTrees(dirIn, pid, chain):
    for key in dirIn.GetListOfKeys():
        cl_name = dirIn.Get(key.GetName()).ClassName()
        if key.GetName() in selectedFolders:
            new_dir = dirIn.Get(key.GetName())
            print 'adding ntuple'
            print new_dir
            #tree = new_dir.Get(key.GetName()+'Ntuple').Clone()
            #tree.SetName('Ntuple')
            chain.Add(new_dir.Get(key.GetName()+'Ntuple'))#tree)
            #get the ntuple!
        elif cl_name == 'TDirectoryFile':
            combineTrees(dirIn.Get(key.GetName()), pid, chain)
        elif (cl_name == 'TH1F' or cl_name == 'TH1D') and key.GetName().endswith('BaselineOneLepton'):
            getAllEntries(dirIn, key)

def readPIDs(dirIn, pids):
    '''
    Read all the TTrees for different PIDs, traversing through all subfolders.  Recursive method, calls on itself if the current item being viewed in the pwd is a TDirectory.
    Keyword arguments:
    dirIn --- The current TDirectory.
    pid --- A list of PIDs to read in.
    '''
    global inFile,outFile,inFile_curr
    global allTrees, createFullSample
    inFile_curr = copy.deepcopy(dirIn.GetName())
    for key in dirIn.GetListOfKeys():
        entries = 0
        cl_name = dirIn.Get(key.GetName()).ClassName()
        if key.GetName().find("pid") != -1:
            pid = key.GetName()
            new_pid = stripPID(pid)
            print pid
            if pids and (not new_pid in pids):
                # Add 'continue' here since we don't want to add this!
                continue
            treelist = ROOT.TList()
            combineTrees(dirIn.Get(key.GetName()), key.GetName(), treelist)
            outFile.cd()
            mergeTree = ROOT.TTree.MergeTrees(treelist)#.Write()
            # add new branch with xsec and pid
            xsec = getXSec(pid)
            varStruct = ROOT.Vars()
            outTree = mergeTree.CloneTree(0)
            outTree.Branch('xsec', ROOT.AddressOf(varStruct, 'xsec'), 'xsec/F')
            outTree.Branch('pid', ROOT.AddressOf(varStruct, 'pid'), 'pid/I') #/I is very important!!!!
            # Loop through all entries and add values
            varStruct.xsec = float(xsec[2])*float(xsec[3])
            print new_pid
            varStruct.pid = int(copy.deepcopy(new_pid))
            print int(new_pid)
            for i in xrange(mergeTree.GetEntries()):
                mergeTree.GetEntry(i)
                outTree.Fill()
            outTree.SetName('Ntuple_'+str(pid))
            if createFullSample:
                allTrees.append(outTree.Clone())
            outTree.Write()
            print inFile_curr
            inFile.cd(inFile_curr)
        elif cl_name == 'TDirectoryFile':
            readPIDs(dirIn.Get(key.GetName()),pids)


if __name__ == '__main__':
    # ProcessLine for adding xsec and pid
    pids = []
    if sys.argc == 3:
        pids = readXml(sys.argv[2])
        createFullSample = True
    readPIDs(inFile, '', pids)
    outFile.Close()

    # do this before closing input file
    if createFullSample:
        #loop through allTrees and add to TList
        finalList = ROOT.TList()
        for tree in allTrees:
            finalList.Add(tree)
        finalTree = ROOT.TTree.MergeTrees(finalList)
        fullSampleFile = ROOT.TFile(str(sys.argv[1]+'_fullsample_'+sys.argv[2]+'.root'),'RECREATE')
        finalTree.Write()
        fullSampleFile.Close()

    inFile.Close()
    log.close()


