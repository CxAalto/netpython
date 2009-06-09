
#include "../../lcelib/Nets.H"
#include "sn.h"
#include "netext.h"

float clusteringCoefficient(Sn::Sn *netContainer, int node){
  int i=node;
  SymmNet<float> &net=*netContainer->net;

  float size=(float) net(i).size();
  if (size==0.0) return 0.0;

  size_t sum=0;
  // naapurit:
  for (SymmNet<float>::const_edge_iterator j=net(i).begin();
       !j.finished();
       ++j) {
    // niiden naapurit. Huomaa, ettei särmää *j->i tarvitse suodattaa pois. 
    for (SymmNet<float>::const_edge_iterator k=net(*j).begin();
	 !k.finished();
	 ++k) {
      if (net(*k)[i] != 0) sum++;    
    }
  }
  return ((float) sum)/net(i).size() / ( net(i).size()-1 ); 
  //return (float)sum;
}
