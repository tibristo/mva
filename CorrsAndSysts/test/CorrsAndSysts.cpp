#include <boost/python.hpp>
#include "CorrsAndSysts.hpp"
#include <algorithm>
#include <cmath>
#include <Python.h>
#include <TVector2.h>
using namespace boost::python;

/*
 * See header file for description
 *
 */

CorrsAndSysts::CorrsAndSysts(TString name, bool draw) :
  m_debug(0),
  m_zero(false),
  m_one(false),
  m_two(false),
  m_seven(false),
  m_eight(false)
{
  m_draw = draw;

  // set analysis basesd on contentes of name
  if(name.Contains("Zero") || name.Contains("zero") || name.Contains("ZERO")) { m_zero = true; }
  if(name.Contains("One")  || name.Contains("one")  || name.Contains("ONE"))  { m_one  = true; }
  if(name.Contains("Two")  || name.Contains("two")  || name.Contains("TWO"))  { m_two  = true; }

  // check lepton selection chosen correctly
  if((m_zero && m_one) || (m_zero && m_two) || (m_one && m_two)) {
    std::cout << "CorrsAndSysts initialized for multiple analyses" << std::endl;
    exit(-1);
  }
  if(!m_zero && !m_one && !m_two) {
    std::cout << "CorrsAndSysts initialized for none of the analyses" << std::endl;
    exit(-1);
  }

  // set year
  if(name.Contains("7TeV")) { m_seven = true; }
  if(name.Contains("8TeV")) { m_eight = true; }

  // check year is set correctly
  if(m_seven && m_eight) {
    std::cout << "CorrsAndSysts initialized for 7 and 8 TeV" << std::endl;
    exit(-1);
  }
  if(!m_seven && !m_eight) {
    std::cout << "CorrsAndSysts initialized for neither 7 nor 8 TeV" << std::endl;
    exit(-1);
  }

  // write some stuff so users can be confident they did this correctly
  std::cout << "Initalize CorrsAndSysts for ";
  if(m_zero) {  std::cout << "Zero"; }
  if(m_one)  {  std::cout << "One";  }
  if(m_two)  {  std::cout << "Two";  }
  std::cout << " Lepton ";
  if(m_seven) { std::cout << "7"; }
  if(m_eight) { std::cout << "8"; }
  std::cout << " TeV analysis" << std::endl;

  // initalize the corrections and systematics
  Initialize();

} // CorrsAndSysts

CorrsAndSysts::CorrsAndSysts(int channel, int year, bool draw) :
  m_debug(0),
  m_zero(false),
  m_one(false),
  m_two(false),
  m_seven(false),
  m_eight(false)
{
  m_draw = draw;

  switch(channel) {
    case 0:
      m_zero = true;
    break;
    case 1:
      m_one = true;
    break;
    case 2:
      m_two = true;
    break;
    default:
      std::cout << "CorrsAndSysts initialized for none of the analyses" << std::endl;
      exit(-1);
  }
  switch(year) {
    case 2011:
      m_seven = true;
    break;
    case 2012:
      m_eight = true;
    break;
    default:
      std::cout << "CorrsAndSysts initialized for neither 7 nor 8 TeV" << std::endl;
      exit(-1);
  }

  // write some stuff so users can be confident they did this correctly
  std::cout << "Initalize CorrsAndSysts for ";
  if(m_zero) {  std::cout << "Zero"; }
  if(m_one)  {  std::cout << "One";  }
  if(m_two)  {  std::cout << "Two";  }
  std::cout << " Lepton ";
  if(m_seven) { std::cout << "7"; }
  if(m_eight) { std::cout << "8"; }
  std::cout << " TeV analysis" << std::endl;

  // initalize the corrections and systematics
  Initialize();


} // CorrsAndSysts

CorrsAndSysts::~CorrsAndSysts() {
  delete m_h_WHlvbbNLOEWKCorrection;
  delete m_h_ZHllbbNLOEWKCorrection;
  delete m_h_ZHvvbbNLOEWKCorrection;
  delete m_h_WpTCorrection;
  delete m_h_ZpTCorrection;
  delete m_h_WDeltaPhiCorrection2Jet;
  delete m_h_WDeltaPhiCorrection3Jet;
  delete m_h_ZDeltaPhiCorrection;
  delete m_h_topPtCorrection;

  delete m_h_SysWbbPtW;
  delete m_h_SysStopPt;
  delete m_h_SysWccPtW;
  delete m_h_SysWllPtW;
  delete m_h_SysZbbPtZ;
  delete m_h_SysZccPtZ;
  delete m_h_SysZllPtZ;

  delete m_h_SysTheoryWHlvbbPt;
  delete m_h_SysTheoryZHllbbPt;
  delete m_h_SysTheoryZHvvbbPt;
  delete m_f_WDPhiCorr;
  delete m_f_ZDPhiCorr;
  delete m_f_SysZbbMbb;
  delete m_f_SysWbbMbb;
  delete m_f_SysTopMbb;
  delete m_f_SysStopMbb;
  delete m_f_SysWMbb;
  delete m_f_SysZMbb;

}

