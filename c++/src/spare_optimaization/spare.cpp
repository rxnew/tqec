#include "sa_non_shared.hpp"
#include "sa_shared.hpp"

#include <iostream>

auto main(int argc, char* argv[]) -> int {
  std::vector<int> c = {4, 3, 6, 7, 3, 7};
  std::vector<float> e = {0.03, 0.03, 0.01, 0.01, 0.005, 0.3};
  float et = 0.03;

  auto x = optimization::SANonShared().optimize(c, e, et);

  for(const auto& xi : x) {
    std::cout << xi << std::endl;
  }

  std::vector<std::vector<int>> cs = {{4, 3}, {6}, {7}, {3}, {7}};
  std::vector<float> es = {0.03, 0.01, 0.01, 0.005, 0.3};
  float est = 0.03;

  auto xs = optimization::SAShared().optimize(cs, es, est);

  for(const auto& xsi : xs) {
    std::cout << "{";
    for(const auto& xsj : xsi) {
      std::cout << xsj << ",";
    }
    std::cout << "}" << std::endl;
  }

  return 0;
}
