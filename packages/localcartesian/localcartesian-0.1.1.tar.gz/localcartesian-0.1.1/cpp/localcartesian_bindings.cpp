/*
    Converts lat, lon coordinates to local x, y coordinates using
    the geographiclib library:
        https://geographiclib.sourceforge.io/index.html

    This C++ module exists because the library's Python bindings
        https://geographiclib.sourceforge.io/Python/doc/index.html
    does not list the equivalent of the C++ class LocalCartesian:
        https://geographiclib.sourceforge.io/C++/doc/classGeographicLib_1_1LocalCartesian.html
*/

// geographiclib
#include <GeographicLib/LocalCartesian.hpp>

// for interfacing with python
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

// vectors/arrays
#include <vector>

using namespace std;
using namespace GeographicLib;


vector<vector<double>> gps2xy(vector<vector<double>> & latlon, vector<double> & origin_latlonalt){

    // create an instance of LocalCartesian with the reference point
    LocalCartesian local(origin_latlonalt[0], origin_latlonalt[1], origin_latlonalt[2]);

    vector<vector<double>> localxy;

    for (size_t i = 0; i < latlon.size(); i++){
        
        double lat = latlon[i][0];
        double lon = latlon[i][1];
        double alt = origin_latlonalt[2]; // no alt info given, assume same as origin

        double x, y, z;
        local.Forward(lat, lon, alt, x, y, z);

        vector<double> row = {x, y};
        localxy.push_back(row);
    }
    return localxy;
}


vector<vector<double>> xy2gps(vector<vector<double>> & xy, vector<double> & origin_latlonalt){

    // create an instance of LocalCartesian with the reference point
    LocalCartesian local(origin_latlonalt[0], origin_latlonalt[1], origin_latlonalt[2]);

    vector<vector<double>> latlon;

    for (size_t i = 0; i < xy.size(); i++){
        
        double x = xy[i][0];
        double y = xy[i][1];
        double z = 0.; // no alt info given, assume same as origin

        double lat, lon, alt;
        local.Reverse(x, y, z, lat, lon, alt);

        vector<double> row = {lat, lon};
        latlon.push_back(row);
    }
    return latlon;
}


PYBIND11_MODULE(_core, m) {
    m.doc() = "Fast GPS to local Cartesian coordinate conversion using GeographicLib";
    m.def("gps2xy", &gps2xy, "Convert GPS coordinates to local Cartesian coordinates");
    m.def("xy2gps", &xy2gps, "Convert local Cartesian coordinates to GPS coordinates");
}