void CorrsAndSysts::Initialize() {
  // initialize the mappings to event types
  m_typeNames["WHlvbb"] = CAS::WHlvbb;
  m_typeNames["ZHllbb"] = CAS::ZHllbb;
  m_typeNames["ZHvvbb"] = CAS::ZHvvbb;
  m_typeNames["WlvH"] = CAS::WHlvbb;
  m_typeNames["ZllH"] = CAS::ZHllbb;
  m_typeNames["ZvvH"] = CAS::ZHvvbb;
  m_typeNames["signalWH"] = CAS::WHlvbb;
  m_typeNames["signalZHll"] = CAS::ZHllbb;
  m_typeNames["signalZHvv"] = CAS::ZHvvbb;
  m_typeNames["Wb"] = CAS::Wb;
  m_typeNames["Wbb"] = CAS::Wb;
  m_typeNames["Wbc"] = CAS::Wb;
  m_typeNames["Wbl"] = CAS::Wb;
  m_typeNames["Wc"] = CAS::Wc;
  m_typeNames["Wcl"] = CAS::Wc;
  m_typeNames["Wcc"] = CAS::Wcc;
  m_typeNames["Wl"] = CAS::Wl;
  m_typeNames["Wll"] = CAS::Wl;
  m_typeNames["Zb"] = CAS::Zb;
  m_typeNames["Zbb"] = CAS::Zb;
  m_typeNames["Zbc"] = CAS::Zb;
  m_typeNames["Zbl"] = CAS::Zb;
  m_typeNames["Zc"] = CAS::Zc;
  m_typeNames["Zcc"] = CAS::Zc;
  m_typeNames["Zcl"] = CAS::Zc;
  m_typeNames["Zl"] = CAS::Zl;
  m_typeNames["Zll"] = CAS::Zl;
  m_typeNames["top"] = CAS::ttbar;
  m_typeNames["ttbar"] = CAS::ttbar;
  m_typeNames["stop"] = CAS::stop;
  m_typeNames["WW"] = CAS::diboson;
  m_typeNames["WZ"] = CAS::diboson;
  m_typeNames["ZZ"] = CAS::diboson;

  m_systNames[CAS::Nominal] = "";
  m_systNames[CAS::SysTheoryHPt] = "SysTheoryHPt";
  m_systNames[CAS::SysTopPt] = "SysTopPt";
  m_systNames[CAS::SysStopPt] = "SysStopPt";
  m_systNames[CAS::SysWbbPtW] = "SysWbbPtW";
  m_systNames[CAS::SysWccPtW] = "SysWccPtW";
  m_systNames[CAS::SysZbbPtZ] = "SysZbbPtZ";
  m_systNames[CAS::SysZccPtZ] = "SysZccPtZ";
  m_systNames[CAS::SysWllPtW] = "SysWllPtW";
  m_systNames[CAS::SysZllPtZ] = "SysZllPtZ";
  m_systNames[CAS::SysTopMbb] = "SysTopMbb";
  m_systNames[CAS::SysStopMbb] = "SysStopMbb";
  m_systNames[CAS::SysZbbMbb] = "SysZbbMbb";
  m_systNames[CAS::SysWbbMbb] = "SysWbbMbb";
  m_systNames[CAS::SysZMbb] = "SysZMbb";
  m_systNames[CAS::SysWMbb] = "SysWMbb";
  m_systNames[CAS::SysWDPhi] = "SysWDPhi";
  m_systNames[CAS::SysWccDPhi] = "SysWccDPhi";
  m_systNames[CAS::SysWbDPhi] = "SysWbDPhi";
  m_systNames[CAS::SysZDPhi] = "SysZDPhi";
  m_systNames[CAS::SysZcDPhi] = "SysZcDPhi";
  m_systNames[CAS::SysZbDPhi] = "SysZbDPhi";

  m_varNames[CAS::Up] = "Up";
  m_varNames[CAS::Do] = "Do";

  m_binNames[CAS::None] = "";
  m_binNames[CAS::Any] = "";
  m_binNames[CAS::Bin0] = "Bin0";
  m_binNames[CAS::Bin1] = "Bin1";
  m_binNames[CAS::Bin2] = "Bin2";
  m_binNames[CAS::Bin3] = "Bin3";
  m_binNames[CAS::Bin4] = "Bin4";

  m_systFromNames = Utils::reverseMap<CAS::Systematic, std::string>(m_systNames);
  m_varFromNames = Utils::reverseMap<CAS::SysVar, std::string>(m_varNames);
  // resolve ambiguity
  m_binFromNames = Utils::reverseMap<CAS::SysBin, std::string>(m_binNames);
  m_binFromNames[""] = CAS::Any;

  // V pT bins. For now 5 bins as in cut-based
  pTbins[0] = 0.;
  pTbins[1] = 90.e3;
  pTbins[2] = 120.e3;
  pTbins[3] = 160.e3;
  pTbins[4] = 200.e3;
  pTbins[5] = 500.e3;


  /*********************************************
   *
   *    CORRECTIONS
   *    These should be applied to the nominal
   *
   *    Below the histograms which contain the
   *    values of the correction are created
   *
  *********************************************/

  // signal NLO EW corrections
  m_h_WHlvbbNLOEWKCorrection = new TH1F("WHlvbbpTCorr","WHlvbbpTCorr",95 ,25.e3, 500.e3);
  m_h_WHlvbbNLOEWKCorrection->SetDirectory(0);
  m_h_ZHllbbNLOEWKCorrection = new TH1F("ZHllbbpTCorr","ZHllbbpTCorr",95 ,25.e3, 500.e3);
  m_h_ZHllbbNLOEWKCorrection->SetDirectory(0);
  m_h_ZHvvbbNLOEWKCorrection = new TH1F("ZHvvbbpTCorr","ZHvvbbpTCorr",95 ,25.e3, 500.e3);
  m_h_ZHvvbbNLOEWKCorrection->SetDirectory(0);

  // numbers from Jason
  if(m_seven) {
    Float_t a_whlvbbcorr[95] = {0.00224198, -0.000370526, -0.00169178, -0.00189401, -0.00200129, -0.00301404, -0.00325795, -0.0041637, -0.00587139, -0.00739039, -0.00917371, -0.0112332, -0.0134147, -0.0152704, -0.0175308, -0.0194987, -0.021615, -0.0233439, -0.0251813, -0.0278489, -0.0296617, -0.0324331, -0.0347805, -0.0362031, -0.0376821, -0.0403375, -0.042188, -0.0439056, -0.045399, -0.0482114, -0.0505533, -0.0524687, -0.0556041, -0.0565102, -0.0585783, -0.0618502, -0.0639255, -0.0660007, -0.068076, -0.0701513, -0.0722265, -0.0743018, -0.0763771, -0.0784523, -0.0805276, -0.0826029, -0.0846781, -0.0867534, -0.0888287, -0.0909039, -0.0929792, -0.0950545, -0.0971297, -0.099205, -0.10128, -0.103356, -0.105431, -0.107506, -0.109581, -0.111657, -0.113732, -0.115807, -0.117882, -0.119958, -0.122033, -0.124108, -0.126183, -0.128259, -0.130334, -0.132409, -0.134485, -0.13656, -0.138635, -0.14071, -0.142786, -0.144861, -0.146936, -0.149011, -0.151087, -0.153162, -0.155237, -0.157312, -0.159388, -0.161463, -0.163538, -0.165614, -0.167689, -0.169764, -0.171839, -0.173915, -0.17599, -0.178065, -0.18014, -0.182216, -0.184291};
    Utils::FillTH1F(95, a_whlvbbcorr, m_h_WHlvbbNLOEWKCorrection, m_allHists);
    Float_t a_zhllbbcorr[95] = {0.000369691, -0.00311954, -0.00814806, -0.0101356, -0.0133924, -0.015624, -0.0188796, -0.0212749, -0.0233653, -0.0254506, -0.0270923, -0.028222, -0.0284564, -0.0287463, -0.0294866, -0.031416, -0.0304275, -0.0317627, -0.0329827, -0.0322219, -0.0339739, -0.0323855, -0.0329175, -0.0336001, -0.033455, -0.0350176, -0.0341059, -0.0383008, -0.0375261, -0.0404764, -0.0405512, -0.0410093, -0.0432318, -0.0475565, -0.0498079, -0.0470666, -0.0544329, -0.0534824, -0.055241, -0.0582209, -0.0604063, -0.0625916, -0.064777, -0.0669624, -0.0691477, -0.0713331, -0.0735185, -0.0757038, -0.0778892, -0.0800746, -0.0822599, -0.0844453, -0.0866307, -0.088816, -0.0910014, -0.0931868, -0.0953721, -0.0975575, -0.0997429, -0.101928, -0.104114, -0.106299, -0.108484, -0.11067, -0.112855, -0.11504, -0.117226, -0.119411, -0.121597, -0.123782, -0.125967, -0.128153, -0.130338, -0.132523, -0.134709, -0.136894, -0.139079, -0.141265, -0.14345, -0.145636, -0.147821, -0.150006, -0.152192, -0.154377, -0.156562, -0.158748, -0.160933, -0.163119, -0.165304, -0.167489, -0.169675, -0.17186, -0.174045, -0.176231, -0.178416};
    Utils::FillTH1F(95, a_zhllbbcorr, m_h_ZHllbbNLOEWKCorrection, m_allHists);
    Float_t a_zhvvbbcorr[95] = {0.0148102, 0.0137398, 0.0127929, 0.0117756, 0.011091, 0.0100978, 0.0094288, 0.0083615, 0.00791759, 0.00740715, 0.00712286, 0.00672918, 0.00662655, 0.00650805, 0.00671416, 0.00694015, 0.00738593, 0.00741676, 0.00850807, 0.00886493, 0.010138, 0.011426, 0.0122657, 0.0125201, 0.01283, 0.0127657, 0.0135671, 0.0126575, 0.0118711, 0.0115731, 0.0104059, 0.0108386, 0.00905639, 0.00774211, 0.00647519, 0.00545708, 0.00377601, 0.00251831, 0.00148805, 5.26677e-06, -0.00186611, -0.0037375, -0.00560888, -0.00748026, -0.00935164, -0.011223, -0.0130944, -0.0149658, -0.0168372, -0.0187085, -0.0205799, -0.0224513, -0.0243227, -0.0261941, -0.0280655, -0.0299368, -0.0318082, -0.0336796, -0.035551, -0.0374224, -0.0392937, -0.0411651, -0.0430365, -0.0449079, -0.0467793, -0.0486507, -0.050522, -0.0523934, -0.0542648, -0.0561362, -0.0580076, -0.0598789, -0.0617503, -0.0636217, -0.0654931, -0.0673645, -0.0692359, -0.0711072, -0.0729786, -0.07485, -0.0767214, -0.0785928, -0.0804641, -0.0823355, -0.0842069, -0.0860783, -0.0879497, -0.0898211, -0.0916924, -0.0935638, -0.0954352, -0.0973066, -0.099178, -0.101049, -0.102921};
    Utils::FillTH1F(95, a_zhvvbbcorr, m_h_ZHvvbbNLOEWKCorrection, m_allHists);
  }
  else if(m_eight) {
    Float_t a_whlvbbcorr[95] = {0.00200484, -9.13928e-05, -0.00219974, -0.00202884, -0.00219318, -0.00299564, -0.00336771, -0.00409143, -0.0059936, -0.00750034, -0.00881597, -0.0111589, -0.0135328, -0.0151878, -0.0178145, -0.0189559, -0.0215716, -0.0233429, -0.0250507, -0.0278028, -0.0291708, -0.0319617, -0.0341056, -0.0365647, -0.0381327, -0.0399857, -0.0405974, -0.0444237, -0.0454833, -0.0482596, -0.0486239, -0.0534461, -0.0539187, -0.0559509, -0.0596689, -0.0610085, -0.0633554, -0.0639406, -0.0672306, -0.0699078, -0.0719664, -0.0740249, -0.0760835, -0.078142, -0.0802005, -0.0822591, -0.0843176, -0.0863761, -0.0884347, -0.0904932, -0.0925517, -0.0946103, -0.0966688, -0.0987273, -0.100786, -0.102844, -0.104903, -0.106961, -0.10902, -0.111079, -0.113137, -0.115196, -0.117254, -0.119313, -0.121371, -0.12343, -0.125488, -0.127547, -0.129605, -0.131664, -0.133722, -0.135781, -0.13784, -0.139898, -0.141957, -0.144015, -0.146074, -0.148132, -0.150191, -0.152249, -0.154308, -0.156366, -0.158425, -0.160483, -0.162542, -0.1646, -0.166659, -0.168718, -0.170776, -0.172835, -0.174893, -0.176952, -0.17901, -0.181069, -0.183127};
    Utils::FillTH1F(95, a_whlvbbcorr, m_h_WHlvbbNLOEWKCorrection, m_allHists);
    Float_t a_zhllbbcorr[95] = {0.000664024, -0.00357095, -0.00767076, -0.00967366, -0.0134844, -0.0157148, -0.0181885, -0.0209647, -0.0232788, -0.0252373, -0.0265634, -0.0275069, -0.0285776, -0.0281683, -0.0294206, -0.0299975, -0.0308047, -0.0311716, -0.030913, -0.0324821, -0.0323192, -0.0324639, -0.0319356, -0.0322621, -0.0331146, -0.0338905, -0.0345189, -0.0358591, -0.0358407, -0.040018, -0.0396389, -0.0407177, -0.0445103, -0.0441406, -0.0471215, -0.0463301, -0.0513777, -0.0536773, -0.0546446, -0.0568508, -0.0590333, -0.0612157, -0.0633981, -0.0655805, -0.067763, -0.0699454, -0.0721278, -0.0743103, -0.0764927, -0.0786751, -0.0808575, -0.08304, -0.0852224, -0.0874048, -0.0895872, -0.0917697, -0.0939521, -0.0961345, -0.098317, -0.100499, -0.102682, -0.104864, -0.107047, -0.109229, -0.111412, -0.113594, -0.115776, -0.117959, -0.120141, -0.122324, -0.124506, -0.126689, -0.128871, -0.131053, -0.133236, -0.135418, -0.137601, -0.139783, -0.141965, -0.144148, -0.14633, -0.148513, -0.150695, -0.152878, -0.15506, -0.157242, -0.159425, -0.161607, -0.16379, -0.165972, -0.168155, -0.170337, -0.172519, -0.174702, -0.176884};
    Utils::FillTH1F(95, a_zhllbbcorr, m_h_ZHllbbNLOEWKCorrection, m_allHists);
    Float_t a_zhvvbbcorr[95] = {0.0146846, 0.0136521, 0.0125801, 0.0117771, 0.010976, 0.00989665, 0.00929942, 0.00836484, 0.00781992, 0.00733247, 0.00688885, 0.00666833, 0.0063354, 0.00637412, 0.00662595, 0.0069015, 0.00716689, 0.00760953, 0.00823267, 0.00914484, 0.00960494, 0.0110894, 0.0122241, 0.0127155, 0.0126892, 0.0125873, 0.01278, 0.0128243, 0.0118519, 0.0116125, 0.0102697, 0.00960959, 0.00929141, 0.00807739, 0.00588976, 0.00522135, 0.00365527, 0.00214147, 0.000569382, 0.000322672, -0.0015679, -0.00345846, -0.00534903, -0.0072396, -0.00913017, -0.0110207, -0.0129113, -0.0148019, -0.0166924, -0.018583, -0.0204736, -0.0223641, -0.0242547, -0.0261453, -0.0280358, -0.0299264, -0.031817, -0.0337076, -0.0355981, -0.0374887, -0.0393793, -0.0412698, -0.0431604, -0.045051, -0.0469415, -0.0488321, -0.0507227, -0.0526132, -0.0545038, -0.0563944, -0.0582849, -0.0601755, -0.0620661, -0.0639566, -0.0658472, -0.0677378, -0.0696283, -0.0715189, -0.0734095, -0.0753001, -0.0771906, -0.0790812, -0.0809718, -0.0828623, -0.0847529, -0.0866435, -0.088534, -0.0904246, -0.0923152, -0.0942057, -0.0960963, -0.0979869, -0.0998774, -0.101768, -0.103659};
    Utils::FillTH1F(95, a_zhvvbbcorr, m_h_ZHvvbbNLOEWKCorrection, m_allHists);
  }

  // W, Z and top backgrounds pT corrections
  m_h_WpTCorrection = new TH1F("WpTCorr","WpTCorr",5 ,pTbins);
  m_h_WpTCorrection->SetDirectory(0);
  m_h_ZpTCorrection = new TH1F("ZpTCorr","ZpTCorr",5 ,pTbins);
  m_h_ZpTCorrection->SetDirectory(0);

  Float_t a_wcorr[5] = {0.02, 0.00, 0.01, -0.01, -0.05};
  Utils::FillTH1F(5, a_wcorr, m_h_WpTCorrection, m_allHists);
  Float_t a_zcorr[5] = {0.00, -0.01, 0.00, 0.00, -0.03};
  Utils::FillTH1F(5, a_zcorr, m_h_ZpTCorrection, m_allHists);


  // W, backgrounds DeltaPhi corrections
  m_h_WDeltaPhiCorrection2Jet = new TH1F("WDeltaPhiCorr2Jet","WDeltaPhiCorr2Jet", 16, 0, 3.2);
  m_h_WDeltaPhiCorrection2Jet->SetDirectory(0);
  m_h_WDeltaPhiCorrection3Jet = new TH1F("WDeltaPhiCorr3Jet","WDeltaPhiCorr3Jet", 16, 0, 3.2);
  m_h_WDeltaPhiCorrection3Jet->SetDirectory(0);

  // numbers from Garabed. 26/05/2013
  Float_t a_wlcorr2Jet[16] = { -0.15044, -0.137197, -0.105746, -0.112105, -0.097855, 
    -0.096983, -0.064647, -0.041897, -0.02896, -0.026313, 0.01495, 0.03721, 0.05588, 0.07741, 
    0.0809799, 0.06379 }; 
  Utils::FillTH1F(16, a_wlcorr2Jet, m_h_WDeltaPhiCorrection2Jet, m_allHists);

  Float_t a_wlcorr3Jet[16] = { -0.092645, -0.093605, -0.074694, -0.055558, -0.045499, 
    -0.055228, -0.059025, -0.026597, -0.024518, -0.00629598, 0.01531, 0.04161, 0.04169, 0.02874, 
    0.03457, 0.0127701 };
  Utils::FillTH1F(16, a_wlcorr3Jet, m_h_WDeltaPhiCorrection3Jet, m_allHists);

  // parameterized line for 2 and 3 Jets
  m_f_WDPhiCorr = new TF1("f_WDPhiCorr","([0] + [1] * x) * (x<=2.52) + ([2] + [3]*x + [4]*x*x) * (x>2.52) - 1", 0, 3.2);
  m_f_WDPhiCorr->SetParameter(0, 0.820954);
  m_f_WDPhiCorr->SetParameter(1, 0.0965);
  m_f_WDPhiCorr->SetParameter(2, -0.130413);
  m_f_WDPhiCorr->SetParameter(3, +0.849834);
  m_f_WDPhiCorr->SetParameter(4, -0.149133);
  Utils::SaveHist(m_f_WDPhiCorr, m_allHists);


  // Z, backgrounds DeltaPhi corrections
  m_h_ZDeltaPhiCorrection = new TH1F("ZDeltaPhiCorr","ZDeltaPhiCorr", 16, 0, 3.2);
  m_h_ZDeltaPhiCorrection->SetDirectory(0);

  // numbers from Kevin. 12/04/2013
  Float_t a_zlcorr[16] = { -0.0800548, -0.0816269, -0.0432947, -0.0479725, -0.0516307,
    -0.0438293, -0.0204907, 0.00574154, 0.0169727, 0.057972, 0.0232869, 0.0621223, 0.0584892,
    0.0631624, 0.0652384, 0.0596382 };
  Utils::FillTH1F(16, a_zlcorr, m_h_ZDeltaPhiCorrection, m_allHists);

  // parameterized line for 2 and 3 Jets
  // f(dphi) = (Norm*0.9189 + 0.0675*dPhi)
  m_f_ZDPhiCorr = new TF1("f_ZDPhiCorr","[0] + [1] * x - 1", 0, 3.2);
  m_f_ZDPhiCorr->SetParameter(0, 0.880);
  m_f_ZDPhiCorr->SetParameter(1, 0.0675);
  Utils::SaveHist(m_f_ZDPhiCorr, m_allHists);

  // top pT correction. Yuji 18/05/13
  // From https://cds.cern.ch/record/1470588/ Figure 46
  // update on 27/05/13 for error to be 50% of the correction
  

  Float_t topPtCorr[7] = { 0.05128, 0.0288, -0.000898004, -0.024253, -0.08489, -0.170377, -0.247117 }; 
  Float_t topPtCorrBins[8]  = { 0, 50.e3, 100.e3, 150.e3, 200.e3, 250.e3, 350.e3, 800.e3 };

  /*
  float normTopPt = 100000./99833.4;
  for( int i=0; i<7; i++) { 
    topPtCorr[i] *= normTopPt;
  }
  */

  m_h_topPtCorrection = new TH1F("topPtCorrection", "topPtCorrection", 7, topPtCorrBins);
  m_h_topPtCorrection->SetDirectory(0);
  Utils::FillTH1F( 7, topPtCorr, m_h_topPtCorrection, m_allHists );

  /*********************************************
   *
   *    SYSTEMATICS
   *    These should be applied to the nominal
   *
   *    Below the histograms which contain the
   *    values of the correction are created
   *
  *********************************************/

  m_h_SysTheoryWHlvbbPt = new TH1F("SysTheoryWHlvbbPt", "SysTheoryWHlvbbPt", 95, 25.e3, 500.e3);
  m_h_SysTheoryWHlvbbPt->SetDirectory(0);
  m_h_SysTheoryZHllbbPt = new TH1F("SysTheoryZHllbbPt", "SysTheoryZHllbbPt", 95, 25.e3, 500.e3);
  m_h_SysTheoryZHllbbPt->SetDirectory(0);
  m_h_SysTheoryZHvvbbPt = new TH1F("SysTheoryZHvvbbPt", "SysTheoryZHvvbbPt", 95, 25.e3, 500.e3);
  m_h_SysTheoryZHvvbbPt->SetDirectory(0);
  if(m_seven) {
    Float_t hw7_errors[95] = {0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.0201801, 0.0207736, 0.0213758, 0.0219865, 0.0226059, 0.0232338, 0.0238704, 0.0245155, 0.0251693, 0.0258317, 0.0265027, 0.0271822, 0.0278704, 0.0285672, 0.0292726, 0.0299866, 0.0307092, 0.0314403, 0.0321801, 0.0329285, 0.0336855, 0.0344511, 0.0352254, 0.0360082, 0.0367996, 0.0375996, 0.0384082, 0.0392254, 0.0400513, 0.0408857, 0.0417287, 0.0425803, 0.0434406, 0.0443094, 0.0451869, 0.0460729, 0.0469675, 0.0478708, 0.0487827, 0.0497031, 0.0506322, 0.0515698, 0.0525161, 0.053471, 0.0544344, 0.0554065, 0.0563872, 0.0573764, 0.0583743, 0.0593808, 0.0603959, 0.0614196, 0.0624519, 0.0634928, 0.0645423, 0.0656004};
    Utils::FillTH1F(95, hw7_errors, m_h_SysTheoryWHlvbbPt, m_allHists);
    Float_t hll7_errors[95] = {0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.0203477, 0.0209749, 0.0216116, 0.0222579, 0.0229137, 0.023579, 0.0242538, 0.0249381, 0.025632, 0.0263354, 0.0270483, 0.0277707, 0.0285026, 0.0292441, 0.0299951, 0.0307556, 0.0315256, 0.0323051, 0.0330942, 0.0338928, 0.0347009, 0.0355185, 0.0363457, 0.0371823, 0.0380285, 0.0388842, 0.0397495, 0.0406242, 0.0415085, 0.0424023, 0.0433056, 0.0442184, 0.0451408, 0.0460727, 0.0470141, 0.047965, 0.0489254, 0.0498954, 0.0508749, 0.0518639, 0.0528624, 0.0538704};
    Utils::FillTH1F(95, hll7_errors, m_h_SysTheoryZHllbbPt, m_allHists);
    Float_t hnn7_errors[95] = {0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.0202857, 0.0208312, 0.0213839, 0.0219438, 0.022511, 0.0230854, 0.023667, 0.0242559, 0.024852};
    Utils::FillTH1F(95, hnn7_errors, m_h_SysTheoryZHvvbbPt, m_allHists);
  }
  else if(m_eight) {
    Float_t	hw8_errors[95] = {0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.0201193, 0.0207066, 0.0213024, 0.0219067, 0.0225194, 0.0231405, 0.0237701, 0.0244082, 0.0250547, 0.0257096, 0.026373, 0.0270449, 0.0277252, 0.0284139, 0.0291111, 0.0298168, 0.0305309, 0.0312534, 0.0319844, 0.0327239, 0.0334718, 0.0342281, 0.0349929, 0.0357662, 0.0365479, 0.037338, 0.0381367, 0.0389437, 0.0397592, 0.0405832, 0.0414156, 0.0422564, 0.0431057, 0.0439635, 0.0448297, 0.0457044, 0.0465875, 0.047479, 0.048379, 0.0492875, 0.0502044, 0.0511298, 0.0520636, 0.0530058, 0.0539565, 0.0549157, 0.0558833, 0.0568594, 0.0578439, 0.0588369, 0.0598383, 0.0608481, 0.0618664, 0.0628932, 0.0639284, 0.0649721};
    Utils::FillTH1F(95, hw8_errors, m_h_SysTheoryWHlvbbPt, m_allHists);
    Float_t hll8_errors[95] = {0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.0205646, 0.0211945, 0.021834, 0.022483, 0.0231415, 0.0238095, 0.024487, 0.025174, 0.0258705, 0.0265765, 0.027292, 0.028017, 0.0287516, 0.0294956, 0.0302491, 0.0310122, 0.0317847, 0.0325667, 0.0333583, 0.0341594, 0.0349699, 0.03579, 0.0366195, 0.0374586, 0.0383072, 0.0391653, 0.0400329, 0.0409099, 0.0417965, 0.0426926, 0.0435982, 0.0445134, 0.045438, 0.0463721, 0.0473157, 0.0482688, 0.0492315, 0.0502036, 0.0511852, 0.0521764, 0.053177};
    Utils::FillTH1F(95, hll8_errors, m_h_SysTheoryZHllbbPt, m_allHists);
    Float_t hnn8_errors[95] = {0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.0202975, 0.0208415, 0.0213928, 0.0219513, 0.0225169, 0.0230898, 0.0236698, 0.0242571, 0.0248515};
    Utils::FillTH1F(95, hnn8_errors, m_h_SysTheoryZHvvbbPt, m_allHists);
  }

  m_h_SysStopPt = new TH1F("SysStopPt", "SysStopPt", 5, pTbins);
  m_h_SysStopPt->SetDirectory(0);
  m_h_SysWbbPtW = new TH1F("SysWbbPtW", "SysWbbPtW", 5, pTbins);
  m_h_SysWbbPtW->SetDirectory(0);
  m_h_SysWccPtW = new TH1F("SysWccPtW", "SysWccPtW", 5, pTbins);
  m_h_SysWccPtW->SetDirectory(0);
  m_h_SysWllPtW = new TH1F("SysWllPtW", "SysWllPtW", 5, pTbins);
  m_h_SysWllPtW->SetDirectory(0);
  m_h_SysZbbPtZ = new TH1F("SysZbbPtZ", "SysZbbPtZ", 5, pTbins);
  m_h_SysZbbPtZ->SetDirectory(0);
  m_h_SysZccPtZ = new TH1F("SysZccPtZ", "SysZccPtZ", 5, pTbins);
  m_h_SysZccPtZ->SetDirectory(0);
  m_h_SysZllPtZ = new TH1F("SysZllPtZ", "SysZllPtZ", 5, pTbins);
  m_h_SysZllPtZ->SetDirectory(0);

  Float_t a_SysStopPt[5] = { 0.02, 0.00, 0.01, -0.01, -0.05};
  Utils::FillTH1F(5, a_SysStopPt, m_h_SysStopPt, m_allHists);
  Float_t a_SysWbbPtW[5] = { 0.02, 0.00, 0.01, -0.01, -0.05}; // same as stop
  Utils::FillTH1F(5, a_SysWbbPtW, m_h_SysWbbPtW, m_allHists);
  Float_t a_SysWccPtW[5] = { 0.02, 0.00, 0.01, -0.01, -0.05}; // same as stop
  Utils::FillTH1F(5, a_SysWccPtW, m_h_SysWccPtW, m_allHists);
  Float_t a_SysWllPtW[5] = { 0.02, 0.00, 0.01, -0.01, -0.05}; // same as stop
  Utils::FillTH1F(5, a_SysWllPtW, m_h_SysWllPtW, m_allHists);
  Float_t a_SysZbbPtW[5] = { 0.00, -0.01, 0.00, 0.00, -0.03};
  Utils::FillTH1F(5, a_SysZbbPtW, m_h_SysZbbPtZ, m_allHists);
  Float_t a_SysZccPtW[5] = { 0.00, -0.01, 0.00, 0.00, -0.03}; // same as Zbb
  Utils::FillTH1F(5, a_SysZccPtW, m_h_SysZccPtZ, m_allHists);
  Float_t a_SysZllPtW[5] = { 0.00, -0.01, 0.00, 0.00, -0.03}; // same as Zbb
  Utils::FillTH1F(5, a_SysZllPtW, m_h_SysZllPtZ, m_allHists);


  // Continuus systematics

  m_f_SysZbbMbb = new TF1("f_SysZbbMbb","[0] * (x/1.e3 - [1])", 0, pTbins[5]);
  m_f_SysZbbMbb->SetParameter(0, 0.001);
  m_f_SysZbbMbb->SetParameter(1, 100.);

  m_f_SysWbbMbb = new TF1("f_SysWbbMbb","[0] + [1] * x/1.e3", 0, pTbins[5]);
  m_f_SysWbbMbb->SetParameter(0, 0.19);
  m_f_SysWbbMbb->SetParameter(1, -0.0017);

  m_f_SysTopMbb = new TF1("f_SysTopMbb","[0] + [1] * x/1.e3", 0, pTbins[5]);
  m_f_SysTopMbb->SetParameter(0, 0.05);
  m_f_SysTopMbb->SetParameter(1, -3.4e-4);

  m_f_SysStopMbb = new TF1("f_SysStopMbb","[0] + [1] * x/1.e3", 0, pTbins[5]);
  m_f_SysStopMbb->SetParameter(0, 0.19); // same as Wbb
  m_f_SysStopMbb->SetParameter(1, -0.0017);

  m_f_SysWMbb = new TF1("f_SysWMbb","[0] + [1] * TMath::Log(x) + [2] * pow(TMath::Log(x), 2)", 0, pTbins[5]);
  m_f_SysWMbb->SetParameter(0, -2.3);
  m_f_SysWMbb->SetParameter(1, 3.1e-01);
  m_f_SysWMbb->SetParameter(2, -9.7e-03);

  m_f_SysZMbb = new TF1("f_SysZMbb","[0] * (x/1.e3 - [1])", 0, pTbins[5]);
  m_f_SysZMbb->SetParameter(0, 0.001); // same as Zbb
  m_f_SysZMbb->SetParameter(1, 100.);

  Utils::SaveHist(m_f_SysZbbMbb, m_allHists);
  Utils::SaveHist(m_f_SysWbbMbb, m_allHists);
  Utils::SaveHist(m_f_SysTopMbb, m_allHists);
  Utils::SaveHist(m_f_SysStopMbb, m_allHists);
  Utils::SaveHist(m_f_SysWMbb, m_allHists);
  Utils::SaveHist(m_f_SysZMbb, m_allHists);

  if(m_draw) {
    TString fname("CorrsAndSysts_");
    if(m_zero) {  fname.Append("Zero"); }
    if(m_one)  {  fname.Append("One");  }
    if(m_two)  {  fname.Append("Two");  }
    fname.Append("Lep_");
    if(m_seven) { fname.Append("7"); }
    if(m_eight) { fname.Append("8"); }
    fname.Append("TeV.root");
    WriteHistsToFile(fname);
  }


} // Initialize

