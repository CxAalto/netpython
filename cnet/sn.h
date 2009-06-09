#ifndef SN_HH
#define SN_HH

//#define NDEBUG
//#include <stddef.h>
#include "../../lcelib/Nets.H"




class NeighborIterator{

 public:
  //SymmNet<float>::const_edge_iterator theIterator;
  int *neighbors;
  int size;
  int current;
  NeighborIterator(int,SymmNet<float>*);
  int getNext();
  ~NeighborIterator();

};


class Sn{

 public:
  SymmNet<float> *net;
  Sn(int);
  int getSize();
  float getEdge(int,int);
  void setEdge(int,int,float);
  ~Sn();
  NeighborIterator* getNeighborIterator(int node);
  int* getNeighbors(int);
  int getDegree(int);


};



#endif //SN_HH
