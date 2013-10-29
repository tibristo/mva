#include <boost/python.hpp>

#include <map>
#include <vector>
#include <string>
#include <iostream>
#include <cstdlib>

#include "TH1F.h"
#include "TF1.h"
#include "TString.h"
#include "TFile.h"
#include "TObject.h"

using namespace boost::python;

//check namespaces for these thin wrappers

float Get_SystematicWeight0(CAS::EventType type, float VpT, float Mbb, float avgTopPt, float DeltaPhi, int njet){ return CorrAndSysts::Get_SystematicWeight(type, VpT, Mbb, avgTopPt, DeltaPhi, njet);}
float Get_SystematicWeight1(CAS::EventType type, float VpT, float Mbb, float avgTopPt, float DeltaPhi, int njet, CAS::Systematic sys){return CorrAndSysts::Get_SystematicWeight(type, VpT, Mbb, avgTopPt, DeltaPhi, njet, sys);}
float Get_SystematicWeight2(CAS::EventType type, float VpT, float Mbb, float avgTopPt, float DeltaPhi, int njet, CAS::Systematic sys, CAS::SysVar var){return CorrAndSysts::Get_SystematicWeight(type, VpT, Mbb, avgTopPt, DeltaPhi, njet, sys, var);}
float Get_SystematicWeight3(CAS::EventType type, float VpT, float Mbb, float avgTopPt, float DeltaPhi, int njet, CAS::Systematic sys, CAS::SysVar var, CAS::SysBin bin){return CorrAndSysts::Get_SystematicWeight(type, VpT, Mbb, avgTopPt, DeltaPhi, njet, sys, var, bin);}


  // Systematics on distributions
//  float Get_SystematicWeight(CAS::EventType type, float VpT, float Mbb, float avgTopPt, float DeltaPhi, int njet, CAS::Systematic sys=CAS::Nominal, CAS::SysVar var=CAS::Up, CAS::SysBin bin=CAS::None);
//  float Get_SystematicWeight(CAS::EventType type, float VpT, float Mbb, float avgTopPt, float DeltaPhi, int njet, TString sysName);
/*
  inline float Get_SystematicWeight(TString evtType, float VpT, float Mbb, float avgTopPt, float DeltaPhi, int njet, CAS::Systematic sys, CAS::SysVar var, CAS::SysBin bin)
  { return Get_SystematicWeight(m_typeNames[evtType.Data()], VpT, Mbb, avgTopPt, DeltaPhi, njet, sys, var, bin); }

  inline float Get_SystematicWeight(TString evtType, float VpT, float Mbb, float avgTopPt, float DeltaPhi, int njet, TString sysName)
  { return Get_SystematicWeight(m_typeNames[evtType.Data()], VpT, Mbb, avgTopPt, DeltaPhi, njet, sysName); }
*/

float (CorrAndSysts::*Get_HiggsNLOEWKCorrectionx1)(CAS::EventType, float) = &CorrAndSysts::Get_HiggsNLOEWKCorrection;
float (CorrAndSysts::*Get_HiggsNLOEWKCorrectionx2)(ROOT::TString, float) = &CorrAndSysts::Get_HiggsNLOEWKCorrection; //inline
float (CorrAndSysts::*Get_BkgpTCorrectionx1)(CAS::EventType, float) = &CorrAndSysts::Get_BkgpTCorrection;
float (CorrAndSysts::*Get_BkgpTCorrectionx2)(ROOT::TString, float) = &CorrAndSysts::Get_BkgpTCorrection;//inline
float (CorrAndSysts::*Get_ToppTCorrectionx1)(CAS::EventType, float) = &CorrAndSysts::Get_ToppTCorrection;
float (CorrAndSysts::*Get_ToppTCorrectionx2)(ROOT::TString, float) = &CorrAndSysts::Get_ToppTCorrection;//inline
float (CorrAndSysts::*Get_BkgDeltaPhiCorrectionx1)(CAS::EventType, float, int) = &CorrAndSysts::Get_BkgDeltaPhiCorrection;
float (CorrAndSysts::*Get_BkgDeltaPhiCorrectionx2)(ROOT::TString, float, int) = &CorrAndSysts::Get_BkgDeltaPhiCorrection;//inline
//float (CorrAndSysts::*Get_SystematicWeightx1)(CAS::EventType, float, float, float, float, int, CAS::Systematic, CAS::SysVar, CAS::SysBin) = &CorrAndSysts::Get_SystematicWeight; // default values need to be included!
float (CorrAndSysts::*Get_SystematicWeightx2)(CAS::EventType, float, float, float, float, int, ROOT::TString) = &CorrAndSysts::Get_SystematicWeight;
float (CorrAndSysts::*Get_SystematicWeightx3)(ROOT::TString, float, float, float, float, int, CAS::Systematic, CAS::SysVar, CAS::SysBin) = &CorrAndSysts::Get_SystematicWeight; //inline
float (CorrAndSysts::*Get_SystematicWeightx4)(ROOT::TString, float, float, float, float, int, ROOT::TString) = &CorrAndSysts::Get_SystematicWeight; //inline

