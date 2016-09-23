all: alloclots burncycles spawnthreads

alloclots: alloclots.cc
	g++ -Wall -Wextra -pedantic -std=c++11 -O3 -g -o alloclots alloclots.cc

burncycles: burncycles.cc
	g++ -Wall -Wextra -pedantic -std=c++11 -O3 -g -o burncycles burncycles.cc

spawnthreads: spawnthreads.cc
	g++ -Wall -Wextra -pedantic -std=c++11 -O3 -g -o spawnthreads spawnthreads.cc -lpthread

clean:
	rm -f alloclots burncycles spawnthreads
