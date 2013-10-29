#include <HistoTransform.h>
#include <math.h>
using namespace boost::python;

// PRIVATE

// get a vector of bins where to rebin to get an uncertainty <= 5% per bin.
// starting from highest bin!
// the numbers give the lowest bin included in the new bin
// overflowbin+1 and underflow bins are returned as the first and last element in the vector, respectively.


HistoTransform::HistoTransform(const std::string inFileName, const std::string outFileName)
{

  m_inFileName = TString(inFileName);
  m_outFileName = TString(outFileName);

    cout << "INFO: reading from file '" << m_inFileName.Data() << "'" << endl;
    m_inFile = new TFile(m_inFileName, "read");
    if (!m_inFile -> IsOpen()) {
      gSystem -> Exit(1);
    }

    if (m_outFileName == "") {
      m_outFileName = m_inFileName;
      m_outFileName.ReplaceAll(".root", ".transformed.root");
    }
    cout << "INFO: writing to file '" << m_outFileName.Data() << "'" << endl;
    m_outFile = new TFile(m_outFileName, "recreate");

    doMergeKFolds = true;
    doTransformBeforeMerging = false;
    transformAlgorithm = 1;
    trafoFiveY = 5.;
    trafoSixY = 10.;
    trafoSixZ = 10.;
    trafoSevenNBins = 20;
    trafoEightRebin = 20;
    transformBkgBDTs = true;

}


vector<int> HistoTransform::getRebinBins(TH1* histoBkg, TH1* histoSig, int method, double maxUnc) {

  vector<int> bins;
  bins.clear();

  int nBins = histoBkg -> GetNbinsX();
  int iBin = nBins + 1; // start with overflow bin
  bins.push_back(nBins + 2);

  float nBkg = histoBkg -> Integral(0, nBins + 1);
  float nSig = 0;
  if (histoSig)
    nSig = histoSig -> Integral(0, nBins + 1);
  
  while (iBin > 0) {

    double sumBkg = 0;
    double sumSig = 0;
    double err2Bkg = 0;
    bool pass = false;
    int binCount = 1;

    while (!pass && iBin >= 0) {
      sumBkg += histoBkg -> GetBinContent(iBin);
      if (histoSig)
        sumSig += histoSig -> GetBinContent(iBin);
      err2Bkg += pow(histoBkg -> GetBinError(iBin), 2);

      double err2RelBkg = 1;
      if (sumBkg != 0) {
        err2RelBkg = err2Bkg / pow(sumBkg, 2);
      }

      float err2Rel = 1;
      float err2MaxBkg = pow(maxUnc, 2);

      switch (method) {
        case 1:
          // METHOD 1 : err(Bkg) < XX%
          pass = sqrt(err2RelBkg) < maxUnc;
          break;
        case 5:
          if (!histoSig) {
            cout << "ERROR: signal histogram needed for transformation method '" << method << "'!" << endl;
            gSystem -> Exit(1);
          }
          if (sumBkg != 0 && sumSig != 0)
            err2Rel = 1 / (err2MaxBkg / err2RelBkg + sumSig / (nSig / trafoFiveY));
          else if (sumBkg != 0)
            err2Rel = err2RelBkg / err2MaxBkg;
          else if (sumSig != 0)
            err2Rel = (nSig / trafoFiveY) / sumSig;
          pass = sqrt(err2Rel) < 1;
          break;
        case 6:
          if (!histoSig) {
            cout << "ERROR: signal histogram needed for transformation method '" << method << "'!" << endl;
            gSystem -> Exit(1);
          }
          if (sumBkg != 0 && sumSig != 0)
            err2Rel = 1 / (sumBkg / (nBkg / trafoSixZ) + sumSig / (nSig / trafoSixY));
          else if (sumBkg != 0)
            err2Rel = (nBkg / trafoSixZ) / sumBkg;
          else if (sumSig != 0)
            err2Rel = (nSig / trafoSixY) / sumSig;
          pass = sqrt(err2Rel) < 1;
          break;
        case 7:
          pass = sumBkg > nBkg / trafoSevenNBins;
          break;
        case 8:
          pass = (binCount >= trafoEightRebin);
          break;
        default:
          cout << "ERROR: transformation method '" << method << "' unknown!" << endl;
          gSystem -> Exit(1);
          break;
      }
      binCount++;
      iBin--;
    }
    // remove last bin
    if (iBin + 1 == 0 && bins.size() > 1)
      if (method != 6 && method != 7)
        bins.pop_back();
    bins.push_back(iBin + 1);
  }

  return bins;
}
BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(getRebinOverloads, getRebinBins, 3,4)
// rebin histogram with provided vector of bins

