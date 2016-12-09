#pragma once

#include "point.hpp"
#include "size.hpp"

namespace tqec {
namespace spp {
struct Rectangle : Point2D, Size2D {
  Rectangle() : Point2D(), Size2D() {}
  Rectangle(int x, int y, int w, int h)
    : Point2D(x, y), Size2D(w, h) {}
  Rectangle(Point2D const& point, int w, int h)
    : Point2D(point), Size2D(w, h) {}
  Rectangle(int x, int y, Size2D const& size)
    : Point2D(x, y), Size2D(size) {}
  Rectangle(Point2D const& point, Size2D const& size)
    : Point2D(point), Size2D(size) {}
  Rectangle(Rectangle const& other)
    : Point2D(other), Size2D(other) {}
  virtual ~Rectangle() = default;

  auto operator=(Rectangle const& other) -> Rectangle& {
    Point2D::operator=(other);
    Size2D::operator=(other);
    return *this;
  }
  auto operator==(Rectangle const& other) const -> bool {
    return Point2D::operator==(other) && Size2D::operator==(other);
  }
  auto operator!=(Rectangle const& other) const -> bool {
    return !(*this == other);
  }

  auto get_point() const -> Point2D {
    return Point2D(x, y);
  }
  auto get_antigoglin_point() const -> Point2D {
    return Point2D(x + w, y + h);
  }
  auto set_point(Point2D const& point) -> Rectangle {
    Point2D::operator=(point);
    return *this;
  }
  auto is_intersected(Point2D const& point) const -> bool {
    return is_intersected(Rectangle(point, 0, 0));
  }
  auto is_intersected(Rectangle const& other) const -> bool {
    return
      x < other.x + other.w &&
      y < other.y + other.h &&
      x + w > other.x &&
      y + h > other.y;
  }
  auto print(std::ostream& os = std::cout) const -> void {
    os << "Point(" << x << ',' << y << "), "
       << "Size("  << w << ',' << h << ")" << std::endl;
  }
};
}
}