CAS::EventType CorrsAndSysts::GetEventType(TString name) {
  if( m_typeNames.find(name.Data()) == m_typeNames.end() ) {
    std::cout << "CorrsAndSysts::ERROR - unknown event type " << name << std::endl;
    exit(-1);
  }
  return m_typeNames[name.Data()];
} // GetEventType

CAS::SysBin CorrsAndSysts::GetSysBin(float vpt) {
  if(vpt < pTbins[0]) {
    std::cout << "CorrsAndSysts::ERROR - V pT " << vpt << " is smaller than lowest bin boundary " <<  pTbins[0] << std::endl;
  }
  if(vpt < pTbins[1]) { return CAS::Bin0; }
  if(vpt < pTbins[2]) { return CAS::Bin1; }
  if(vpt < pTbins[3]) { return CAS::Bin2; }
  if(vpt < pTbins[4]) { return CAS::Bin3; }
  return CAS::Bin4;

} // GetSysBin

/*********************************************
 *
 *  CORRECTIONS continued - functions below
 *
 *********************************************/

float CorrsAndSysts::Get_HiggsNLOEWKCorrection(CAS::EventType type, float VpT) {
  float scale=0;
  switch(type) {
    case CAS::WHlvbb:
      scale = Utils::GetScale(VpT, m_h_WHlvbbNLOEWKCorrection);
      break;
    case CAS::ZHllbb:
      scale = Utils::GetScale(VpT, m_h_ZHllbbNLOEWKCorrection);
      break;
    case CAS::ZHvvbb:
      scale = Utils::GetScale(VpT, m_h_ZHvvbbNLOEWKCorrection);
      break;
    default:
      scale=0;
      break;
  }
  return 1+scale;
}