void HistoTransform::rebinHisto(TH1* histo, vector<int>* bins) {

  TH1* histoOld = (TH1*) histo -> Clone();
  histo -> Reset();
  int newNBins = bins -> size() - 1;
  histo -> SetBins(newNBins, -1, 1);

  for (int iBinNew = 1; iBinNew <= newNBins; iBinNew++) {
    int iBinLow = bins -> at(newNBins - iBinNew + 1); // vector is reverse-ordered
    int iBinHigh = bins -> at(newNBins - iBinNew) - 1;

    double err = 0;
    double sum = histoOld -> IntegralAndError(iBinLow, iBinHigh, err);
    histo -> SetBinContent(iBinNew, sum);
    histo -> SetBinError(iBinNew, err);
  }
  int oldNbins = histoOld -> GetNbinsX();
  double diff = 1 - histo -> Integral(0, newNBins + 1) / histoOld -> Integral(0, oldNbins + 1);
  //  double diff = 1 - histo -> GetSumOfWeights() / histoOld -> GetSumOfWeights();
  if (TMath::Abs(diff) > 1e-7) {
    cout << "WARNING: sizeable difference in tranformation of '" << histo -> GetName() << "' found. Integrals: (old-new)/old = " << diff << endl;
  }
  delete histoOld;
}

void HistoTransform::readRebinBins(SubDirectory* subDir) {
  for (unsigned int iKFold = 0; iKFold < subDir -> kFolds.size(); iKFold++) {
    KFold* kFold = subDir -> kFolds[iKFold];
    for (unsigned int iRegion = 0; iRegion < kFold -> regions.size(); iRegion++) {
      Region* region = kFold -> regions[iRegion];
      cout << "INFO: building transformation for region '" << region -> name << "':";
      region -> bins = getRebinBins(region -> bkg, region -> sig, transformAlgorithm, region -> maxUnc);
      cout << " Nbins = " << region -> bins.size() - 1 << endl;
    }
  }
}

HistoTransform::KFold* HistoTransform::getKFold(SubDirectory* subDir, string histName) {
  for (unsigned int iKFold = 0; iKFold < subDir -> kFolds.size(); iKFold++) {
    KFold* kFold = subDir -> kFolds[iKFold];
    if (kFold -> name == getRegionName(histName))
      return kFold;
  }
  //  cout << "WARNING: kFold for histo '" << histName << "' not found!" << endl;
  return 0;
}

HistoTransform::Region* HistoTransform::getRegion(SubDirectory* subDir, string histName) {
  KFold* kFold = getKFold(subDir, histName);
  if (!kFold)
    return 0;
  if (kFold -> regions.size() == 1)
    return kFold -> regions[0];
  TString name = histName;
  for (unsigned int iRegion = 0; iRegion < kFold -> regions.size(); iRegion++) {
    TString stringIofK = TString::Format("_%iof%i", iRegion, (int) kFold -> regions.size());
    if (name.Contains(stringIofK))
      return kFold -> regions[iRegion];
  }
  //  cout << "WARNING: region for histo '" << histName << "' not found!" << endl;
  return 0;
}

bool HistoTransform::isFirstOfKFold(KFold* kFold, string histName) {
  if (!kFold)
    return false;
  TString string0ofK = TString::Format("_0of%i", (int) kFold -> regions.size());
  TString name = histName.c_str();
  if (name.Contains(string0ofK))
    return true;
  return false;
}

// go recursively through directories in source.
// rebin all histos found on the way and save same to gDirectory.

