	
#include <iostream>

#define FACTOR	0.79719390

int main(int argc, char* argv[])
{
	double dollar = atof(argv[1]); 
	std::cout<<dollar<<" Dolares son "<<(dollar*FACTOR)<< " Euros"<<std::endl;
	return 0;
} 
