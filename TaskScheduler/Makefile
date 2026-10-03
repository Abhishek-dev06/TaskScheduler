CXX = g++
CXXFLAGS = -std=c++17 -O2 -Wall

ts: src/main.cpp
	$(CXX) $(CXXFLAGS) src/main.cpp -o ts

run: ts
	./ts

clean:
	rm -f ts ts.exe
