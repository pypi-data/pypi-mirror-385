#include "mathaddon.h"

#include <algorithm>
#include <cmath>
#include <initializer_list>
#include <iterator>

int all(const std::initializer_list<double> arguments) {
  for (double number : arguments) {
    if (number == 0.0) {
      return 0;
    }
  }

  return 1;
}

int any(const std::initializer_list<double> arguments) {
  for (double number : arguments) {
    if (number != 0.0) {
      return 1;
    }
  }

  return 0;
}

int eq(const double a, const double b) {
  if (a == b)
    return 1;
  else
    return 0;
}

int ge(const double a, const double b) {
  if (a >= b)
    return 1;
  else
    return 0;
}

int gt(const double a, const double b) {
  if (a > b)
    return 1;
  else
    return 0;
}

int indexMax(const std::initializer_list<double> arguments) {
  auto itMax{std::max_element(arguments.begin(), arguments.end())};
  return static_cast<int>(std::distance(arguments.begin(), itMax));
}

int indexMin(const std::initializer_list<double> arguments) {
  auto itMin{std::min_element(arguments.begin(), arguments.end())};
  return static_cast<int>(std::distance(arguments.begin(), itMin));
}

int le(const double a, const double b) {
  if (a <= b)
    return 1;
  else
    return 0;
}

int lt(const double a, const double b) {
  if (a < b)
    return 1;
  else
    return 0;
}

double max(const double a, const double b) { return std::max(a, b); }

double max(const std::initializer_list<double> arguments) {
  return std::max(arguments);
}

double min(const double a, const double b) { return std::min(a, b); }

double min(const std::initializer_list<double> arguments) {
  return std::min(arguments);
}

double mod(const double a, const double b) {
  if (b == 0)
    return a;
  else if (a == b)
    return 0;
  return sign(b) * std::abs(a - floor(a / b) * b);
}

double root(const double a, const double n) { return std::pow(a, 1.0 / n); }

int sign(const double a) {
  return (a == 0.0) ? 0 : ((a > 0.0) ? 1 : ((a < 0.0) ? -1 : 0));
}
