#include "io.hpp"

auto main(int argc, char* argv[]) -> int {
  auto const filename = argv[1];
  auto const data = tqec::input(filename);
  auto const& modules = std::get<0>(data);
  auto const& error_rate_threshold = std::get<1>(data);
  auto const counts = tqec::SA().optimize(modules, error_rate_threshold);
  tqec::output(counts);
  return 0;
}
