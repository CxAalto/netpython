// sn.i - SWIG interface
 %module cnet
 %{
 #include "sn.h"
 #include "dn.h"
 #include "netext.h"
 #include "transforms.h"
 %}
 
 // Ignore the default constructor
 //%ignore std::pair::pair();      
 
 // Parse the original header file
 //%include "sn.h"

 // Instantiate some templates
 
// %template(symmnet_float) SymmNet<float>;
 //%template(pairdi) std::pair<double,int>;


class Sn{
 public:
  SymmNet<float> *net;
  Sn(int);
  int getSize();
  float getEdge(int,int);
  void setEdge(int,int,float);
 ~Sn();
  int* getNeighbors(int);
 NeighborIterator* getNeighborIterator(int node);
 int getDegree(int);
};


class NeighborIterator{
 public:
  int *neighbors;
  int size;
  int current;
  //SymmNet<float>::edge_iterator theIterator;
  NeighborIterator(int,SymmNet<float>*);
  int getNext();
  ~NeighborIterator();
};

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

//%include "netext.h"
float clusteringCoefficient(Sn*, int);
int getNumberOfTriangles(Sn*);
float meanPathLength(Sn*, int);

//%include "transforms.h"
void shuffleEdges(Sn*, int,int,int);
//int confModelSimple(Sn*, int,int);
