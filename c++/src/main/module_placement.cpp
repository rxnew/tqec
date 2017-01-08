#include "spp/spp3.hpp"
#include "spp/io.hpp"

#include <fstream>
#include <sstream>

using tqec::spp::Rectangular;
using RecPtr = std::shared_ptr<Rectangular>;
using Rectangulars = std::vector<RecPtr>;

auto create_surface(std::string const& str) ->  Rectangular {
  auto token = std::string();
  auto stream = std::istringstream(str);

  auto params = std::vector<int>();

  while(getline(stream, token, ',')) {
    params.push_back(std::stoi(token));
  }

  assert(params.size() == 6);
  assert(params[2] == 0);

  return Rectangular(params[3], params[4], params[5], params[0], params[1], params[2]);
}

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

auto create_input_data(std::string const& filename)
  -> std::tuple<Rectangular, Rectangulars> {
  auto ifs = std::ifstream(filename);

  assert(!ifs.fail());

  auto str = std::string();
  getline(ifs, str);
  auto surface = create_surface(str);
  auto rectangulars = Rectangulars();
  while(getline(ifs, str)) {
    rectangulars.push_back(create_rectangular(str));
  }

  return std::make_tuple(surface, rectangulars);
}

auto main(int argc, char* argv[]) -> int {
  auto rectangulars_filename =
    argc >= 2 ? argv[1] : "test_data/example_spp3.csv";

  auto input_data = create_input_data(rectangulars_filename);
  auto& surface = std::get<0>(input_data);
  auto& rectangulars = std::get<1>(input_data);

  tqec::spp::Spp3().solve(rectangulars, surface);

  tqec::spp::IO::output(rectangulars);

  return 0;
}
