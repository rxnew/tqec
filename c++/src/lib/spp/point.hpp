#pragma once

namespace tqec {
namespace spp {
struct Point2D {
  int x;
  int y;

  Point2D() : x(0), y(0) {}
  Point2D(int x, int y) : x(x), y(y) {}
  Point2D(Point2D const& other) : x(other.x), y(other.y) {}
  virtual ~Point2D() = default;

  auto operator=(Point2D const& other) -> Point2D& {
    x = other.x;
    y = other.y;
    return *this;
  }

  auto operator==(Point2D const& other) const -> bool {
    return x == other.x && y == other.y;
  }
  auto operator!=(Point2D const& other) const -> bool {
    return !(*this == other);
  }
  auto operator<(Point2D const& other) const -> bool {
    return y < other.y || (y == other.y && x < other.x);
  }
  auto operator>(Point2D const& other) const -> bool {
    return !(*this == other || *this < other);
  }
  auto print(std::ostream& os = std::cout) const -> void {
    os << "Point(" << x << ',' << y << ")" << std::endl;
  }
};

struct Point3D : Point2D {
  int z;

  Point3D() : Point2D(), z(0) {}
  Point3D(int x, int y, int z) : Point2D(x, y), z(z) {}
  Point3D(Point3D const& other) : Point2D(other), z(other.z) {}
  virtual ~Point3D() noexcept = default;

  auto operator=(Point3D const& other) -> Point3D& {
    Point2D::operator=(other);
    z = other.z;
    return *this;
  }

  auto operator==(Point3D const& other) const -> bool {
    return Point2D::operator==(other) && z == other.z;
  }
  auto operator!=(Point3D const& other) const -> bool {
    return !(*this == other);
  }
  auto operator<(Point3D const& other) const -> bool {
    return z < other.z || (z == other.z && Point2D::operator<(other));
  }
  auto operator>(Point3D const& other) const -> bool {
    return !(*this == other || *this < other);
  }
  auto print(std::ostream& os = std::cout) const -> void {
    os << "Point(" << x << ',' << y << ',' << z << ")" << std::endl;
  }
};
}
}
