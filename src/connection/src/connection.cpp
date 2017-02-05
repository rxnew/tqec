#include "connection.hpp"
#include "io.hpp"

#include <cassert>
#include <fstream>
#include <sstream>
#include <vector>

auto createEndpoint(const std::string& str)
  -> tqec::conn::Connection::Endpoint {
  std::string token;
  std::istringstream stream(str);

  std::vector<int> params;

  while(getline(stream, token, ',')) {
    params.push_back(std::stoi(token));
  }

  assert(params.size() == 6);

  tqec::conn::Node src_node(params[0], params[1], params[2]);
  tqec::conn::Node dst_node(params[3], params[4], params[5]);

  return tqec::conn::Connection::Endpoint(src_node, dst_node);
}

auto createEndpoints(const std::string& filename)
  -> tqec::conn::Connection::Endpoints {
  std::ifstream ifs(filename);
  tqec::conn::Connection::Endpoints endpoints;

  if(ifs.fail()) return endpoints;

  std::string str;
  while(getline(ifs, str)) {
    auto endpoint = createEndpoint(str);
    endpoints.push_back(endpoint);
  }

  return std::move(endpoints);
}

auto setObstacles(tqec::conn::Obstacles& obstacles,
                  const std::string& str) -> void {
  std::string token;
  std::istringstream stream(str);

  std::vector<int> params;

  while(getline(stream, token, ',')) {
    params.push_back(std::stoi(token));
  }

  assert(params.size() == 3 || params.size() == 6);

  tqec::conn::Node node(params[0], params[1], params[2]);
  if(params.size() == 3) {
    obstacles.add(node);
  }
  else {
    tqec::conn::Size size(params[3], params[4], params[5]);
    obstacles.addRectangular(node, size);
  }
}

auto createObstacles(const std::string& filename) -> tqec::conn::Obstacles {
  std::ifstream ifs(filename);
  tqec::conn::Obstacles obstacles;

  if(ifs.fail()) return std::move(obstacles);

  std::string str;
  while(getline(ifs, str)) {
    if(str.front() != '!') setObstacles(obstacles, str);
  }

  return std::move(obstacles);
}

auto createArea(const std::string& filename) -> tqec::conn::Area {
  std::ifstream ifs(filename);

  if(ifs.fail()) return tqec::conn::Area();

  std::string str;
  while(getline(ifs, str)) {
    if(str.front() == '!') {
      std::string token;
      std::istringstream stream(str.substr(1));

      std::vector<int> params;

      while(getline(stream, token, ',')) {
        params.push_back(std::stoi(token));
      }

      assert(params.size() == 6);

      tqec::conn::Node pos(params[0], params[1], params[2]);
      tqec::conn::Size size(params[3], params[4], params[5]);

      return tqec::conn::Area(pos, size);
    }
  }

  return tqec::conn::Area();
}

auto main(int argc, char* argv[]) -> int {
  auto filename = argc >= 2 ? argv[1] : "test_data/example_connection.json";
  auto data = tqec::conn::io::open(filename);
  auto endpoints = std::get<0>(data);
  auto obstacles = std::get<1>(data);
  auto region    = std::get<2>(data);
  auto routes = tqec::conn::Connection(endpoints, obstacles, region).search();
  tqec::conn::io::print(routes);
  return 0;
}
