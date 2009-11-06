// sn.i - SWIG interface
 %module cnet
 %{
 #include "sn.h"
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



//%include "netext.h"
float clusteringCoefficient(Sn*, int);

//%include "transforms.h"
void shuffleEdges(Sn*, int,int,int);
