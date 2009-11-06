
#include "../../lcelib/Nets.H"
#include "../../lcelib/Containers.H"
#include "../../lcelib/nets/NetExtras.H"

#include "../../lcelib/Randgens.H"
#include "../../lcelib/Nets.H"
#include "../../lcelib/nets/Randomizer.H"
#include "sn.h"
#include "transforms.h"

void shuffleEdges(Sn::Sn *netContainer, int rounds,int limit,int randseed){
  SymmNet<float> &net=*netContainer->net;

  RandNumGen<> generator(randseed);

  randomize(net,generator,rounds,limit);

}
