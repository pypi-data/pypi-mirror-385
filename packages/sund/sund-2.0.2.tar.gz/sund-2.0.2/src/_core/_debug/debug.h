#pragma once

#include "Python.h"
#include <string>

namespace debug {
extern bool DEBUG;

PyObject *disableDebug();
PyObject *enableDebug();
PyObject *isDebug();

void debugPrint(std::string instance, std::string function,
                std::string message);
extern PyMethodDef debugMethods[]; // defined in debug.cpp
} // namespace debug

// Single-definition refactor: the actual PyModuleDef instance now lives in
// debug.cpp
extern PyModuleDef debugModule;

PyMODINIT_FUNC PyInit__debug(void);

#define debugPrint(instance, function, message)                                \
  do {                                                                         \
    if (debug::DEBUG)                                                          \
      debug::debugPrint(instance, function, message);                          \
  } while (0)
