#pragma once

#include <algorithm>

namespace util {
template <class T>
auto combination(T n, T k) -> T {
  k = std::min(k, n - k);
  T res(1);
  for(auto i = 1; i <= k; i++) {
    res *= n--;
    res /= i;
  }
  return res;
}
}
