#ifndef MATHADDON_H
#define MATHADDON_H

#include <initializer_list>
#include <numbers>

const double CONSTANT_E{std::numbers::e};
const double CONSTANT_GAMMA{std::numbers::egamma};
const double CONSTANT_INV_PI{std::numbers::inv_pi};
const double CONSTANT_INV_SQRT_3{std::numbers::inv_sqrt3};
const double CONSTANT_INV_SQRT_PI{std::numbers::inv_sqrtpi};
const double CONSTANT_LN_10{std::numbers::ln10};
const double CONSTANT_LN_2{std::numbers::ln2};
const double CONSTANT_LOG10_E{std::numbers::log10e};
const double CONSTANT_LOG2_E{std::numbers::log2e};
const double CONSTANT_PHI{std::numbers::phi};
const double CONSTANT_PI{std::numbers::pi};
const double CONSTANT_SQRT_2{std::numbers::sqrt2};
const double CONSTANT_SQRT_3{std::numbers::sqrt3};

int all(const std::initializer_list<double> arguments);
int any(const std::initializer_list<double> arguments);
int eq(const double a, const double b);
int ge(const double a, const double b);
int gt(const double a, const double b);
int indexMax(const std::initializer_list<double> arguments);
int indexMin(const std::initializer_list<double> arguments);
int le(const double a, const double b);
int lt(const double a, const double b);
double max(const double a, const double b);
double max(const std::initializer_list<double> arguments);
double min(const double a, const double b);
double min(const std::initializer_list<double> arguments);
double mod(const double a, const double b);
double root(const double a, const double n);
int sign(const double a);

#endif
