#ifndef DN_HH
#define DN_HH

//#define NDEBUG
//#include <stddef.h>
#include "../../lcelib/Nets.H"




class NeighborIteratorAll{
 public:
  int *neighbors;
  int size;
  int current;
  NeighborIteratorAll(int,DirNet<float>*);
  int getNext();
  ~NeighborIteratorAll();
};

class NeighborIteratorIn{
 public:
  int *neighbors;
  int size;
  int current;
  NeighborIteratorIn(int,DirNet<float>*);
  int getNext();
  ~NeighborIteratorIn();
};

class NeighborIteratorOut{
 public:
  int *neighbors;
  int size;
  int current;
  NeighborIteratorOut(int,DirNet<float>*);
  int getNext();
  ~NeighborIteratorOut();
};

class Dn{
 public:
  DirNet<float> *net;
  Dn(int);
  int getSize();
  float getEdge(int,int);
  void setEdge(int,int,float);
  ~Dn();
  NeighborIteratorAll* getNeighborIteratorAll(int node);
  NeighborIteratorIn* getNeighborIteratorIn(int node);
  NeighborIteratorOut* getNeighborIteratorOut(int node);
  int getDegree(int);
  int getInDegree(int);
  int getOutDegree(int);


};



#endif //DN_HH
