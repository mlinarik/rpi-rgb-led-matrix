#include "led-matrix.h"
#include "graphics.h"
#include <Magick++.h>
#include <vector>
#include <string>
#include <iostream>
#include <dirent.h>
#include <algorithm>
#include <unistd.h>

using namespace rgb_matrix;
using namespace std;

// Helper: Get sorted list of PNG files in frames/
vector<string> GetFrameFiles(const string& dir) {
    vector<string> files;
    DIR* dp = opendir(dir.c_str());
    if (!dp) return files;
    struct dirent* ep;
    while ((ep = readdir(dp))) {
        string fname = ep->d_name;
        if (fname.size() > 4 && fname.substr(fname.size()-4) == ".png")
            files.push_back(dir + "/" + fname);
    }
    closedir(dp);
    sort(files.begin(), files.end());
    return files;
}

int main(int argc, char **argv) {
    RGBMatrix::Options options;
    RuntimeOptions runtime;
    options.hardware_mapping = "regular";
    options.rows = 32;      // Change to your panel size
    options.cols = 32;
    options.chain_length = 1;
    options.parallel = 1;
    options.brightness = 80;
    runtime.drop_privileges = 1;

    RGBMatrix *matrix = RGBMatrix::CreateFromFlags(&argc, &argv, &options, &runtime);
    if (!matrix) {
        cerr << "Could not create matrix." << endl;
        return 1;
    }
    FrameCanvas *canvas = matrix->CreateFrameCanvas();

    Magick::InitializeMagick(*argv);

    // Get frames from ./frames/
    vector<string> frames = GetFrameFiles("frames");
    if (frames.empty()) {
        cerr << "No PNG frames found in ./frames/" << endl;
        return 1;
    }

    // Play frames in a loop
    while (true) {
        for (const auto& fname : frames) {
            Magick::Image img;
            try {
                img.read(fname);
                img.scale(Magick::Geometry(options.cols, options.rows));
            } catch (...) {
                cerr << "Error loading " << fname << endl;
                continue;
            }
            for (int y = 0; y < options.rows; ++y) {
                for (int x = 0; x < options.cols; ++x) {
                    Magick::Color c = img.pixelColor(x, y);
                    canvas->SetPixel(x, y, c.redQuantum()/257, c.greenQuantum()/257, c.blueQuantum()/257);
                }
            }
            canvas = matrix->SwapOnVSync(canvas);
            usleep(33000); // ~30 FPS
        }
    }

    delete canvas;
    delete matrix;
    return 0;
}