#include "../io.hpp"
#include "io_private.hpp"

#include <cassert>
#include <fstream>

namespace tqec {
auto input(std::string const& filename) -> std::tuple<SA::Modules, float> {
  auto const json_object = _input(filename);
  auto modules = _make_modules(json_object);
  auto const error_rate_threshold = _get_error_rate_threshold(json_object);
  return std::make_tuple(std::move(modules), error_rate_threshold);
}

auto output(SA::Counts const& counts, std::ostream& os) -> void {
  auto first = true;
  for(auto const& count : counts) {
    if(first) first = false;
    else      os << ',';
    os << count;
  }
  os << std::endl;
}

auto _input(std::string const& filename) -> json11::Json {
  auto ifs = std::ifstream(filename);

  assert(!ifs.fail());

  auto buf = std::string();
  auto tmp = std::string();
  auto err = std::string();

  while(std::getline(ifs, tmp)) buf += tmp;

  ifs.close();

  return json11::Json::parse(buf, err);
}

auto _make_module(json11::Json const& json_object) -> Module {
  assert(json_object.is_object());

  auto const& cost_json_number = json_object["cost"];
  auto const& error_json_number = json_object["error"];
  auto const& number_json_number = json_object["number"];

  assert(cost_json_number.is_number());
  assert(error_json_number.is_number());
  assert(number_json_number.is_number());

  auto cost = cost_json_number.int_value();
  auto error_rate = error_json_number.number_value();
  auto count = number_json_number.int_value();

  return Module(cost, error_rate, count);
}

auto _make_modules(json11::Json const& json_object) -> SA::Modules {
  assert(json_object.is_object());

  auto const& json_array = json_object["modules"];

  assert(json_array.is_array());

  auto modules = SA::Modules();

  for(auto const& module_json_object : json_array.array_items()) {
    modules.push_back(_make_module(module_json_object));
  }

  return modules;
}

auto _get_error_rate_threshold(json11::Json const& json_object) -> float {
  assert(json_object.is_object());

  auto const& error_threshold_json_number = json_object["error_threshold"];

  assert(error_threshold_json_number.is_number());

  return error_threshold_json_number.number_value();
}
}
