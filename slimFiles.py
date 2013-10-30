import ROOT,sys,copy
selectedFolders = ['SelectedPosMuTrig','SelectedNegMuTrig', 'SelectedPosElTrig', 'SelectedNegElTrig']

log = open('log_slimmedout.txt','w')
inFile = ROOT.TFile(sys.argv[1],'READ')
inFile_curr = ''
outFile = ROOT.TFile(str(sys.argv[1]+'_slimmed.root'),'RECREATE')
all_xsec = {}


def stripPID(pid):
    if pid.isdigit():
        return pid
    new_pid = ''
    for x in pid:
        if x.isdigit():
            new_pid+=x
    return new_pid

def getXSec(pid):
    #strip non-integer parts off pid
    new_pid = stripPID(pid)
    if all_xsec:
        return all_xsec[new_pid]
    f = open('2012_hcp_cross_sections.txt','r')
    for line in f:
        line_arr = line.split('|')
        if len(line_arr) == 7:
            for i in xrange(len(line_arr)):
                line_arr[i] = line_arr[i].strip()
            all_xsec[str(line_arr[0]).strip()] = line_arr[1:]
    f.close()
    return all_xsec[new_pid]

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

def readPIDs(dirIn, pid):
    global inFile,outFile,inFile_curr
    inFile_curr = copy.deepcopy(dirIn.GetName())
    for key in dirIn.GetListOfKeys():
        entries = 0
        cl_name = dirIn.Get(key.GetName()).ClassName()
        if key.GetName().find("pid") != -1:
            #print 'found pid'
            pid = key.GetName()
            print pid
            #chain = ROOT.TChain('Ntuple')
            treelist = ROOT.TList()
            combineTrees(dirIn.Get(key.GetName()), key.GetName(), treelist)
            outFile.cd()
            outFile.mkdir(pid)
            outFile.cd(pid)
            mergeTree = ROOT.TTree.MergeTrees(treelist)#.Write()
            # add new branch with xsec and pid
            xsec = getXSec(pid)
            new_pid = stripPID(pid)
            varStruct = Vars()
            outTree = mergeTree.CloneTree(0)
            outTree.Branch('xsec', ROOT.AddressOf(varStruct, 'xsec'), 'xsec')
            outTree.Branch('pid', ROOT.AddressOf(varStruct, 'pid'), 'pid')
            # Loop through all entries and add values
            # Need to set entries, says Rob
            outTree.SetEntries(mergeTree.GetEntries())
            varStruct.xsec = xsec
            varStruct.pid = pid
            for i in xrange(size):
                outTree.Fill()
            outTree.Write()
            print inFile_curr
            inFile.cd(inFile_curr)
        elif cl_name == 'TDirectoryFile':
            readPIDs(dirIn.Get(key.GetName()),pid)


if __name__ == '__main__':
    # ProcessLine for adding xsec and pid
    gROOT.ProcessLine(\
        "struct Vars{\
        Float_t xsec;\
        Int_t pid;\
        };")
    
    readPIDs(inFile, '')
    inFile.Close()
    outFile.Close()
    log.close()
