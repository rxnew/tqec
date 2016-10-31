#include "spare/sa.hpp"

#include <cassert>
#include <fstream>
#include <sstream>
#include <iostream>

auto createModule(const std::string& str) -> tqec::spare::Module {
  std::string token;
  std::istringstream stream(str);

  std::vector<float> params;

  while(getline(stream, token, ',')) {
    params.push_back(std::stof(token));
  }

  assert(params.size() == 3);

  const auto cost = static_cast<int>(params[0]);
  const auto error_rate = params[1];
  const auto count = static_cast<int>(params[2]);

  return tqec::spare::Module(cost, error_rate, count);
}

auto createModules(const std::string& filename) -> tqec::spare::Modules {
  std::ifstream ifs(filename);
  tqec::spare::Modules modules;

  assert(!ifs.fail());

  std::string str;
  while(getline(ifs, str)) {
    const auto module = createModule(str);
    modules.push_back(module);
  }

  return std::move(modules);
}

auto main(int argc, char* argv[]) -> int {
  assert(argc >= 3);

  const auto modules_filename = argv[1];
  const auto modules = createModules(modules_filename);
  const auto error_rate_threshold = std::stof(argv[2]);

  auto spare_counts = tqec::spare::SA().optimize(modules, error_rate_threshold);

  {
    auto first = true;
    for(const auto& spare_count : spare_counts) {
      if(first) first = false;
      else      std::cout << ',';
      std::cout << spare_count;
    }
    std::cout << std::endl;
  }

  return 0;
}