float CorrsAndSysts::Get_BkgpTCorrection(CAS::EventType type, float VpT) {
  
  std::cout << "CorrsAndSysts::WARNING - Get_BkgpTCorrection deprecated!" << std::endl;
  return 1;

  float scale=0;
  switch(type) {
    case CAS::Wl: case CAS::Wb: case CAS::Wc: case CAS::Wcc: case CAS::stop:
      scale = Utils::GetScale(VpT, m_h_WpTCorrection);
      break;
    case CAS::Zb: case CAS::Zc: case CAS::Zl:
      scale = Utils::GetScale(VpT, m_h_ZpTCorrection);
      break;
    default:
      scale=0;
      break;
  }
  return 1+scale;
}

float CorrsAndSysts::Get_ToppTCorrection(CAS::EventType type, float avgTopPt) {
  if (type != CAS::ttbar) { return 1; }
  float scale = Utils::GetScale(avgTopPt, m_h_topPtCorrection);
  return 1+scale;
}

float CorrsAndSysts::Get_BkgDeltaPhiCorrection(CAS::EventType type, float DeltaPhi, int njet) {
  DeltaPhi = fabs(TVector2::Phi_mpi_pi(DeltaPhi));
  float scale=0;
  switch(type) {
    case CAS::Wl:
    case CAS::Wc:
    case CAS::Wcc:
    case CAS::Wb:
      /*
      if(njet == 2) {
        scale = Utils::GetScale(DeltaPhi, m_h_WDeltaPhiCorrection2Jet);
      } else {
        scale = Utils::GetScale(DeltaPhi, m_h_WDeltaPhiCorrection3Jet);
      }
      */
      scale = m_f_WDPhiCorr->Eval(DeltaPhi);
      break;
    case CAS::Zl:
    case CAS::Zc:
    case CAS::Zb:
      //scale = Utils::GetScale(DeltaPhi, m_h_ZDeltaPhiCorrection);
      scale = m_f_ZDPhiCorr->Eval(DeltaPhi);
      break;
    default:
      scale=0;
      break;
  }
  return 1+scale;
}

