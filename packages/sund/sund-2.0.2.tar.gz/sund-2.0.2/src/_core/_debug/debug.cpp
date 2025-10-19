#include "debug.h"
#include <iostream>

bool debug::DEBUG = false;

// Define method table here (single definition)
PyMethodDef debug::debugMethods[] = {
    {"disable_debug", (PyCFunction)debug::disableDebug, METH_NOARGS,
     "disable debug mode"},
    {"enable_debug", (PyCFunction)debug::enableDebug, METH_NOARGS,
     "enable debug mode"},
    {"is_debug", (PyCFunction)debug::isDebug, METH_NOARGS,
     "Returns true if debug mode is active"},
    {NULL, NULL, 0, NULL}};

// Define the module here (single definition)
PyModuleDef debugModule = {PyModuleDef_HEAD_INIT,
                           "sund._debug", // m_name
                           nullptr,       // m_doc
                           -1,            // m_size
                           debug::debugMethods,
                           nullptr,
                           nullptr,
                           nullptr,
                           nullptr};

// Undefine the macro in this file to avoid conflicts
#ifdef debugPrint
#undef debugPrint
#endif

PyObject *debug::disableDebug() {
  debug::debugPrint("_debug", "disableDebug", "SET DEBUG MODE TO FALSE");
  debug::DEBUG = false;
  Py_RETURN_NONE;
}

PyObject *debug::enableDebug() {
  std::cout << "enableDebug called, setting DEBUG to true" << std::endl;
  debug::DEBUG = true;
  std::cout << "DEBUG is now: " << debug::DEBUG << std::endl;
  Py_RETURN_NONE;
}

PyObject *debug::isDebug() {
  if (debug::DEBUG) {
    debug::debugPrint("_debug", "isDebug", "RETURN TRUE");
    Py_RETURN_TRUE;
  } else {
    Py_RETURN_FALSE;
  }
}

void debug::debugPrint(std::string instance, std::string function,
                       std::string message) {
  if (debug::DEBUG) {
    // Escape single quotes in the message
    std::string escaped_message = message;
    size_t pos = 0;
    while ((pos = escaped_message.find("'", pos)) != std::string::npos) {
      escaped_message.replace(pos, 1, "\\'");
      pos += 2;
    }

    std::string python_code = "print('DEBUG: " + instance + " - " + function +
                              ": " + escaped_message + "')";
    PyRun_SimpleString(python_code.c_str());
  }
}

PyMODINIT_FUNC PyInit__debug(void) { return PyModule_Create(&debugModule); }