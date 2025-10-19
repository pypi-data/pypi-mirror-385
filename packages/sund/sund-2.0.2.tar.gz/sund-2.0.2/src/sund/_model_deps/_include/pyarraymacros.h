#include "Python.h"

#define PYARRAY(arr) ((PyArrayObject *)(arr))
#define PYSIZE(arr) (PyArray_SIZE(PYARRAY(arr)))
#define PYDATA(arr) ((double *)PyArray_DATA(PYARRAY(arr)))
#define PYDATAINT(arr) ((int *)PyArray_DATA(PYARRAY(arr)))