#include "spp/spp3.hpp"
#include "spp/io.hpp"

#include <fstream>
#include <sstream>

using tqec::spp::Rectangular;
using RecPtr = std::shared_ptr<Rectangular>;
using Rectangulars = std::vector<RecPtr>;

auto create_rectangular(std::string const& str) -> RecPtr {
  auto token = std::string();
  auto stream = std::istringstream(str);

  auto params = std::vector<int>();

  while(getline(stream, token, ',')) {
    params.push_back(std::stoi(token));
  }

  assert(params.size() == 3);

  return std::make_shared<Rectangular>
    (tqec::spp::Point(), params[0], params[1], params[2]);
}

auto create_rectangulars(std::string const& filename) -> Rectangulars {
  auto ifs = std::ifstream(filename);
  auto rectangulars = Rectangulars();

  if(ifs.fail()) return rectangulars;

  auto str = std::string();
  while(getline(ifs, str)) {
    rectangulars.push_back(create_rectangular(str));
  }

  return rectangulars;
}

auto create_surface(std::string const& filename) ->  Rectangular {
  auto ifs = std::ifstream(filename);

  if(ifs.fail()) return Rectangular();

  auto str = std::string();
  getline(ifs, str);

  auto token = std::string();
  auto stream = std::istringstream(str);

  auto params = std::vector<int>();

  while(getline(stream, token, ',')) {
    params.push_back(std::stoi(token));
  }

  assert(params.size() == 3);

  return Rectangular(tqec::spp::Point(), params[0], params[1], params[2]);
}

auto main(int argc, char* argv[]) -> int {
  auto rectangulars_filename =
    argc >= 2 ? argv[1] : "test_data/example_rectangulars.csv";
  auto rectangulars = create_rectangulars(rectangulars_filename);

  auto surface_filename =
    argc >= 3 ? argv[2] : "test_data/example_surface.csv";
  auto surface = create_surface(surface_filename);

  tqec::spp::Spp3().solve(rectangulars, surface);

  tqec::spp::IO::output(rectangulars);

  return 0;
}
