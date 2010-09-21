#include "dn.h"
#include "../../lcelib/Nets.H"

Dn::Dn(int size){
  this->net=new DirNet<float>(size);
}

Dn::~Dn(){
  delete this->net;
}

int Dn::getSize(){
  return this->net->size();
}

float Dn::getEdge(int node1,int node2){
  if (node1!=node2){
    return (*(this->net))[node1][node2];
  }else{
    return 0.0;
  }
}

void Dn::setEdge(int node1,int node2,float value){
  if (node1!=node2){
    (*(this->net))[node1][node2]=value;
  }
}

int Dn::getDegree(int node){
  return (*(this->net))(node).size();
}

int Dn::getInDegree(int node){
  int inSize=0;
  for (DirNet<float>::edge_iterator j=(*net)[node].begin(); !j.finished(); ++j) {
    if (j.value().in()>0){
      inSize++;
    }
  }
  return inSize;
}
int Dn::getOutDegree(int node){
  int outSize=0;
  for (DirNet<float>::edge_iterator j=(*net)[node].begin(); !j.finished(); ++j) {
    if (j.value().out()>0){
      outSize++;
    }
  }
  return outSize;
}

NeighborIteratorAll* Dn::getNeighborIteratorAll(int node){
  return new NeighborIteratorAll(node,this->net);
}

NeighborIteratorIn* Dn::getNeighborIteratorIn(int node){
  return new NeighborIteratorIn(node,this->net);
}

NeighborIteratorOut* Dn::getNeighborIteratorOut(int node){
  return new NeighborIteratorOut(node,this->net);
}


NeighborIteratorAll::NeighborIteratorAll(int node ,DirNet<float> *net){
  this->current=0;
  this->size=((*net)(node)).size();
  int size=this->size;
  this->neighbors= new int[size];
  int i=0;
  for (DirNet<float>::edge_iterator j=(*net)[node].begin(); !j.finished(); ++j) {
    neighbors[i]=*j;
    i++;
  }
}

int NeighborIteratorAll::getNext(){
  if (this->current<this->size){
      this->current=this->current+1;
      return this->neighbors[this->current-1];
    } else {
    return -1;
  }
}

NeighborIteratorAll::~NeighborIteratorAll(){
  delete this->neighbors;
}


NeighborIteratorIn::NeighborIteratorIn(int node ,DirNet<float> *net){
  this->current=0;
  int allSize=((*net)(node)).size();
  this->neighbors= new int[allSize];
  int inSize=0;
  for (DirNet<float>::edge_iterator j=(*net)[node].begin(); !j.finished(); ++j) {
    if (j.value().in()>0){
      neighbors[inSize]=*j;
      inSize++;
    }
  }
  this->size=inSize;
}

int NeighborIteratorIn::getNext(){
  if (this->current<this->size){
      this->current=this->current+1;
      return this->neighbors[this->current-1];
    } else {
    return -1;
  }
}
NeighborIteratorIn::~NeighborIteratorIn(){
  delete this->neighbors;
}

NeighborIteratorOut::NeighborIteratorOut(int node ,DirNet<float> *net){
  this->current=0;
  int allSize=((*net)(node)).size();
  this->neighbors= new int[allSize];
  int outSize=0;
  for (DirNet<float>::edge_iterator j=(*net)[node].begin(); !j.finished(); ++j) {
    if (j.value().out()>0){
      neighbors[outSize]=*j;
      outSize++;
    }
  }
  this->size=outSize;
}

int NeighborIteratorOut::getNext(){
  if (this->current<this->size){
      this->current=this->current+1;
      return this->neighbors[this->current-1];
    } else {
    return -1;
  }
}
NeighborIteratorOut::~NeighborIteratorOut(){
  delete this->neighbors;
}
