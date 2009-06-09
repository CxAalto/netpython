// cnet.i - SWIG interface
 %module cnet
 %{
 #include "../../../lcelib/Nets.H"
 %}
 
 // Ignore the default constructor
 //%ignore std::pair::pair();      
 
 // Parse the original header file
 %include "../../../lcelib/Nets.H"
 
 // Instantiate some templates
 
 %template(symmnet_float) SymmNet<float>;
 //%template(pairdi) std::pair<double,int>;