import ROOT,sys
selectedFolders = ['SelectedPosMuTrig','SelectedNegMuTrig', 'SelectedPosElTrig', 'SelectedNegElTrig']

log = open('log.txt','rw')
inFile = TFile(sys.argv[1],'READ')
inFile_curr = ''
outFile = TFile(str('slimmed_'+sys.argv[1]),'RECREATE')

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

def combineTrees(dirIn, pid, chain):xs
    for key in dirIn.GetListOfKeys():
        cl_name = dirIn.Get(key.GetName()).ClassName()
        if key.GetName() in selectedFolders:
            new_dir = dirIn.Get(key.GetName())
            print 'adding ntuple'
            tree = new_dir.Get(key.GetName()).Clone()
            tree.SetName('Ntuple')
            chain.Add(tree)
            #get the ntuple!
        if cl_name == 'TDirectoryFile':
            combineTrees(dirIn.Get(key.GetName()), pid, chain)
        elif (cl_name == 'TH1F' or cl_name == 'TH1D') and key.GetName().endswith('BaselineOneLepton'):
            getAllEntries(dirIn, key)

def readPIDs(dirIn, pid):
    global inFile,outFile,inFile_curr
    inFile_curr = dirIn
    for key in dirIn.GetListOfKeys():
        entries = 0
        if key.GetName().find("pid") != -1:
            #print 'found pid'
            pid = key.GetName()
            print pid
            chain = TChain('Ntuple')
            combineTrees(dirIn.Get(key.GetName()), key.GetName(), chain)
            outFile.mkdir(pid)
            outFile.cd(pid)
            chain.Write()
            inFile.cd(inFile_curr)
        cl_name = dirIn.Get(key.GetName()).ClassName()
        if cl_name == 'TDirectoryFile':
            readPIDs(dirIn.Get(key.GetName()),pid)

if __name__ == '__main__':
    readPIDs(inFile, '')
    inFile.Close()
    outFile.Close()
    log.close()
