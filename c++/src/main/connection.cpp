#include "conn/connection.hpp"
#include "conn/io.hpp"

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
    setObstacles(obstacles, str);
  }

  return std::move(obstacles);
}

auto main(int argc, char* argv[]) -> int {
  auto obstacles_filename =
    argc >= 2 ? argv[1] : "test_data/example_obstacles.csv";
  auto obstacles = createObstacles(obstacles_filename);

  auto endpoints_filename =
    argc >= 3 ? argv[2] : "test_data/example_endpoints.csv";
  auto endpoints = createEndpoints(endpoints_filename);

  auto routes = tqec::conn::Connection(endpoints, obstacles).search();

  tqec::conn::IO::output(routes);

  return 0;
}