void HistoTransform::rebinAllHistos(TDirectory* source, SubDirectory* subDir) {
  TDirectory* savdir = gDirectory;
  TDirectory* adir = savdir;
  if (source != m_inFile) {
    adir = savdir -> mkdir(source -> GetName());
  }
  adir -> cd();
  //loop on all entries of this directory
  TKey* key;
  TIter nextkey(source -> GetListOfKeys());
  while ((key = (TKey*) nextkey())) {
    TClass* cl = gROOT -> GetClass(key -> GetClassName());
    if (!cl) continue;
    if (cl -> InheritsFrom(TDirectory::Class())) {
      cout << "INFO: going into directory '" << key -> GetName() << "'" << endl;
      source -> cd(key -> GetName());
      TDirectory* subdir = gDirectory;
      adir -> cd();
      rebinAllHistos(subdir, subDir);
      adir -> cd();
    } else if (cl -> InheritsFrom(TH1::Class())) {
      string name = key -> GetName();
      TH1* histo = (TH1*) source -> Get(name.c_str());
      adir -> cd();
      Region* region = getRegion(subDir, name);
      if (region) {
        //        cout << "INFO: applying transformation for region '" << region -> name << "' to histogram '" << name << "'" << endl;
        //        cout << getSampleName(name) << " : " << getRegionName(name) << " : " << getMVATag(name) << " : " << getSysName(name) << endl;
        rebinHisto(histo, &region -> bins);
        histo -> Write();
      }
      delete histo;
    }
  }
  adir -> SaveSelf(kTRUE);
  savdir -> cd();
}

void HistoTransform::mergeKFolds(TDirectory* source, SubDirectory* subDir) {
  TDirectory* savdir = gDirectory;
  TDirectory* adir = source;
  //    if (source != m_inFile) {
  //      adir = savdir -> mkdir(source -> GetName());
  //    }
  adir -> cd();
  //loop on all entries of this directory
  TKey* key;
  TIter nextkey(source -> GetListOfKeys());
  while ((key = (TKey*) nextkey())) {
    TClass* cl = gROOT -> GetClass(key -> GetClassName());
    if (!cl) continue;
    if (cl -> InheritsFrom(TDirectory::Class())) {
      cout << "INFO: going into directory '" << key -> GetName() << "'" << endl;
      source -> cd(key -> GetName());
      TDirectory* subdir = gDirectory;
      adir -> cd();
      mergeKFolds(subdir, subDir);
      adir -> cd();
    } else if (cl -> InheritsFrom(TH1::Class())) {
      string name = key -> GetName();
      TH1* histo = (TH1*) source -> Get(name.c_str());
      adir -> cd();
      KFold* kFold = getKFold(subDir, name);
      if (isFirstOfKFold(kFold, name)) {
        TString string0ofK = TString::Format("_0of%i", (int) kFold -> regions.size());
        TString nameMerged = name.c_str();
        nameMerged.ReplaceAll(string0ofK, "");
        TH1* histoMerged = (TH1*) histo -> Clone(nameMerged);
        bool foundAllFolds = true;
        for (unsigned int iRegion = 1; iRegion < kFold -> regions.size(); iRegion++) {
          //region = kFold -> regions[iRegion];
          TString foldName = name.c_str();
          //foldName.ReplaceAll(nameFirstRegion, region -> name.c_str());
          TString stringIofK = TString::Format("_%iof%i", iRegion, (int) kFold -> regions.size());
          foldName.ReplaceAll(string0ofK, stringIofK);
          TObject* objHisto = source -> Get(foldName);
          if (objHisto) {
            histo = (TH1*) objHisto;
            histoMerged -> Add(histo);
            delete histo;
            //cout << "added " << iRegion << endl;
          } else {
            cout << "WARNING: histogram '" << foldName << "' not found! Not writing merged output." << endl;
            foundAllFolds = false;
          }
        }
        if (foundAllFolds)
          histoMerged -> Write();
        delete histoMerged;
      }
    }
  }
  adir -> SaveSelf(kTRUE);
  savdir -> cd();
}

