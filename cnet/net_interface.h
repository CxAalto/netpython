#include "../../lcelib/Nets.H"

template<class NetType> class NeighborIterator{

 public:
  int *neighbors;
  int size;
  int current;
  NeighborIterator(int,NetType*);
  int getNext();
  ~NeighborIterator();

};


template<class NetType> class NetInterface{

 public:
  NetType *net;
  NetInterface(int);
  int getSize();
  float getEdge(int,int);
  void setEdge(int,int,float);
  ~NetInterface();
  NeighborIterator<NetType>* getNeighborIterator(int node);
  int* getNeighbors(int);
  int getDegree(int);


};



NetInterface::NetInterface(int size){
  this->net=new NetType(size);
}

NetInterface::~NetInterface(){
  delete this->net;
}

int NetInterface::getSize(){
  return this->net->size();
}

float NetInterface::getEdge(int node1,int node2){
  if (node1!=node2){
    return (*(this->net))[node1][node2];
  }else{
    return 0.0;
  }
}

void NetInterface::setEdge(int node1,int node2,float value){
  if (node1!=node2){
    (*(this->net))[node1][node2]=value;
  }
}

int* NetInterface::getNeighbors(int node){
  int size=(*(this->net))(node).size();
  int *a= new int[size];
  int i=0;
  for (NetType::edge_iterator j=(*net)[node].begin(); !j.finished(); ++j) {
    a[i]=*j;
    i++;
  }
  return a;
}

int NetInterface::getDegree(int node){
  return (*(this->net))(node).size();
}

NeighborIterator<NetType>* NetInterface::getNeighborIterator(int node){
  return new NeighborIterator<NetType>(node,this->net);
}


NeighborIterator::NeighborIterator(int node ,NetType *net){
  this->current=0;
  this->size=((*net)(node)).size();
  int size=this->size;
  this->neighbors= new int[size];
  int i=0;
  for (NetType::edge_iterator j=(*net)[node].begin(); !j.finished(); ++j) {
    neighbors[i]=*j;
    i++;
  }
}

int NeighborIterator::getNext(){
  if (this->current<this->size){
      this->current=this->current+1;
      return this->neighbors[this->current-1];
    } else {
    return -1;
  }
}

NeighborIterator::~NeighborIterator(){
  delete this->neighbors;
}


//int main(void){
//  NetInterface testi=NetInterface::NetInterface(10);
  //NetType net=NetType(10);
//  testi.setEdge(0,1,1.0);
  //float t=net(0,1);
//}
