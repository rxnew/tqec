#pragma once

#include <iostream>

#include "json11.hpp"

#include "sa.hpp"

namespace tqec {
auto input(std::string const& filename) -> std::tuple<SA::Modules, float>;
auto output(SA::Counts const& counts, std::ostream& os = std::cout) -> void;
}
