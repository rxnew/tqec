#include "spp3.hpp"

namespace tqec {
namespace spp {
auto Spp3::NfCompare::operator()(RecPtr const& lhs, RecPtr const& rhs)
  -> bool {
  return lhs->front_surface() < rhs->front_surface();
}

auto Spp3::NbCompare::operator()(RecPtr const& lhs, RecPtr const& rhs)
  -> bool {
  return lhs->back_surface() < rhs->back_surface();
}

auto Spp3::_solve() -> void {
  auto status = _step1();

  while(true) {
    //std::cout << "step: " << status << std::endl;
    //_print_status();
    switch(status) {
      case 0:  return;
      case 1:  status = _step1();  break;
      case 2:  status = _step2();  break;
      case 3:  status = _step3();  break;
      case 4:  status = _step4();  break;
      case 5:  status = _step5();  break;
      case 6:  status = _step6();  break;
      case 7:  status = _step7();  break;
      case 8:  status = _step8();  break;
      case 9:  status = _step9();  break;
      case 10: status = _step10(); break;
      default: assert(false);      break;
    }
  }
}

auto Spp3::_step1() -> int {
  n_ = sigma_.size();
  placed_.clear();
  e_.clear();
  nf_.clear();
  nb_.clear();
  auto front_ptr = std::make_shared<Rectangular>(container_front_surface_);
  nf_.insert(front_ptr);
  nb_.insert(front_ptr);
  placed_.insert(front_ptr);
  s_ = 0;
  return 2;
}

auto Spp3::_step2() -> int {
  if(s_ == n_) return 10; // goto Step 10
  i_ = sigma_[s_];
  ++s_;
  bl_ = Point(INF, INF, INF);
  lf_ = 0;
  lb_ = 0;
  jf_ = nf_[lf_];
  jb_ = nb_[lb_];
  //jb_->print();
  floor_ = 0;
  interim_bl_ = Point(INF, INF, INF);
  x_end_ = container_back_surface_.x + container_back_surface_.w - i_->w;
  y_end_ = container_back_surface_.y + container_back_surface_.h - i_->h;
  return 3;
}

auto Spp3::_step3() -> int {
  nfp_.clear();
  for(auto const& j : placed_) {
    nfp_[j] = _make_nfp(j, i_);
  }
  return 4;
}

auto Spp3::_step4() -> int {
  if(floor_ == 0) {
    //jb_->print();
    //std::cout << nfp_[jb_]->back_surface().z << std::endl;
    //std::cout << jb_->z - i_->d << std::endl;
    //std::cout << std::endl;
    if(nfp_[jb_]->back_surface().z < container_back_surface_.z) {
      return 5; // goto Step 5
    }
    else {
      return 8; // goto Step 8
    }
  }
  else if(floor_ == 1) {
    if(nfp_[jb_]->back_surface().z < nfp_[jf_]->front_surface().z) {
      //std::cout << "goto 5" << std::endl;
      return 5; // goto Step 5
    }
    else {
      //std::cout << "goto 6" << std::endl;
      return 6; // goto Step 6
    }
  }
  return -1;
}

auto Spp3::_step5() -> int {
  if(lb_ == placed_.size() - 1) return 6; // goto Step 6?
  e_.insert(jb_);
  ++lb_;
  //std::cout << "m: " << placed_.size() << std::endl;
  //std::cout << "lb: " << lb_ << std::endl;
  //std::cout << "jb[lb]" << std::flush;
  jb_ = nb_[lb_];
  //std::cout << " accessed" << std::endl;
  return 4; // goto Step 4
}

auto Spp3::_step6() -> int {
  e_.erase(jf_);
  auto ed = std::unordered_set<RecPtr>();
  auto front = nfp_[jf_]->front_surface();
  for(auto const& j : nfp_) {
    if(j.first == jf_) {
      continue;
    }
    if(front.is_intersected(*j.second)) {
      ed.insert(j.first);
    }
  }
  //std::cout << "i: ";
  //i_->print();
  //std::cout << "jf: ";
  //jf_->print();
  //std::cout << "NFP(jf, i): ";
  //nfp_[jf_]->print();
  auto bl = _find_2d_bl(ed, front);
  //bl.print();
  if(_is_avairable(bl)) interim_bl_ = std::min(interim_bl_, bl);
  //std::cout << "interim_bl: ";
  //interim_bl_.print();
  return 7;
}

auto Spp3::_step7() -> int {
  //if(_make_nfp(nf_[lf_ + 1], i_)->front_surface().get_point() < bl_) {
  if(nf_.size() <= lf_ - 1 &&
     _make_nfp(nf_[lf_ + 1], i_)->front_surface().get_point() < bl_) {
    ++lf_;
    //std::cout << "lf: " << lb_ << std::endl;
    //std::cout << "jf[lf]" << std::flush;
    jf_ = nf_[lf_];
    //std::cout << " accessed" << std::endl;
    return 4; // goto Step 4
  }
  bl_ = interim_bl_;
  //std::cout << "interim_bl: ";
  //interim_bl_.print();
  return 9; // goto Step 9
}

auto Spp3::_step8() -> int {
  auto bl = _find_2d_bl(e_, container_back_surface_);
  //bl.print();
  floor_ = 1;
  if(!_is_avairable(bl)) return 4; // goto Step4
  bl_ = bl;
  return 9; // goto Step 9
}

auto Spp3::_step9() -> int {
  i_->set_point(bl_);
  //i_->print();
  placed_.insert(i_);
  nf_.insert(i_);
  nb_.insert(i_);
  //std::cout << "nf: " << std::endl;
  //for(auto i = 0; i < nf_.size(); i++) nf_[i]->print();
  //std::cout << "nb: " << std::endl;
  //for(auto i = 0; i < nb_.size(); i++) nb_[i]->print();
  return 2; // goto Step 2
}

auto Spp3::_step10() -> int {
  return 0;
}

auto Spp3::_find_2d_bl(std::unordered_set<RecPtr> const& rectangulars,
                       Rectangular const& surface) const -> Point {
  //_print_status();
  //std::cout << "surface: ";
  //surface.print();
  auto x_begin = std::max(container_back_surface_.x, surface.x);
  auto y_begin = std::max(container_back_surface_.y, surface.y);
  auto x_end = std::min(x_end_, surface.x + surface.w);
  auto y_end = y_end_;
  for(auto sweep_line = y_begin; sweep_line <= y_end; ++sweep_line) {
    for(auto x = x_begin; x <= x_end; ++x) {
      auto const point = Point2D(x, sweep_line);
      auto non_intersected = true;
      for(auto const& rectangular : rectangulars) {
        non_intersected &=
          !nfp_.at(rectangular)->to_rectangle().is_intersected(point);
        if(!non_intersected) break;
      }
      if(non_intersected) return Point(x, sweep_line, surface.z);
    }
  }
  return Point(INF, INF, INF);
}

auto Spp3::_make_nfp(RecPtr const& i, RecPtr const& j) const
  -> RecPtr {
  auto x = i->x - j->w;
  auto y = i->y - j->h;
  auto z = i->z - j->d;

  auto w = i->w + j->w;
  auto h = i->h + j->h;
  auto d = i->d + j->d;

  return std::make_shared<Rectangular>(x, y, z, w, h, d);
}

auto Spp3::_is_avairable(Point const& point) const -> bool {
  static auto const no_avairable_point = Point(INF, INF, INF);
  return point != no_avairable_point;
}
}
}
