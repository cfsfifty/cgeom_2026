#include <cmath>
#include <ctime>
#include <cassert>
#include <vector>
#include <fstream>
#include <iostream>
#include <limits>
#include <algorithm>
#include <string>
#include <sstream> 

struct Point2f {
public:
    Point2f() 
    : x(0.0f), y(0.0f) {
    }
    Point2f(float x, float y) {
        set(x, y);
    }

    void set(float x, float y) {
        this->x = x;
        this->y = y;
    }
    void min(Point2f const& p) {
        this->x = std::min(this->x, p.x);
        this->y = std::min(this->y, p.y);
    }
    void max(Point2f const& p) {
        this->x = std::max(this->x, p.x);
        this->y = std::max(this->y, p.y);
    }
    operator const float* () const {
        return &x;
    }
    operator float* () {
        return &x;
    }

    friend std::ostream& operator<< (std::ostream& os, const Point2f& value) {
        os << "(" << value.x << "," << value.y << ")" << std::flush;
        return os;
    }

    float x;
    float y;
};

///
class FileObj
{
public:
    // 
    FileObj() {
        this->filename = NULL;
    }

    //
    void read(const char* filename) {
        this->filename = filename;
        this->indices.clear();
        this->points.clear();

        constexpr float inf = std::numeric_limits<float>::infinity();
        this->bbox_min.set( inf,  inf);
        this->bbox_max.set(-inf, -inf);

        std::string line;
        std::ifstream file;
        file.open(this->filename);
        while (std::getline(file, line)) {
            //print(line)
            if (line.empty()) { 
                continue;
            }
            std::string::size_type prev_pos = 0, pos = 0;
            std::string element, element2;

            pos     = line.find(" ", pos);
            element = line.substr(prev_pos, pos - prev_pos), prev_pos = ++pos;
            std::istringstream str(line.substr(prev_pos, line.size()-prev_pos));

            if (element == "#") { // skip comment line
                continue;
            }
            if (element == "v") {
                Point2f point;
                str >> point.x >> point.y;
                // only 2d
                this->bbox_min.min(point);
                this->bbox_max.max(point);
                this->points.push_back(point);
                continue;
            }
            if (element == "f") {
                while (true) {
                    unsigned index;
                    str >> index;
                    if (!str)
                        break;
                    // indices in OBJ are 1 based
                    this->indices.push_back(index - 1);
                }
                continue;
            }
        }
        std::cout << this->bbox_min << " " << this->bbox_max << std::endl;
        std::cout << "read " << this->points.size() << " points, " << this->indices.size() << " deg-polygon" << std::endl;
        if (this->indices.size() == 0) {
            for (unsigned i = 0; i < this->points.size(); ++i) {
                this->indices.push_back(i);
            }
        }
        std::cout << "read " << this->points.size() << " points, " << this->indices.size() << " deg-polygon" << std::endl;
    }

    // List of coords tuples of all points read 
    std::vector<Point2f> getPointCoords() const {
        return this->points;
    }
    // List of indices into PointCoords list
    std::vector<unsigned> getPolygonIndices() const {
        return this->indices;
    }
    // List of polygon coords tuples
    std::vector<Point2f> getPolygon() const {
        std::vector<Point2f> polygon;
        if (this->indices.size() == 0) {
            return polygon;
        }
        assert(0 <= *std::min_element(this->indices.begin(), this->indices.end()) 
        && *std::max_element(this->indices.begin(), this->indices.end()) < this->points.size());
        for (auto iter = this->indices.begin(); iter!=this->indices.end(); ++iter) {
            polygon.push_back(this->points[*iter]);
        }
        return polygon;
  }

  Point2f bbox_min; 
  Point2f bbox_max;

private:
  std::vector<Point2f>  points;
  std::vector<unsigned> indices;
  const char* filename;
};