/*********************************************
 *
 *  SYSTEMATICS continued - functions below
 *
 *********************************************/


float CorrsAndSysts::Get_SystematicWeight(CAS::EventType type, float VpT, float Mbb, float avgTopPt, float DeltaPhi, int njet, 
    CAS::Systematic sys, CAS::SysVar var, CAS::SysBin bin) {
  DeltaPhi = fabs(TVector2::Phi_mpi_pi(DeltaPhi));
  // no systematics
  if(sys == CAS::Nominal)
    return 1;

  if(sys == CAS::PTBINNED || sys == CAS::CONTINUOUS) {
    std::cout << "CorrsAndSysts::ERROR Using a systematic enum which should not be used" << std::endl;
    exit(-1);
  }

  if(bin == CAS::None) {
    std::cout << "CorrsAndSysts: no indication of type of binning given for systematics ! Exiting..." << std::endl;
    exit(-1);
  }

  // sanity check: binned / continuous systematics
  if(sys < CAS::CONTINUOUS && bin == CAS::Any) {
    std::cout << "CorrsAndSysts: asked no binning for a systematic which is binned ! Exiting..." << std::endl;
    exit(-1);
  }
  if(sys >= CAS::CONTINUOUS && sys < CAS::LAST && bin != CAS::Any) {
    std::cout << "CorrsAndSysts: asked specific bin for a systematic which is not binned ! Exiting..." << std::endl;
    exit(-1);
  }


  // for binned systematics, check if the pT bin matches. else return 1
  if(sys > CAS::PTBINNED && sys < CAS::CONTINUOUS) {
    int ptbin = m_h_WpTCorrection->FindBin(VpT) - 1;
    if(ptbin != bin)
      return 1;
  }

  float scale = 0;

  int sgn = 2*var-1;
  
  float unc_scale = 0.5;

  switch(sys) {
    case CAS::SysTheoryHPt:
      switch(type) {
        case CAS::WHlvbb:
          scale = Utils::GetScale(VpT, m_h_SysTheoryWHlvbbPt);
        break;
        case CAS::ZHllbb:
          scale = Utils::GetScale(VpT, m_h_SysTheoryZHllbbPt);
        break;
        case CAS::ZHvvbb:
          scale = Utils::GetScale(VpT, m_h_SysTheoryZHvvbbPt);
        break;
        default:
          return 1;
      }
      break;

    case CAS::SysTopPt:
      if(type != CAS::ttbar) { return 1; }
      scale = Utils::GetScale(avgTopPt, m_h_topPtCorrection);
      scale = .5*scale/(1+scale); // DO is 50% of correction, UP is 150%
    break;

    case CAS::SysStopPt:
      return 1;
      if(type != CAS::stop)
        return 1;
      scale = unc_scale * m_h_SysStopPt->GetBinContent(bin+1);
    break;

    case CAS::SysWbbPtW:
      std::cout << "CorrsAndSysts::WARNING - requested systematic deprecated!" << std::endl;
      return 1;
      if(type != CAS::Wb)
        return 1;
      scale = unc_scale * m_h_SysWbbPtW->GetBinContent(bin+1);
    break;

    case CAS::SysWccPtW:
      std::cout << "CorrsAndSysts::WARNING - requested systematic deprecated!" << std::endl;
      return 1;
      if(type != CAS::Wc && type != CAS::Wcc)
        return 1;
      scale = unc_scale * m_h_SysWccPtW->GetBinContent(bin+1);
    break;

    case CAS::SysZbbPtZ:
      std::cout << "CorrsAndSysts::WARNING - requested systematic deprecated!" << std::endl;
      return 1;
      if(type != CAS::Zb)
        return 1;
      scale = unc_scale * m_h_SysZbbPtZ->GetBinContent(bin+1);
    break;

    case CAS::SysZccPtZ:
      std::cout << "CorrsAndSysts::WARNING - requested systematic deprecated!" << std::endl;
      return 1;
      if(type != CAS::Zc)
        return 1;
      scale = unc_scale * m_h_SysZccPtZ->GetBinContent(bin+1);
    break;

    case CAS::SysWllPtW:
      std::cout << "CorrsAndSysts::WARNING - requested systematic deprecated!" << std::endl;
      return 1;
      if(type != CAS::Wl)
        return 1;
      scale = unc_scale * m_h_SysWllPtW->GetBinContent(bin+1);
    break;

    case CAS::SysZllPtZ:
      std::cout << "CorrsAndSysts::WARNING - requested systematic deprecated!" << std::endl;
      return 1;
      if(type != CAS::Zl)
        return 1;
      scale = unc_scale * m_h_SysZllPtZ->GetBinContent(bin+1);
    break;

    // now continuus systematics

    case CAS::SysZbbMbb:
      if(type != CAS::Zb)
        return 1;
      scale = m_f_SysZbbMbb->Eval(Mbb);
    break;

    case CAS::SysWbbMbb:
      if(type != CAS::Wb && type != CAS::Wcc)
        return 1;
      scale = m_f_SysWbbMbb->Eval(Mbb);
    break;

    case CAS::SysWMbb:
      if(type != CAS::Wl && type != CAS::Wc)
        return 1;
      scale = m_f_SysWMbb->Eval(Mbb);
    break;

    case CAS::SysTopMbb:
      if(type != CAS::ttbar)
        return 1;
      scale = m_f_SysTopMbb->Eval(Mbb);
    break;

    case CAS::SysStopMbb:
      if(type != CAS::stop)
        return 1;
      scale = m_f_SysStopMbb->Eval(Mbb);
    break;

    case CAS::SysZMbb:
      if(type != CAS::Zl && type != CAS::Zc)
        return 1;
      scale = m_f_SysZMbb->Eval(Mbb);
    break;

    case CAS::SysWDPhi:
      if(type != CAS::Wl && type !=CAS::Wc)
        return 1;
      /*
      if(njet == 2) {
        scale = Utils::GetScale(DeltaPhi, m_h_WDeltaPhiCorrection2Jet); 
      } else {
        scale = Utils::GetScale(DeltaPhi, m_h_WDeltaPhiCorrection3Jet); 
      }
      */
      scale = m_f_WDPhiCorr->Eval(DeltaPhi);
      scale = .5*scale/(1+scale); // DO is 50% of correction, UP is 150%
    break;

    case CAS::SysWccDPhi:
      if(type != CAS::Wcc)
        return 1;
      /*
      if(njet == 2) {
        scale = Utils::GetScale(DeltaPhi, m_h_WDeltaPhiCorrection2Jet);
      } else {
        scale = Utils::GetScale(DeltaPhi, m_h_WDeltaPhiCorrection3Jet);
      }
      */
      scale = m_f_WDPhiCorr->Eval(DeltaPhi);
      scale = .5*scale/(1+scale); // DO is 50% of correction, UP is 150%
    break;

    case CAS::SysWbDPhi:
      if(type != CAS::Wb)
        return 1;
      /*
      if(njet == 2) {
        scale = Utils::GetScale(DeltaPhi, m_h_WDeltaPhiCorrection2Jet);
      } else {
        scale = Utils::GetScale(DeltaPhi, m_h_WDeltaPhiCorrection3Jet);
      }
      */
      scale = m_f_WDPhiCorr->Eval(DeltaPhi);
      scale = .5*scale/(1+scale); // DO is 50% of correction, UP is 150%
    break;

    case CAS::SysZDPhi:
      if(type != CAS::Zl)
        return 1;
      //scale = Utils::GetScale(DeltaPhi, m_h_ZDeltaPhiCorrection);
      scale = m_f_ZDPhiCorr->Eval(DeltaPhi);
      scale = .5*scale/(1+scale); // DO is 50% of correction, UP is 150%
    break;

    case CAS::SysZcDPhi:
      if(type != CAS::Zc)
        return 1;
      //scale = Utils::GetScale(DeltaPhi, m_h_ZDeltaPhiCorrection);
      scale = m_f_ZDPhiCorr->Eval(DeltaPhi);
      scale = .5*scale/(1+scale); // DO is 50% of correction, UP is 150%
    break;

    case CAS::SysZbDPhi:
      if(type != CAS::Zb)
        return 1;
      //scale = Utils::GetScale(DeltaPhi, m_h_ZDeltaPhiCorrection);
      scale = m_f_ZDPhiCorr->Eval(DeltaPhi);
      scale = .5*scale/(1+scale); // DO is 50% of correction, UP is 150%
    break;

    default:
      return 1;
    break;
  }

  // generic case: symmetric uncertainties
  scale*=sgn;

  return 1+scale;

} // Get_SystematicWeight