void (Utils::*FillTH1Fx1)(std::vector<ROOT::Float_t>, ROOT::TH1F*, std::map<ROOT::TString, ROOT::TObject*>&) = &Utils::FillTH1F;
void (Utils::*FillTH1Fx2)(int, ROOT::Float_t*, ROOT::TH1F*, std::map<ROOT::TString, ROOT::TObject*>&) = &Utils::FillTH1F;

BOOST_PYTHON_MODULE(Corrs)
{

  scope CAS = class_<CAS>("CAS");
  enum_<CAS::EventType>("EventType")
    .value("WHlvbb"=0,WHlvbb)
    .value("ZHllbb",ZHllbb)
    .value("ZHvvbb",ZHvvbb)
    .value("Wb",Wb)
    .value("Wc",Wc)
    .value("Wcc",Wcc)
    .value("Wl",Wl)
    .value("Zb",Zb)
    .value("Zc",Zc)
    .value("Zl",Zl)
    .value("ttbar",ttbar)
    .value("stop",stop)
    .value("diboson",diboson)
    .value("NONAME",NONAME);

  enum_<CAS::SysVar>("SysVar")
    .value("Do",Do=0)
    .value("Up", Up=1);

  enum_<CAS::SysBin>("SysBin")
    .value("None",None =-2)                            // default
    .value("Any",Any = -1)                             // means no binning -> used for continuous systematics
    .value("Bin0", Bin0 = 0)
    .value("Bin1", Bin1) 
    .value("Bin2", Bin2)
    .value("Bin3", Bin3)
    .value("Bin4", Bin4)     // pT bins for binned systematics
    .value("NOTDEFINED", NOTDEFINED);


  enum_<CAS::Systematic>("Systematic") // only systematics affecting the shape are relevant to this tool
    .value("Nominal",Nominal)
    // the following are binned in pT (5 bins") independent systematics)
    .value("PTBINNED",PTBINNED)
    .value("SysStopPt",SysStopPt)
    .value("SysWbbPtW",SysWbbPtW)
    .value("SysWccPtW",SysWccPtW)
    .value("SysZbbPtZ",SysZbbPtZ)
    .value("SysZccPtZ",SysZccPtZ)
    .value("SysWllPtW",SysWllPtW)
    .value("SysZllPtZ",SysZllPtZ)
    // the following are continuous (thus correlated in pT)
    .value("CONTINUOUS",CONTINUOUS)
    .value("SysTheoryHPt",SysTheoryHPt)
    .value("SysTopPt",SysTopPt)
    .value("SysTopMbb",SysTopMbb)
    .value("SysStopMbb",SysStopMbb)
    .value("SysZbbMbb",SysZbbMbb)
    .value("SysWbbMbb",SysWbbMbb)
    .value("SysZMbb",SysZMbb)
    .value("SysWMbb",SysWMbb)
    .value("SysWDPhi",SysWDPhi)
    .value("SysWccDPhi",SysWccDPhi)
    .value("SysWbDPhi",SysWbDPhi)
    .value("SysZDPhi",SysZDPhi)
    .value("SysZcDPhi",SysZcDPhi)
    .value("SysZbDPhi",SysZbDPhi)
    .value("LAST",LAST);
    
  //scope b = class_<CorrAndSysts>("b");
  
  scope corr = class_<CorrAndSysts>("CorrsAndSysts",init<ROOT::TString,bool>())
    .def(init<int, int, bool>())
    .def("Initialize", &CorrAndSysts::Initialise)
    .def("SetDebug", &CorrAndSysts::SetDebug)//inline
    .def("WriteHistsToFile", &CorrAndSysts::WriteHistsToFile)
    .def("Get_HiggsNLOEWKCorrection", &CorrAndSysts::Get_HiggsNLOEWKCorrectionx1)
    .def("Get_HiggsNLOEWKCorrection", &CorrAndSysts::Get_HiggsNLOEWKCorrectionx2)//inline
    .def("Get_BkgpTCorrection", &CorrAndSysts::Get_BkgpTCorrectionx1)
    .def("Get_BkgpTCorrection", &CorrAndSysts::Get_BkgpTCorrectionx2)//inline
    .def("Get_ToppTCorrection", &CorrAndSysts::Get_ToppTCorrectionx1)
    .def("Get_ToppTCorrection", &CorrAndSysts::Get_ToppTCorrectionx2)//inline
    .def("Get_BkgDeltaPhiCorrection", &CorrAndSysts::Get_BkgDeltaPhiCorrectionx1)
    .def("Get_BkgDeltaPhiCorrection", &CorrAndSysts::Get_BkgDeltaPhiCorrectionx2)
    .def("Get_SystematicWeight", &CorrAndSysts::Get_SystematicWeight0)
    .def("Get_SystematicWeight", &CorrAndSysts::Get_SystematicWeight1)
    .def("Get_SystematicWeight", &CorrAndSysts::Get_SystematicWeight2)
    .def("Get_SystematicWeight", &CorrAndSysts::Get_SystematicWeight3)
    .def("Get_SystematicWeight", &CorrAndSysts::Get_SystematicWeightx2)
    .def("Get_SystematicWeight", &CorrAndSysts::Get_SystematicWeightx3)//inline
    .def("Get_SystematicWeight", &CorrAndSysts::Get_SystematicWeightx4)//inline
    .def("Get_SystName", &CorrAndSysts::Get_SystName)//inline
    .def("GetSystFromName", &CorrAndSysts::GetSystFromName)//inline
    .def("GetEventType", &CorrAndSysts::GetEventType)
    .def("GetSysBin", &CorrAndSysts::GetSysBin)
    .def_readwrite("m_debug", &CorrAndSysts::m_debug)
    .def_readwrite("m_draw", &CorrAndSysts::m_draw)  
    .def_readwrite("m_zero", &CorrAndSysts::m_zero)  
    .def_readwrite("m_one", &CorrAndSysts::m_one)  
    .def_readwrite("m_two", &CorrAndSysts::m_two)  
    .def_readwrite("m_seven", &CorrAndSysts::m_seven)  
    .def_readwrite("m_eight", &CorrAndSysts::m_eight)  
    .def_readwrite("pTbins", &CorrAndSysts::pTbins)
    .def_readwrite("m_typeNames", &CorrAndSysts::m_typeNames)
    .def_readwrite("m_systNames", &CorrAndSysts::m_systNames)
    .def_readwrite("m_varNames", &CorrAndSysts::m_varNames)
    .def_readwrite("m_binNames", &CorrAndSysts::m_binNames)
    .def_readwrite("m_systFromNames", &CorrAndSysts::m_systFromNames)
    .def_readwrite("m_varFromNames", &CorrAndSysts::m_varFromNames)
    .def_readwrite("m_binFromNames", &CorrAndSysts::m_binFromNames)
    .def_readwrite("m_allHists", &CorrAndSysts::m_allHists)
    .def_readwrite("m_h_WHlvbbNLOEWKCorrection", &CorrAndSysts::m_h_WHlvbbNLOEWKCorrection)
    .def_readwrite("m_h_ZHllbbNLOEWKCorrection", &CorrAndSysts::m_h_ZHllbbNLOEWKCorrection)
    .def_readwrite("m_h_ZHvvbbNLOEWKCorrection", &CorrAndSysts::m_h_ZHvvbbNLOEWKCorrection)
    .def_readwrite("m_h_WpTCorrection", &CorrAndSysts::m_h_WpTCorrection)
    .def_readwrite("m_h_ZpTCorrection", &CorrAndSysts::m_h_ZpTCorrection)
    .def_readwrite("m_h_WDeltaPhiCorrection2Jet", &CorrAndSysts::m_h_WDeltaPhiCorrection2Jet)
    .def_readwrite("m_h_WDeltaPhiCorrection3Jet", &CorrAndSysts::m_h_WDeltaPhiCorrection3Jet)
    .def_readwrite("m_h_ZDeltaPhiCorrection", &CorrAndSysts::m_h_ZDeltaPhiCorrection)
    .def_readwrite("m_h_topPtCorrection", &CorrAndSysts::m_h_topPtCorrection)
    
    // binned systematics
    .def_readwrite("m_h_SysWbbPtW", &CorrAndSysts::m_h_SysWbbPtW)
    .def_readwrite("m_h_SysStopPt", &CorrAndSysts::m_h_SysStopPt)
    .def_readwrite("m_h_SysWccPtW", &CorrAndSysts::m_h_SysWccPtW)
    .def_readwrite("m_h_SysWllPtW", &CorrAndSysts::m_h_SysWllPtW)
    .def_readwrite("m_h_SysZbbPtZ", &CorrAndSysts::m_h_SysZbbPtZ)
    .def_readwrite("m_h_SysZccPtZ", &CorrAndSysts::m_h_SysZccPtZ)
    .def_readwrite("m_h_SysZllPtZ", &CorrAndSysts::m_h_SysZllPtZ)
    
    // continuous systematics
    .def_readwrite("m_h_SysTheoryWHlvbbPt", &CorrAndSysts::m_h_SysTheoryWHlvbbPt)
    .def_readwrite("m_h_SysTheoryZHllbbPt", &CorrAndSysts::m_h_SysTheoryZHllbbPt)
    .def_readwrite("m_h_SysTheoryZHvvbbPt", &CorrAndSysts::m_h_SysTheoryZHvvbbPt)
    .def_readwrite("m_f_WDPhiCorr", &CorrAndSysts::m_f_WDPhiCorr)
    .def_readwrite("m_f_ZDPhiCorr", &CorrAndSysts::m_f_ZDPhiCorr)
    .def_readwrite("m_f_SysZbbMbb", &CorrAndSysts::m_f_SysZbbMbb)
    .def_readwrite("m_f_SysWbbMbb", &CorrAndSysts::m_f_SysWbbMbb)
    .def_readwrite("m_f_SysTopMbb", &CorrAndSysts::m_f_SysTopMbb)
    .def_readwrite("m_f_SysStopMbb", &CorrAndSysts::m_f_SysStopMbb)
    .def_readwrite("m_f_SysWMbb", &CorrAndSysts::m_f_SysWMbb)
    .def_readwrite("m_f_SysZMbb", &CorrAndSysts::m_f_SysZMbb);

    
  scope utils = class_<Utils>("Utils")
    .def("BuildTH1F", &Utils::BuildTH1F)
    .def("FillTH1F", &Utils::FillTH1Fx1)
    .def("FillTH1F", &Utils::FillTH1Fx2)
    .def("GetScale", &Utils::GetScale)//inline
    ;//.def("reverseMap")
;



  // use TH* to store weights ; seems easier to maintain if ever we need e.g 2-d corrections
  // corrections


};
