
#include "../../lcelib/Nets.H"
#include "../../lcelib/Containers.H"
#include "../../lcelib/nets/NetExtras.H"

#include "../../lcelib/Randgens.H"
#include "../../lcelib/Nets.H"
#include "../../lcelib/nets/Randomizer.H"

#include "sn.h"
#include "netext.h"

float clusteringCoefficient(Sn *netContainer, int node){
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

int getNumberOfTriangles(Sn *netContainer){
  SymmNet<float> &net=*netContainer->net;

  int triangles=0;
  for (unsigned int i=0;i<net.size();++i)
    for (SymmNet<float>::const_edge_iterator j=net(i).begin();
	 !j.finished();
	 ++j) { 
      if (*j<i)
	for (SymmNet<float>::const_edge_iterator k=net(*j).begin();
	     !k.finished();
	     ++k) {
	  if (*k<*j)
	    if (net(*k)[i] != 0){ triangles++;}
    }
  }
  return triangles; 
 
}

float meanPathLength(Sn *netContainer, int maxSamples){
  SymmNet<float> &net=*netContainer->net;
  size_t randseed = time(0);
  RandNumGen<> generator(randseed);
    
  float maxlength=0; 
  double sumlengths=0; 
  long long Ndistances=0; 
  size_t NStartNodes=maxSamples;
  if (maxSamples>(int)net.size()){
    NStartNodes=net.size();
  }
  if (maxSamples<1){
    NStartNodes=net.size();
  }

    
  /* * * * shuffle node indices from 0 to N-1, then take NStartNodes
     indices from the beginning. This way, we are able to pick
     NStartNodes unique indices. The operation is O(N) (linear
     with N). */
  std::vector<size_t> order;  
  for (size_t i=0; i<net.size(); ++i) { order.push_back(i); };  
  shuffle(order,generator);   
    
  for (size_t m=0; m<NStartNodes; ++m) {
    size_t startingPoint=order[m]; 
    std::cerr << "\r\rStarting to find shortest paths from node id " << startingPoint << "...\n";
    Dijkstrator<SymmNet<float> > paths(net,startingPoint);
    for (; !paths.finished(); ++paths) {
      sumlengths += (*paths).getWeight();
      Ndistances++;
      if (maxlength <  (*paths).getWeight() ) 
	maxlength =  (*paths).getWeight();    
    } 
  } // end of loop for choosing Nstarts starting nodes
    // Calculate and output longest shortest path and average shortest path length for this run      
  //std::cerr << "Outputting: average path length \t maximum path length.\n";
  //std::cout <<  sumlengths/Ndistances << "\t" << maxlength << "\n";
  return sumlengths/Ndistances;
}