// if using this function
//  need to have Up or Do as the last two characters of the syst name
//  the string Bin in the name if necessary
float CorrsAndSysts::Get_SystematicWeight(CAS::EventType type, float VpT, float Mbb, float avgTopPt, float DeltaPhi, int njet, TString sysName) {
  CAS::Systematic sys;
  CAS::SysBin bin;
  CAS::SysVar var;
  GetSystFromName(sysName, sys, bin, var);
  return Get_SystematicWeight(type, VpT, Mbb, avgTopPt, DeltaPhi, njet, sys, var, bin);
}

// if using this function
//  need to have Up or Do as the last two characters of the syst name
//  the string Bin in the name if necessary
void CorrsAndSysts::GetSystFromName(TString name, CAS::Systematic& sys, CAS::SysBin& bin, CAS::SysVar& var) {
  var = m_varFromNames[name(name.Length()-2, 2).Data()];
  name.Remove(name.Length()-2);
  if(name.Contains("Bin")) {
    bin = m_binFromNames[name(name.Length()-4, 4).Data()];
    name.Remove(name.Length()-4);
  }
  else {
    bin = CAS::Any;
  }
  sys = m_systFromNames[name.Data()];
}

void CorrsAndSysts::WriteHistsToFile(TString fname) {
  TFile *file = new TFile(fname,"RECREATE");
  for(std::map<TString,TObject*>::iterator hists=m_allHists.begin(); hists!=m_allHists.end(); hists++) {
    hists->second->Write();
  }
  file->Close();
  delete file;
} // WriteHistsToFile



