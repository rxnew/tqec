#pragma once

#include <iostream>

#include "point.hpp"
#include "size.hpp"
#include "rectangle.hpp"

namespace tqec {
namespace spp {
struct Rectangular : Point3D, Size3D {
  Rectangular() : Point3D(), Size3D() {}
  Rectangular(int x, int y, int z, int w, int h, int d)
    : Point3D(x, y, z), Size3D(w, h, d) {}
  Rectangular(Point3D const& point, int w, int h, int d)
    : Point3D(point), Size3D(w, h, d) {}
  Rectangular(int x, int y, int z, Size3D const& size)
    : Point3D(x, y, z), Size3D(size) {}
  Rectangular(Point3D const& point, Size3D const& size)
    : Point3D(point), Size3D(size) {}
  Rectangular(Size3D const& size) : Point3D(), Size3D(size) {}
  Rectangular(Rectangular const& other)
    : Point3D(other), Size3D(other) {}
  virtual ~Rectangular() = default;

  auto operator=(Rectangular const& other) -> Rectangular& {
    Point3D::operator=(other);
    Size3D::operator=(other);
    return *this;
  }
  auto operator==(Rectangular const& other) const -> bool {
    return Point3D::operator==(other) && Size3D::operator==(other);
  }
  auto operator!=(Rectangular const& other) const -> bool {
    return !(*this == other);
  }
  auto operator<(Rectangular const& other) const -> bool {
    return Point3D::operator<(other);
  }
  auto operator>(Rectangular const& other) const -> bool {
    return Point3D::operator>(other);
  }

  auto get_point() const -> Point3D {
    return Point3D(x, y, z);
  }
  auto get_antigoglin_point() const -> Point3D {
    return Point3D(x + w, y + h, z + d);
  }
  auto set_point(Point3D const& point) -> Rectangular {
    Point3D::operator=(point);
    return *this;
  }
  auto front_surface() const -> Rectangular {
    return Rectangular(x, y, z + d, w, h, 0);
  }
  auto back_surface() const -> Rectangular {
    return Rectangular(x, y, z, w, h, 0);
  }
  auto to_rectangle() const -> Rectangle {
    return Rectangle(x, y, w, h);
  }
  auto is_intersected(Point3D const& point) const -> bool {
    return is_intersected(Rectangular(point, 0, 0, 0));
  }
  auto is_intersected(Rectangular const& other) const -> bool {
    return
      x < other.x + other.w &&
      y < other.y + other.h &&
      z < other.z + other.d &&
      x + w > other.x &&
      y + h > other.y &&
      z + d > other.z;
  }
  auto print(std::ostream& os = std::cout) const -> void {
    os << "Point(" << x << ',' << y << ',' << z << "), "
       << "Size("  << w << ',' << h << ',' << d << ")" << std::endl;
  }
};
}
}

namespace std {
template <>
struct hash<tqec::spp::Rectangular> {
  auto operator()(tqec::spp::Rectangular const& obj) const noexcept -> size_t {
    return obj.x ^ obj.y ^ obj.z ^ obj.w ^ obj.h ^ obj.d;
  }
};
}
