#pragma once

namespace tqec {
namespace spp {
struct Size2D {
  int w;
  int h;

  Size2D() : w(0), h(0) {}
  Size2D(int w, int h) : w(w), h(h) {}
  Size2D(Size2D const& other) : w(other.w), h(other.h) {}
  virtual ~Size2D() noexcept = default;

  auto operator=(Size2D const& other) -> Size2D& {
    w = other.w;
    h = other.h;
    return *this;
  }
  auto operator==(Size2D const& other) const -> bool {
    return w == other.w && h == other.h;
  }
  auto operator!=(Size2D const& other) const -> bool {
    return !(*this == other);
  }
};

struct Size3D : Size2D {
  int d;

  Size3D() : Size2D(), d(0) {}
  Size3D(int w, int h, int d) : Size2D(w, h), d(d) {}
  Size3D(Size3D const& other) : Size2D(other), d(other.d) {}
  virtual ~Size3D() noexcept = default;

  auto operator=(Size3D const& other) -> Size3D& {
    Size2D::operator=(other);
    d = other.d;
    return *this;
  }
  auto operator==(Size3D const& other) const -> bool {
    return Size2D::operator==(other) && d == other.d;
  }
  auto operator!=(Size3D const& other) const -> bool {
    return !(*this == other);
  }
};
}
}