/*
 *
 *  UTILITY FUNCTIONS
 *
 */

namespace Utils {
  TH1F* BuildTH1F(std::vector<Double_t> contents, TString hname, float min, float max, std::map<TString, TObject*>& hists) {
    TH1F* tmp = new TH1F(hname,hname,contents.size(),min,max);
    for(unsigned int i = 1; i<contents.size()+1; i++) {
      tmp->SetBinContent(i, contents[i-1]);
    }
    if(tmp->GetBinContent( tmp->GetNbinsX()+1 ) == 0) {
      tmp->SetBinContent( tmp->GetNbinsX()+1, tmp->GetBinContent( tmp->GetNbinsX() ) );
    }
    SaveHist(tmp,hists);
    return tmp;
  }

  void  FillTH1F(std::vector<Float_t> contents, TH1F* h, std::map<TString, TObject*>& hists) {
    if( contents.size() != static_cast<unsigned int>(h->GetNbinsX()) ){
      std::cout << "CorrsAndSysts: filling the histogram " << h->GetName() << " with a wrong number of bins" << std::endl;
      exit(-1);
    }
    for(int i=0; i<h->GetNbinsX(); i++) {
      h->SetBinContent(i+1, contents[i]);
    }
    if(h->GetBinContent( h->GetNbinsX()+1 ) == 0) {
      h->SetBinContent( h->GetNbinsX()+1, h->GetBinContent( h->GetNbinsX() ) );
    }
    SaveHist(h,hists);
  }

  void  FillTH1F(int len, Float_t* contents, TH1F* h, std::map<TString, TObject*>& hists) {
    if( len != h->GetNbinsX() ){
      std::cout << "CorrsAndSysts: filling the histogram " << h->GetName() << " with a wrong number of bins" << std::endl;
      exit(-1);
    }
    for(int i=0; i<h->GetNbinsX(); i++) {
      h->SetBinContent(i+1, contents[i]);
    }
    if(h->GetBinContent( h->GetNbinsX()+1 ) == 0) {
      h->SetBinContent( h->GetNbinsX()+1, h->GetBinContent( h->GetNbinsX() ) );
    }
    SaveHist(h,hists);
  }

  void SaveHist(TObject* h, std::map<TString, TObject*>& hists) {
    if(hists.find(h->GetName()) != hists.end()) {
      std::cout << "CorrsAndSysts::ERROR - non-unique name of histogram/function is being used - please correct" << std::endl;
      exit(-1);
    }
    hists[h->GetName()] = h;
  } //SaveHist

  inline float GetScale(float value, TH1F* h) {
    return h->GetBinContent( h->FindBin(value) );
  }

}





  // Systematics on distributions
//  float Get_SystematicWeight(CAS::EventType type, float VpT, float Mbb, float avgTopPt, float DeltaPhi, int njet, CAS::Systematic sys=CAS::Nominal, CAS::SysVar var=CAS::Up, CAS::SysBin bin=CAS::None);
//  float Get_SystematicWeight(CAS::EventType type, float VpT, float Mbb, float avgTopPt, float DeltaPhi, int njet, TString sysName);
/*
  inline float Get_SystematicWeight(TString evtType, float VpT, float Mbb, float avgTopPt, float DeltaPhi, int njet, CAS::Systematic sys, CAS::SysVar var, CAS::SysBin bin)
  { return Get_SystematicWeight(m_typeNames[evtType.Data()], VpT, Mbb, avgTopPt, DeltaPhi, njet, sys, var, bin); }

  inline float Get_SystematicWeight(TString evtType, float VpT, float Mbb, float avgTopPt, float DeltaPhi, int njet, TString sysName)
  { return Get_SystematicWeight(m_typeNames[evtType.Data()], VpT, Mbb, avgTopPt, DeltaPhi, njet, sysName); }
*/

//void (Utils::*FillTH1Fx1)(std::vector<Float_t>, ROOT::TH1F*, std::map<TString, ROOT::TObject*>&) = &Utils::FillTH1F;
//void (Utils::*FillTH1Fx2)(int, Float_t*, ROOT::TH1F*, std::map<TString, ROOT::TObject*>&) = &Utils::FillTH1F;



float (CorrsAndSysts::*Get_HiggsNLOEWKCorrectionx1)(CAS::EventType, float) = &CorrsAndSysts::Get_HiggsNLOEWKCorrection;
float (CorrsAndSysts::*Get_HiggsNLOEWKCorrectionx2)(TString, float) = &CorrsAndSysts::Get_HiggsNLOEWKCorrection; //inline
float (CorrsAndSysts::*Get_BkgpTCorrectionx1)(CAS::EventType, float) = &CorrsAndSysts::Get_BkgpTCorrection;
float (CorrsAndSysts::*Get_BkgpTCorrectionx2)(TString, float) = &CorrsAndSysts::Get_BkgpTCorrection;//inline
float (CorrsAndSysts::*Get_ToppTCorrectionx1)(CAS::EventType, float) = &CorrsAndSysts::Get_ToppTCorrection;
float (CorrsAndSysts::*Get_ToppTCorrectionx2)(TString, float) = &CorrsAndSysts::Get_ToppTCorrection;//inline
float (CorrsAndSysts::*Get_BkgDeltaPhiCorrectionx1)(CAS::EventType, float, int) = &CorrsAndSysts::Get_BkgDeltaPhiCorrection;
float (CorrsAndSysts::*Get_BkgDeltaPhiCorrectionx2)(TString, float, int) = &CorrsAndSysts::Get_BkgDeltaPhiCorrection;//inline
//float (CorrsAndSysts::*Get_SystematicWeightx1)(CAS::EventType, float, float, float, float, int, CAS::Systematic, CAS::SysVar, CAS::SysBin) = &CorrsAndSysts::Get_SystematicWeight; // default values need to be included!
float (CorrsAndSysts::*Get_SystematicWeightx2)(CAS::EventType, float, float, float, float, int, TString) = &CorrsAndSysts::Get_SystematicWeight;
float (CorrsAndSysts::*Get_SystematicWeightx3)(TString, float, float, float, float, int, CAS::Systematic, CAS::SysVar, CAS::SysBin) = &CorrsAndSysts::Get_SystematicWeight; //inline
float (CorrsAndSysts::*Get_SystematicWeightx4)(TString, float, float, float, float, int, TString) = &CorrsAndSysts::Get_SystematicWeight; //inline




