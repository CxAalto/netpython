//#define NDEBUG
#include "../../lcelib/Nets.H"
#include "../../lcelib/Containers.H"
#include "../../lcelib/nets/NetExtras.H"



#include "../../lcelib/Randgens.H"
#include "../../lcelib/Nets.H"
#include "../../lcelib/nets/Randomizer.H"
#include "sn.h"

void shuffleEdges(Sn*, int,int,int);
int confModelSimple(Sn*, int rounds,int randseed);
