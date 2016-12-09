#pragma once

#include <iostream>
#include <memory>
#include <vector>

#include "rectangular.hpp"

namespace tqec {
namespace spp {
class IO {
 private:
  using Rectangular = tqec::spp::Rectangular;
  using RecPtr = std::shared_ptr<Rectangular>;
  using Rectangulars = std::vector<RecPtr>;

 public:
  static auto output(Rectangular const& rectangular, int indent_count = 0,
                     std::ostream& os = std::cout) -> void;
  static auto output(Rectangulars const& rectangulars,
                     std::ostream& os = std::cout) -> void;
};
}
}