void HistoTransform::readTotalBkg(SubDirectory* subDir) {

  for (unsigned int iKFold = 0; iKFold < subDir -> kFolds.size(); iKFold++) {
    KFold* kFold = subDir -> kFolds[iKFold];
    TH1* kFoldBkg = 0;
    for (unsigned int iRegion = 0; iRegion < kFold -> regions.size(); iRegion++) {
      Region* region = kFold -> regions[iRegion];
      cout << "INFO: reading total background for region '" << region -> name << "'" << endl;
      TH1* histoBkg = 0;
      for (unsigned int iBkg = 0; iBkg < subDir -> backgrounds.size(); iBkg++) {

        string histoName = subDir -> backgrounds[iBkg] + "_" + region -> name;
        TObject* objHisto = subDir -> dir -> Get(histoName.c_str());
        if (objHisto == 0) {
          cout << "ERROR: background '" << subDir -> backgrounds[iBkg] << "' not found!" << endl;
          gSystem -> Exit(1);
        }
        if (!histoBkg) {
          histoBkg = (TH1*) objHisto -> Clone("totalBkg");
          histoBkg -> SetDirectory(0);
        } else {
          histoBkg -> Add((TH1*) objHisto);
        }
        if (!kFoldBkg) {
          kFoldBkg = (TH1*) objHisto -> Clone("kFoldBkg");
          kFoldBkg -> SetDirectory(0);
        } else {
          kFoldBkg -> Add((TH1*) objHisto);
        }
      }

      //  histoBkg -> Draw();
      if (!histoBkg) {
        cout << "ERROR: total background not found!" << endl;
        gSystem -> Exit(1);
      }
      region -> bkg = histoBkg;
    }
    if (doMergeKFolds && !doTransformBeforeMerging) {
      for (unsigned int iRegion = 0; iRegion < kFold -> regions.size(); iRegion++) {
        Region* region = kFold -> regions[iRegion];
        region -> bkg = kFoldBkg;
      }
    }
  }
}

void HistoTransform::readSignal(SubDirectory* subDir) {

  if (subDir -> signal == "") {
    cout << "WARNING: signal (possibly used for transformation) not defined!" << endl;
    return;
  }
  for (unsigned int iKFold = 0; iKFold < subDir -> kFolds.size(); iKFold++) {
    KFold* kFold = subDir -> kFolds[iKFold];
    TH1* kFoldSignal = 0;
    for (unsigned int iRegion = 0; iRegion < kFold -> regions.size(); iRegion++) {
      Region* region = kFold -> regions[iRegion];
      cout << "INFO: reading signal for region '" << region -> name << "'" << endl;
      TH1* histoSignal = 0;
      string histoName = subDir -> signal + "_" + region -> name;
      TObject* objHisto = subDir -> dir -> Get(histoName.c_str());
      if (objHisto == 0) {
        cout << "ERROR: signal histogram not found!" << endl;
        gSystem -> Exit(1);
      }
      histoSignal = (TH1*) objHisto -> Clone("signal");
      histoSignal -> SetDirectory(0);
      if (!kFoldSignal) {
        kFoldSignal = (TH1*) objHisto -> Clone("kFoldSignal");
        kFoldSignal -> SetDirectory(0);
      } else {
        kFoldSignal -> Add((TH1*) objHisto);
      }
      region -> sig = histoSignal;
    }
    if (doMergeKFolds && !doTransformBeforeMerging) {
      for (unsigned int iRegion = 0; iRegion < kFold -> regions.size(); iRegion++) {
        Region* region = kFold -> regions[iRegion];
        region -> sig = kFoldSignal;
      }
    }
  }
}

void HistoTransform::findRegions(SubDirectory* subDir, string anyHistoName, float maxUnc, string containRegion, int nFold) {

  cout << "INFO: looking for regions in directory '" << subDir -> dir -> GetName() << "'" << endl;
  TKey* key;
  TIter nextkey(subDir -> dir -> GetListOfKeys());
  while ((key = (TKey*) nextkey())) {
    TClass* cl = gROOT -> GetClass(key -> GetClassName());
    if (!cl) continue;
    if (cl -> InheritsFrom(TH1::Class())) {
      string name = key -> GetName();
      if (getSampleName(name) == anyHistoName) {
        string regionName = getRegionName(name);
        TString regionNameT(regionName.c_str());
        bool addThis = containRegion == "" || regionNameT.Contains(containRegion);
        //        addThis &= regionNameT.Contains("_mva");
        if (addThis) {
          addRegion1(subDir, regionName, maxUnc, nFold);
        }
      }
    }
  }

  if (subDir -> kFolds.size() == 0) {
    cout << "ERROR: no histogram found! maybe there is no histgram named '" << anyHistoName << "'" << endl;
    gSystem -> Exit(1);
  }
}

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(findRegionsOverloads, findRegions, 2,4)

