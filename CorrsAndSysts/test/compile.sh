g++ -c -fPIC -I/usr/include/python2.7 -I/home/tim/root/include CorrsAndSysts.cpp -o CorrsAndSysts.o

g++ -shared -Wl,-soname,CorrsAndSysts_ext.so -o CorrsAndSysts_ext.so CorrsAndSysts.o -lpython2.7 -lboost_python -lPyROOT -L/home/tim/root/lib -lCore -lRIO -lTree -lHist -lPhysics