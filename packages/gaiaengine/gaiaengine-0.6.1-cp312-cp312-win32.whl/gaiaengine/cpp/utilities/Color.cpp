#include "Color.h"

Color::Color(const std::string& hexColorCode)
{
  if ((hexColorCode.length() != 7 && hexColorCode.length() != 9) || hexColorCode[0] != '#')
    throw std::invalid_argument("Wrong format, please enter a RGB or RGBA hex color code (e.g. #FFFFFF or #FFFFFFFF)");

  r = (Uint8) stoi(hexColorCode.substr(1, 2), nullptr, 16);
  g = (Uint8) stoi(hexColorCode.substr(3, 2), nullptr, 16);
  b = (Uint8) stoi(hexColorCode.substr(5, 2), nullptr, 16);

  if (hexColorCode.length() == 9)
    a = (Uint8) stoi(hexColorCode.substr(7, 2), nullptr, 16);
  else
    a = 255;
}

Color::Color(const SDL_Color& color):
  r(color.r),
  g(color.g),
  b(color.b),
  a(color.a)
{}

Color::Color(float r_, float g_, float b_):
  Color(r_, g_, b_, 1.f)
{}

Color::Color(float r_, float g_, float b_, float a_):
  r((Uint8) (r_ * 255)),
  g((Uint8) (g_ * 255)),
  b((Uint8) (b_ * 255)),
  a((Uint8) (a_ * 255))
{
  if (r_ < 0.f || r_ > 1.f || g_ < 0.f || g_ > 1.f || b_ < 0.f || b_ > 1.f || a_ < 0.f || a_ > 1.f)
    throw std::domain_error("Parameter out of bounds, please enter float values between 0 and 1 or int values between 0 and 255");
}

Color::Color(Uint8 r_, Uint8 g_, Uint8 b_):
  Color(r_, g_, b_, 255)
{}

Color::Color(Uint8 r_, Uint8 g_, Uint8 b_, Uint8 a_):
  r(r_),
  g(g_),
  b(b_),
  a(a_)
{}

#include <pybind11/pybind11.h>
#include <pybind11/operators.h>

namespace py = pybind11;

void Color::pythonBindings(py::module& m) {
  py::class_<Color>(m, "Color")
    .def(py::init<>())
    .def(py::init<const std::string&>())
    .def(py::init<Uint8, Uint8, Uint8>())
    .def(py::init<Uint8, Uint8, Uint8, Uint8>())
    .def(py::init<float, float, float>())
    .def(py::init<float, float, float, float>())
    .def_readwrite("r", &Color::r)
    .def_readwrite("g", &Color::g)
    .def_readwrite("b", &Color::b)
    .def_readwrite("a", &Color::a)
    .def_property("rf", &Color::getFloatR, &Color::setFloatR)
    .def_property("gf", &Color::getFloatG, &Color::setFloatG)
    .def_property("bf", &Color::getFloatB, &Color::setFloatB)
    .def_property("af", &Color::getFloatA, &Color::setFloatA)
    .def_property("rgb", &Color::getRGBTuple, &Color::setRGBTuple)
    .def_property("rgbf", &Color::getRGBTupleFloat, &Color::setRGBTupleFloat)
    .def_property("rgba", &Color::getRGBATuple, &Color::setRGBATuple)
    .def_property("rgbaf", &Color::getRGBATupleFloat, &Color::setRGBATupleFloat)
    .def(py::self == py::self);
}