HistoTransform::SubDirectory* HistoTransform::findSubDirs(string subDirName, bool identical) {

  if (identical && subDirName == "") {
    SubDirectory* subDir = new SubDirectory();
    subDir -> dir = m_inFile;
    m_subDirs.push_back(subDir);
    return subDir;
  }

  TKey* key;
  TIter nextkey(m_inFile -> GetListOfKeys());
  while ((key = (TKey*) nextkey())) {
    TClass* cl = gROOT -> GetClass(key -> GetClassName());
    if (!cl) continue;
    if (cl -> InheritsFrom(TDirectory::Class())) {
      TString name = key -> GetName();
      if ((name.Contains(subDirName) && !identical) || name.EqualTo(subDirName)) {
        cout << "INFO: found subdirectory '" << name.Data() << "'" << endl;
        SubDirectory* subDir = new SubDirectory();
        m_inFile -> cd(name);
        subDir -> dir = gDirectory;
        m_subDirs.push_back(subDir);
        if (identical)
          return subDir;
        else
          addBackground(subDir, "bkg");
      }
    }
  }

  if (m_subDirs.size() == 0 && !identical) {
    cout << "INFO: no subdirectory found, using root directory" << endl;
    SubDirectory* subDir = new SubDirectory();
    subDir -> dir = m_inFile;
    m_subDirs.push_back(subDir);
    addBackground(subDir, "bkg");
    return subDir;
  }
  if (identical) {
    cout << "WARNING: subdirectory '" << subDirName << "' not found!" << endl;
  }
  return 0;
}

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(findSubDirsOverloads, findSubDirs, 1,2)

void HistoTransform::skimKFoldTrafos(SubDirectory * subDir) {
  cout << "INFO: skimming kFold transformations (for same number of bins in each fold)" << endl;
  for (unsigned int iKFold = 0; iKFold < subDir -> kFolds.size(); iKFold++) {
    KFold* kFold = subDir -> kFolds[iKFold];
    int nFold = kFold -> regions.size();
    if (nFold <= 1)
      continue;
    int minBins = -1;
    for (int iFold = 0; iFold < nFold; iFold++) {
      int nBins = kFold -> regions[iFold] -> bins.size() - 1;
      if (minBins > nBins || minBins == -1)
        minBins = nBins;
    }
    cout << "INFO: minimum number of bins for kFold '" << kFold -> name << "':" << minBins << endl;
    for (int iFold = 0; iFold < nFold; iFold++) {
      vector<int>* bins = &kFold -> regions[iFold] -> bins;
      while ((int) bins -> size() - 1 > minBins) {
        bins -> pop_back();
        bins -> pop_back();
        bins -> push_back(0);
      }
    }
  }
}

void HistoTransform::addRegion1(SubDirectory* subDir, string regionName, float maxUnc, int nFold) {

  KFold* kFold = new KFold();
  for (int iFold = 0; iFold < nFold; iFold++) {
    Region* region = new Region();
    region -> name = regionName;
    region -> sig = 0;
    if (nFold > 1)
      region -> name += TString::Format("_%iof%i", iFold, nFold);
    region -> maxUnc = maxUnc;
    kFold -> regions.push_back(region);
    kFold -> name = regionName;
    //subDir -> regions.push_back(region);
  }
  //if (nFold > 1)
  subDir -> kFolds.push_back(kFold);
}

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(addRegion1Overloads, addRegion1, 2,4)

string HistoTransform::getNameField(string histoName, int field) {

  TString histNameT(histoName.c_str());
  TObjArray* nameArray = histNameT.Tokenize("_");
  string fieldString = "";
  bool tagFieldFound = false;
  for (int i = 0; i < nameArray -> GetEntries(); i++) {
    TObjString* objString = (TObjString*) nameArray -> At(i);
    bool isTagField = objString -> String().Contains("jet");
    isTagField &= objString -> String().Contains("tag");
    isTagField |= objString -> String().Contains("topcr");
    isTagField |= objString -> String().Contains("topemucr");
    tagFieldFound |= isTagField;
    if (!tagFieldFound && i > 0) {
      field++;
      continue;
    }
    if (i == field) {
      fieldString = objString -> String().Data();
      break;
    }
  }
  nameArray -> Delete();
  if (!tagFieldFound) {
    cout << "WARNING: tag field in '" << histoName << "' not found!" << endl;
  }
  return fieldString;
}