BOOST_PYTHON_MODULE(CorrsAndSysts_ext)
{
  {
  scope CAS = class_<DummyCAS>("CAS");
  enum_<CAS::EventType>("EventType")
    .value("WHlvbb",CAS::WHlvbb)
    .value("ZHllbb",CAS::ZHllbb)
    .value("ZHvvbb",CAS::ZHvvbb)
    .value("Wb",CAS::Wb)
    .value("Wc",CAS::Wc)
    .value("Wcc",CAS::Wcc)
    .value("Wl",CAS::Wl)
    .value("Zb",CAS::Zb)
    .value("Zc",CAS::Zc)
    .value("Zl",CAS::Zl)
    .value("ttbar",CAS::ttbar)
    .value("stop",CAS::stop)
    .value("diboson",CAS::diboson)
    .value("NONAME",CAS::NONAME);

  enum_<CAS::SysVar>("SysVar")
    .value("Do",CAS::Do)
    .value("Up",CAS::Up);

  enum_<CAS::SysBin>("SysBin")
    .value("None",CAS::None)                            // default
    .value("Any",CAS::Any)                             // means no binning -> used for continuous systematics
    .value("Bin0",CAS::Bin0)
    .value("Bin1",CAS::Bin1) 
    .value("Bin2",CAS::Bin2)
    .value("Bin3",CAS::Bin3)
    .value("Bin4",CAS::Bin4)     // pT bins for binned systematics
    .value("NOTDEFINED",CAS::NOTDEFINED);


  enum_<CAS::Systematic>("Systematic") // only systematics affecting the shape are relevant to this tool
    .value("Nominal",CAS::Nominal)
    // the following are binned in pT (5 bins") independent systematics)
    .value("PTBINNED",CAS::PTBINNED)
    .value("SysStopPt",CAS::SysStopPt)
    .value("SysWbbPtW",CAS::SysWbbPtW)
    .value("SysWccPtW",CAS::SysWccPtW)
    .value("SysZbbPtZ",CAS::SysZbbPtZ)
    .value("SysZccPtZ",CAS::SysZccPtZ)
    .value("SysWllPtW",CAS::SysWllPtW)
    .value("SysZllPtZ",CAS::SysZllPtZ)
    // the following are continuous (thus correlated in pT)
    .value("CONTINUOUS",CAS::CONTINUOUS)
    .value("SysTheoryHPt",CAS::SysTheoryHPt)
    .value("SysTopPt",CAS::SysTopPt)
    .value("SysTopMbb",CAS::SysTopMbb)
    .value("SysStopMbb",CAS::SysStopMbb)
    .value("SysZbbMbb",CAS::SysZbbMbb)
    .value("SysWbbMbb",CAS::SysWbbMbb)
    .value("SysZMbb",CAS::SysZMbb)
    .value("SysWMbb",CAS::SysWMbb)
    .value("SysWDPhi",CAS::SysWDPhi)
    .value("SysWccDPhi",CAS::SysWccDPhi)
    .value("SysWbDPhi",CAS::SysWbDPhi)
    .value("SysZDPhi",CAS::SysZDPhi)
    .value("SysZcDPhi",CAS::SysZcDPhi)
    .value("SysZbDPhi",CAS::SysZbDPhi)
    .value("LAST",CAS::LAST);
  }  
  //scope b = class_<CorrsAndSysts>("b");



  scope c = class_<CorrsAndSysts>("CorrsAndSysts",init<TString,bool>())
    .def(init<int, int, bool>())
    //.def("Initialize", &CorrsAndSysts::Initialize)
    .def("SetDebug", &CorrsAndSysts::SetDebug)//inline
    .def("WriteHistsToFile", &CorrsAndSysts::WriteHistsToFile)
    .def("Get_HiggsNLOEWKCorrection", Get_HiggsNLOEWKCorrectionx1)
    .def("Get_HiggsNLOEWKCorrection", Get_HiggsNLOEWKCorrectionx2)//inline
    .def("Get_BkgpTCorrection", Get_BkgpTCorrectionx1)
    .def("Get_BkgpTCorrection", Get_BkgpTCorrectionx2)//inline
    .def("Get_ToppTCorrection", Get_ToppTCorrectionx1)
    .def("Get_ToppTCorrection", Get_ToppTCorrectionx2)//inline
    .def("Get_BkgDeltaPhiCorrection", Get_BkgDeltaPhiCorrectionx1)
    .def("Get_BkgDeltaPhiCorrection", Get_BkgDeltaPhiCorrectionx2)
    .def("Get_SystematicWeight", &CorrsAndSysts::Get_SystematicWeight0)
    .def("Get_SystematicWeight", &CorrsAndSysts::Get_SystematicWeight1)
    .def("Get_SystematicWeight", &CorrsAndSysts::Get_SystematicWeight2)
    .def("Get_SystematicWeight", &CorrsAndSysts::Get_SystematicWeight3)
    .def("Get_SystematicWeight", Get_SystematicWeightx2)
    .def("Get_SystematicWeight", Get_SystematicWeightx3)//inline
    .def("Get_SystematicWeight", Get_SystematicWeightx4)//inline
    .def("Get_SystName", &CorrsAndSysts::GetSystName)//inline
    .def("GetSystFromName", &CorrsAndSysts::GetSystFromName)//inline
    .def("GetEventType", &CorrsAndSysts::GetEventType)
    .def("GetSysBin", &CorrsAndSysts::GetSysBin)
    /*.def_readwrite("m_debug", &CorrsAndSysts::m_debug)
    .def_readwrite("m_draw", &CorrsAndSysts::m_draw)  
    .def_readwrite("m_zero", &CorrsAndSysts::m_zero)  
    .def_readwrite("m_one", &CorrsAndSysts::m_one)  
    .def_readwrite("m_two", &CorrsAndSysts::m_two)  
    .def_readwrite("m_seven", &CorrsAndSysts::m_seven)  
    .def_readwrite("m_eight", &CorrsAndSysts::m_eight)  
    .def_readwrite("pTbins", &CorrsAndSysts::pTbins)*/
    //.def_readwrite("m_typeNames", &CorrsAndSysts::m_typeNames)
    //.def_readwrite("m_systNames", &CorrsAndSysts::m_systNames)
    //.def_readwrite("m_varNames", &CorrsAndSysts::m_varNames)
    //.def_readwrite("m_binNames", &CorrsAndSysts::m_binNames)
    //.def_readwrite("m_systFromNames", &CorrsAndSysts::m_systFromNames)
    //.def_readwrite("m_varFromNames", &CorrsAndSysts::m_varFromNames)
    //.def_readwrite("m_binFromNames", &CorrsAndSysts::m_binFromNames)
    //.def_readwrite("m_allHists", &CorrsAndSysts::m_allHists)
    /*.def_readwrite("m_h_WHlvbbNLOEWKCorrection", &CorrsAndSysts::m_h_WHlvbbNLOEWKCorrection)
    .def_readwrite("m_h_ZHllbbNLOEWKCorrection", &CorrsAndSysts::m_h_ZHllbbNLOEWKCorrection)
    .def_readwrite("m_h_ZHvvbbNLOEWKCorrection", &CorrsAndSysts::m_h_ZHvvbbNLOEWKCorrection)
    .def_readwrite("m_h_WpTCorrection", &CorrsAndSysts::m_h_WpTCorrection)
    .def_readwrite("m_h_ZpTCorrection", &CorrsAndSysts::m_h_ZpTCorrection)
    .def_readwrite("m_h_WDeltaPhiCorrection2Jet", &CorrsAndSysts::m_h_WDeltaPhiCorrection2Jet)
    .def_readwrite("m_h_WDeltaPhiCorrection3Jet", &CorrsAndSysts::m_h_WDeltaPhiCorrection3Jet)
    .def_readwrite("m_h_ZDeltaPhiCorrection", &CorrsAndSysts::m_h_ZDeltaPhiCorrection)
    .def_readwrite("m_h_topPtCorrection", &CorrsAndSysts::m_h_topPtCorrection)
    */
    // binned systematics
    /*.def_readwrite("m_h_SysWbbPtW", &CorrsAndSysts::m_h_SysWbbPtW)
    .def_readwrite("m_h_SysStopPt", &CorrsAndSysts::m_h_SysStopPt)
    .def_readwrite("m_h_SysWccPtW", &CorrsAndSysts::m_h_SysWccPtW)
    .def_readwrite("m_h_SysWllPtW", &CorrsAndSysts::m_h_SysWllPtW)
    .def_readwrite("m_h_SysZbbPtZ", &CorrsAndSysts::m_h_SysZbbPtZ)
    .def_readwrite("m_h_SysZccPtZ", &CorrsAndSysts::m_h_SysZccPtZ)
    .def_readwrite("m_h_SysZllPtZ", &CorrsAndSysts::m_h_SysZllPtZ)
    
    // continuous systematics
    .def_readwrite("m_h_SysTheoryWHlvbbPt", &CorrsAndSysts::m_h_SysTheoryWHlvbbPt)
    .def_readwrite("m_h_SysTheoryZHllbbPt", &CorrsAndSysts::m_h_SysTheoryZHllbbPt)
    .def_readwrite("m_h_SysTheoryZHvvbbPt", &CorrsAndSysts::m_h_SysTheoryZHvvbbPt)
    .def_readwrite("m_f_WDPhiCorr", &CorrsAndSysts::m_f_WDPhiCorr)
    .def_readwrite("m_f_ZDPhiCorr", &CorrsAndSysts::m_f_ZDPhiCorr)
    .def_readwrite("m_f_SysZbbMbb", &CorrsAndSysts::m_f_SysZbbMbb)
    .def_readwrite("m_f_SysWbbMbb", &CorrsAndSysts::m_f_SysWbbMbb)
    .def_readwrite("m_f_SysTopMbb", &CorrsAndSysts::m_f_SysTopMbb)
    .def_readwrite("m_f_SysStopMbb", &CorrsAndSysts::m_f_SysStopMbb)
    .def_readwrite("m_f_SysWMbb", &CorrsAndSysts::m_f_SysWMbb)
    .def_readwrite("m_f_SysZMbb", &CorrsAndSysts::m_f_SysZMbb)*/

;

    
  /*scope utils = class_<Utils>("Utils")
    .def("BuildTH1F", &Utils::BuildTH1F)
    .def("FillTH1F", &Utils::FillTH1Fx1)
    .def("FillTH1F", &Utils::FillTH1Fx2)
    .def("GetScale", &Utils::GetScale)//inline
    ;//.def("reverseMap")*/




  // use TH* to store weights ; seems easier to maintain if ever we need e.g 2-d corrections
  // corrections


};
