g++ -c -fPIC -I/usr/include/python2.7 -I/home/tim/root/include -I./ HistoTransform.cpp -o HistoTransform.o

g++ -shared -Wl,-soname,HistoTransform_ext.so -o HistoTransform_ext.so HistoTransform.o -lpython2.7 -lboost_python -lPyROOT -L/home/tim/root/lib -lCore -lRIO -lTree -lHist -lPhysics

#g++ -fPIC HistoTransform.cpp -lpython2.7 -lboost_python -lPyROOT -lCore -lRIO -lTree -lHist -lPhysics -L/home/tim/root/lib -I./ -I/home/tim/root/include -I/usr/include/python2.7 -o HistoTransform.so -shared