string HistoTransform::getSampleName(string histoName) {

  string suffix = "_" + getRegionName(histoName);
  //  suffix += "_" + getMVATag(histoName);
  if (getSysName(histoName) != "")
    suffix += "_" + getSysName(histoName);
  
  TString name(histoName.c_str());
  name.ReplaceAll(suffix.c_str(), "");
  return name.Data();
}

string HistoTransform::getRegionName(string histoName) {
  return getNameField(histoName, 1) + "_" + getMVATag(histoName);
}

string HistoTransform::getMVATag(string histoName) {
  return getNameField(histoName, 2);
}

string HistoTransform::getSysName(string histoName) {
  return getNameField(histoName, 3);
}

// PUBLIC

HistoTransform::SubDirectory* HistoTransform::addSubDirectory(string subDirName) {
  return findSubDirs(subDirName, true);
}

void HistoTransform::addBackground(SubDirectory* subDir, string bkgName) {
  subDir -> backgrounds.push_back(bkgName);
}

void HistoTransform::setSignal(SubDirectory* subDir, string signalName) {
  subDir -> signal = signalName;
}

void HistoTransform::addRegion(SubDirectory* subDir, string regionName, float maxUnc, int nFold) {
  
  if (transformBkgBDTs)
    findRegions(subDir, "data", maxUnc, regionName);
  else
    addRegion1(subDir, regionName, maxUnc, nFold);
}

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(addRegionOverloads, addRegion, 2,4)

void HistoTransform::run() {

  if (m_subDirs.size() == 0) {
    string subDirName = "Lepton";
    cout << "INFO: no subdirectories defined, looking for those containing '" << subDirName << "'" << endl;
    findSubDirs(subDirName, false);
  }

  for (unsigned int iSubDir = 0; iSubDir < m_subDirs.size(); iSubDir++) {
    SubDirectory* subDir = m_subDirs[iSubDir];
    if (subDir -> kFolds.size() == 0)
      findRegions(subDir, "data");
    readTotalBkg(subDir);
    readSignal(subDir);
    cout << "INFO: using transformation algorithm '" << transformAlgorithm << "'" << endl;
    readRebinBins(subDir);
    skimKFoldTrafos(subDir);
    cout << "INFO: applying transformations" << endl;
    m_outFile -> cd();
    rebinAllHistos(subDir -> dir, subDir);
    if (doMergeKFolds) {
      cout << "INFO: merging KFolds" << endl;
      m_outFile -> cd();
      mergeKFolds(m_outFile, subDir);
    }
  }
  //cout << "INFO: closing input file" << endl;
  //m_inFile -> Close();
  //cout << "INFO: closing output file" << endl;
  //m_outFile -> Close();
};



//BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(addRegionOverloads, addRegion, 2,4)

