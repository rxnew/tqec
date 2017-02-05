#include "size.hpp"

#include <limits>

namespace tqec {
namespace conn {
Size::Size() : w(std::numeric_limits<int>::max()),
               h(std::numeric_limits<int>::max()),
               d(std::numeric_limits<int>::max()) {}

Size::Size(int w, int h, int d) : w(w), h(h), d(d) {}
}
}
