export AtlasSetup=/afs/cern.ch/atlas/software/dist/AtlasSetup
export testarea=/afs/cern.ch/work/t/tibristo/TauDPD/workspace/
source $AtlasSetup/scripts/asetup.sh 17.2.3.7.1 --testarea $testarea

Reco_trf.py inputAODFile=/afs/cern.ch/work/t/tibristo/TauDPD/mc12_8TeV.146637.PowHegPythia8_AU2CT10_ggHtautaulh_MA150TB20.merge.AOD.e1571_s1499_s1504_r3658_r3549_tid01004667_00/AOD.01004667._000010.pool.root.1 autoConfiguration=everything outputNTUP_TAUFile=/afs/cern.ch/work/t/tibristo/TauDPD/NTUP_TAU_MSSM_AOD_10_2.root