BOOST_PYTHON_MODULE(HistoTransform_ext)
{
  {
    scope trans = class_<HistoTransform>("HistoTransform", init<const std::string,optional<const std::string> >())//init<TString,optional<TString> >())
    .def_readwrite("m_inFileName", &HistoTransform::m_inFileName)
    .def_readwrite("m_outFileName", &HistoTransform::m_outFileName)
    .def_readwrite("m_inFile", &HistoTransform::m_inFile)
    .def_readwrite("m_outFile", &HistoTransform::m_outFile)
    // need to add structs!

    //

    .def_readwrite("m_subDirs",&HistoTransform::m_subDirs)
    .def("getRebinBins", &HistoTransform::getRebinBins, getRebinOverloads())
    //.def("getRebinBins", getRebinBins_all)
    //.def("getRebinBins", getRebinBins_x1)
    .def("getKFold", &HistoTransform::getKFold, return_value_policy<manage_new_object>())
    .def("getRegion", &HistoTransform::getRegion, return_value_policy<manage_new_object>())
    .def_readwrite("isFirstOfKFold", &HistoTransform::isFirstOfKFold)
    .def("rebinHisto", &HistoTransform::rebinHisto)
    .def("readRebinBins", &HistoTransform::readRebinBins)
    .def("rebinAllHistos", &HistoTransform::rebinAllHistos)
    .def("mergeKFolds", &HistoTransform::mergeKFolds)
    .def("readTotalBkg", &HistoTransform::readTotalBkg)
    .def("readSignal", &HistoTransform::readSignal)
    //.def("findRegions", &HistoTransform::findRegions)
    .def("findRegions", &HistoTransform::findRegions, findRegionsOverloads())
    //.def("findRegions", findRegions_all)
    //.def("findRegions", findRegions_x1)
    //.def("findRegions", findRegions_x2)
    //.def("findRegions", findRegions_x3)
    .def("findSubDirs",&HistoTransform::findSubDirs, return_value_policy<manage_new_object>(), findSubDirsOverloads())
    //.def("findSubDirs", findSubDirs_all, return_value_policy<manage_new_object>())
    //.def("findSubDirs", findSubDirs_x1, return_value_policy<manage_new_object>())
    //    .def("findSubDirs", findSubDirs_x1, return_value_policy<manage_new_object>())
    .def("skimKFoldTrafos", &HistoTransform::skimKFoldTrafos)
    .def("addRegion1", &HistoTransform::addRegion1, addRegion1Overloads())
    //.def("addRegion1", addRegion1_all)
    //.def("addRegion1", addRegion1_x1)
    //.def("addRegion1", addRegion1_x2)
    .def_readwrite("getNameField", &HistoTransform::getNameField)
    .def_readwrite("getSampleName", &HistoTransform::getSampleName)
    .def_readwrite("getRegionName", &HistoTransform::getRegionName)
    .def_readwrite("getMVATag", &HistoTransform::getMVATag)
    .def_readwrite("getSysName", &HistoTransform::getSysName)
    .def("addSubDirectory", &HistoTransform::addSubDirectory, return_value_policy<manage_new_object>())
    .def("addBackground", &HistoTransform::addBackground)
    .def("setSignal", &HistoTransform::setSignal)
    .def("addRegion", &HistoTransform::addRegion, addRegionOverloads())
    //.def("addRegion", addRegion_all)
    //.def("addRegion", addRegion_x1)
    //.def("addRegion", addRegion_x2)
    .def("run", &HistoTransform::run)
    .def_readwrite("doMergeKFolds", &HistoTransform::doMergeKFolds)
    .def_readwrite("doTransformBeforeMerging", &HistoTransform::doTransformBeforeMerging)
    .def_readwrite("transformBkgBDTs", &HistoTransform::transformBkgBDTs)
    .def_readwrite("transformAlgorithm", &HistoTransform::transformAlgorithm)
    .def_readwrite("trafoFiveY", &HistoTransform::trafoFiveY)
    .def_readwrite("trafoSixY", &HistoTransform::trafoSixY)
    .def_readwrite("trafoSixZ", &HistoTransform::trafoSixZ)
    .def_readwrite("trafoSevenNBins", &HistoTransform::trafoSevenNBins)
    .def_readwrite("trafoEightRebin", &HistoTransform::trafoEightRebin)
    ;

  class_<HistoTransform::SubDirectory>("SubDirectory")
    .def_readwrite("dir", &HistoTransform::SubDirectory::dir)
    .def_readwrite("backgrounds", &HistoTransform::SubDirectory::backgrounds)
    .def_readwrite("signal", &HistoTransform::SubDirectory::signal)
    .def_readwrite("kFolds", &HistoTransform::SubDirectory::kFolds)
    ;
    class_<HistoTransform::KFold>("KFold")
      .def_readwrite("name", &HistoTransform::KFold::name)
      .def_readwrite("nFold", &HistoTransform::KFold::nFold)
      .def_readwrite("regions", &HistoTransform::KFold::regions)
    ;
  class_<HistoTransform::Region>("Region")
    .def_readwrite("name", &HistoTransform::Region::name)
    .def_readwrite("maxUnc", &HistoTransform::Region::maxUnc)
    .def_readwrite("bkg", &HistoTransform::Region::bkg)
    .def_readwrite("sig", &HistoTransform::Region::sig)
    .def_readwrite("bins", &HistoTransform::Region::bins)
    ;

  implicitly_convertible<std::string, TString>();
				       }    
}

