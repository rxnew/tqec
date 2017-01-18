#pragma once

#include "json11.hpp"

#include "../sa.hpp"

namespace tqec {
auto _input(std::string const& filename) -> json11::Json;
auto _make_module(json11::Json const& json_object) -> Module;
auto _make_modules(json11::Json const& json_object) -> SA::Modules;
auto _get_error_rate_threshold(json11::Json const& json_object) -> float;
}
