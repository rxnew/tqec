#include "module.hpp"

namespace tqec {
namespace spare {
Module::Module(int cost, float error_rate, int count)
  : cost(cost), error_rate(error_rate), count(count) {}
}
}
