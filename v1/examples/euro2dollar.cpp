
#include <iostream>

#define FACTOR	0.797193878

int main(int argc, char* argv[])
{
	double euro = atod(argv[1]); 
	std::cout<<euro<<" Euros son "<<(euro/FACTOR)<< " Dolares"<<std::endl;
	return 0;
}  


