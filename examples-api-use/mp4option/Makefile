CXX=g++
CXXFLAGS=-O3 -Wall -I../../include
LDFLAGS=-L../../lib -lrgbmatrix -lrt -lm -lpthread -lGraphicsMagick++ 

all: mp4-player

mp4-player: mp4-player.cc
    $(CXX) $(CXXFLAGS) mp4-player.cc -o mp4-player $(LDFLAGS)

clean:
    rm -f mp4-player