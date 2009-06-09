#include "sn.h"
#include "../../lcelib/Nets.H"

Sn::Sn(int size){
  this->net=new SymmNet<float>(size);
}

Sn::~Sn(){
  delete this->net;
}

int Sn::getSize(){
  return this->net->size();
}

float Sn::getEdge(int node1,int node2){
  if (node1!=node2){
    return (*(this->net))[node1][node2];
  }else{
    return 0.0;
  }
}

void Sn::setEdge(int node1,int node2,float value){
  if (node1!=node2){
    (*(this->net))[node1][node2]=value;
  }
}

int* Sn::getNeighbors(int node){
  int size=(*(this->net))(node).size();
  int *a= new int[size];
  int i=0;
  for (SymmNet<float>::edge_iterator j=(*net)[node].begin(); !j.finished(); ++j) {
    a[i]=*j;
    i++;
  }
  return a;
}

int Sn::getDegree(int node){
  return (*(this->net))(node).size();
}

NeighborIterator* Sn::getNeighborIterator(int node){
  return new NeighborIterator(node,this->net);
  //SymmNet<float>::edge_iterator j=((*this->net))[node].begin();
  //return j;
}


NeighborIterator::NeighborIterator(int node ,SymmNet<float> *net){
  //this->theIterator=(*net)[node].begin();
  this->current=0;
  this->size=((*net)(node)).size();
  int size=this->size;
  this->neighbors= new int[size];
  int i=0;
  for (SymmNet<float>::edge_iterator j=(*net)[node].begin(); !j.finished(); ++j) {
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
//  Sn testi=Sn::Sn(10);
  //SymmNet<float> net=SymmNet<float>(10);
//  testi.setEdge(0,1,1.0);
  //float t=net(0,1);
//}
