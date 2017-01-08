#include "io.hpp"

#include "spp/rectangular.hpp"

namespace tqec {
namespace spp {
auto IO::output(Rectangular const& rectangular, int indent_count,
                std::ostream& os) -> void {
  auto indent1 = std::string(4 * indent_count, ' ');
  auto indent2 = std::string(4 * (indent_count + 1), ' ');

  os << indent1 << '{' << std::endl;

  os << indent2
     << "\"position\": ["
     << rectangular.x
     << ", "
     << rectangular.y
     << ", "
     << rectangular.z
     << "],"
     << std::endl;

  os << indent2
     << "\"size\": ["
     << rectangular.w
     << ", "
     << rectangular.h
     << ", "
     << rectangular.d
     << ']'
     << std::endl;

  os << indent1 << '}';
}

auto IO::output(Rectangulars const& rectangulars, std::ostream& os) -> void {
  auto indent = std::string(4, ' ');

  os << '{' << std::endl;

  os << indent
     << "\"modules\": ["
     << std::endl;

  {
    auto first = true;
    for(const auto& rectangular : rectangulars) {
      if(!first) os << ',' << std::endl;
      else       first = false;
      output(*rectangular, 2, os);
    }
  }

  os << std::endl;

  os << indent
     << ']'
     << std::endl;

  os << '}' << std::endl;
}
}
}
