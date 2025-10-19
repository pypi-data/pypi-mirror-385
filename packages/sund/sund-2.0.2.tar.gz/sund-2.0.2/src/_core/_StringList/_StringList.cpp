#define _STRINGLIST_C

#include "_StringList.h"
#include "_StringList_C_API_defines.h"

#include <Python.h>
#define NPY_NO_DEPRECATED_API NPY_2_3_API_VERSION
#include <numpy/arrayobject.h>

/*
==========================================================================================
C_API functions
==========================================================================================
*/
static int StringList_isStringList(PyObject *list) {
  int k;

  if (!PyList_Check(list))
    return 0;
  for (k = 0; k < Py_SIZE(list); k++) {
    if (!PyUnicode_Check(((PyListObject *)list)->ob_item[k]))
      return 0;
  }
  return 1;
}

/*
==========================================================================================
PyMethods
==========================================================================================
*/
// new SetItem function for StringList
int StringList_SetItem(PyObject *self, PyObject *key, PyObject *value) {
  int r;
  int size;

  if (((StringListObject *)self)->readonly) {
    PyErr_SetString(PyExc_TypeError, "The StringList is read only");
    return -1;
  }

  if (!value) {
    PyErr_SetString(PyExc_TypeError, "Cannot delete item in StringList");
    return -1;
  }
  if (!PyUnicode_Check(value) && !StringList_isStringList(value)) {
    PyErr_SetString(PyExc_TypeError, "Only strings allowed in StringList");
    return -1;
  }

  // Pre-validate slice assignments so size never changes (length preserving
  // only)
  if (PySlice_Check(key)) {
    Py_ssize_t start, stop, step, slicelen;
    if (PySlice_GetIndicesEx(key, Py_SIZE(self), &start, &stop, &step,
                             &slicelen) < 0)
      return -1; // error already set

    if (PyUnicode_Check(value)) {
      // Reject multi-element slice replacement with a raw string (would iterate
      // characters)
      if (slicelen != 1) {
        PyErr_SetString(
            PyExc_TypeError,
            "Cannot assign a string to a slice of length != 1 in StringList");
        return -1;
      }
      // Perform an index assignment directly to avoid Python treating the
      // string as an iterable of chars
      PyObject *indexObj = PyLong_FromSsize_t(start);
      if (!indexObj)
        return -1;
      int orig_size = Py_SIZE(self);
      int rr = Py_TYPE(self)->tp_base->tp_as_mapping->mp_ass_subscript(
          self, indexObj, value);
      Py_DECREF(indexObj);
      if (rr < 0)
        return -1;
      if (Py_SIZE(self) != orig_size) {
        PyErr_SetString(PyExc_TypeError,
                        "Internal error: StringList resized during "
                        "single-element string assignment");
        return -1;
      }
      return rr; // Done; skip generic slice handling path
    } else if (StringList_isStringList(value)) {
      if (Py_SIZE(value) != slicelen) {
        // Distinguish full-slice replacement (attempt to change overall length)
        if (start == 0 && step == 1 && stop == Py_SIZE(self)) {
          PyErr_Format(PyExc_TypeError,
                       "Cannot replace entire StringList with different length "
                       "(expected %zd, got %zd)",
                       (Py_ssize_t)Py_SIZE(self), (Py_ssize_t)Py_SIZE(value));
        } else {
          PyErr_SetString(PyExc_TypeError, "StringList is not resizeable");
        }
        return -1;
      }
      // fall through to generic slice handling below after full validation
    } else {
      // Should not reach due to earlier type gating, but keep defensive check
      PyErr_SetString(PyExc_TypeError,
                      "Unsupported slice assignment type for StringList");
      return -1;
    }
  }

  size = Py_SIZE(self); // store size for compare

  // Update StringList using the base type PyList_Type assign function
  r = Py_TYPE(self)->tp_base->tp_as_mapping->mp_ass_subscript(self, key, value);

  if (size != Py_SIZE(self)) {
    PyErr_SetString(PyExc_TypeError, "StringList is not resizable (attempted "
                                     "implicit resize in assignment)");
    return -1;
  }

  return r;
}

// Function to redefine since StringList are non-resizeable
PyObject *StringList_append(StringListObject *self, PyObject *notuse) {
  PyErr_SetString(PyExc_TypeError, "StringList are not resizeable");
  return NULL;
}

PyObject *StringList_extend(StringListObject *self, PyObject *notuse) {
  PyErr_SetString(PyExc_TypeError, "StringList are not resizeable");
  return NULL;
}

PyObject *StringList_insert(StringListObject *self, PyObject *notuse) {
  PyErr_SetString(PyExc_TypeError, "StringList are not resizeable");
  return NULL;
}

PyObject *StringList_remove(StringListObject *self, PyObject *notuse) {
  PyErr_SetString(PyExc_TypeError, "StringList are not resizeable");
  return NULL;
}

PyObject *StringList_pop(StringListObject *self, PyObject *notuse) {
  PyErr_SetString(PyExc_TypeError, "StringList are not resizeable");
  return NULL;
}

// Explicitly disable sort to prevent reordering without paired data updates
PyObject *StringList_sort(StringListObject *self, PyObject *args,
                          PyObject *kwds) {
  PyErr_SetString(PyExc_TypeError, "Sorting StringList is not allowed");
  return NULL;
}

// Explicitly disable reverse for the same reason
PyObject *StringList_reverse(StringListObject *self, PyObject *args,
                             PyObject *kwds) {
  PyErr_SetString(PyExc_TypeError, "Reversing StringList is not allowed");
  return NULL;
}

PyObject *StringList_Reduce(StringListObject *self) {
  int k;
  PyObject *ret, *args, *state, *tmp;

  state = PyList_New(((PyVarObject *)self)->ob_size);
  for (k = 0; k < PyList_Size(state); k++) {
    tmp = PyList_GetItem((PyObject *)self, k);
    Py_INCREF(tmp);
    PyList_SetItem(state, k, tmp);
  }

  args = Py_BuildValue("ii", ((PyVarObject *)self)->ob_size, self->readonly);
  ret = Py_BuildValue("OOO", Py_TYPE(self), args, state);
  Py_DECREF(args);
  Py_DECREF(state);
  return ret;
}

PyObject *StringList_SetState(StringListObject *self, PyObject *statetuple) {
  int k;
  PyObject *tmp, *state;

  if (!PyArg_Parse(statetuple, "(O,)", &state))
    return NULL;

  if (!PyList_Check(state)) {
    PyErr_SetString(PyExc_TypeError, "State needs to be a list type");
    return NULL;
  }
  if (PyList_Size((PyObject *)self) != PyList_Size(state)) {
    PyErr_SetString(PyExc_TypeError,
                    "State contains incorrect number of elements");
    return NULL;
  }
  for (k = 0; k < PyList_Size(state); k++) {
    tmp = PyLong_FromLong(k);
    StringList_SetItem((PyObject *)self, tmp, PyList_GetItem(state, k));
    Py_DECREF(tmp);
  }

  Py_RETURN_NONE;
}

/*
==========================================================================================
StringListType definition
==========================================================================================
*/
int StringList_init(StringListObject *self, PyObject *args, PyObject *kwds) {
  PyObject *tmp{PyTuple_New(0)};
  PyObject *tmp2{PyDict_New()};

  static char *kwlist[] = {const_cast<char *>("size"),
                           const_cast<char *>("readonly"), NULL};

  int size{};
  int readonly{};

  // initiate parent object
  if (PyList_Type.tp_init((PyObject *)self, tmp, tmp2) < 0) {
    Py_DECREF(tmp);
    Py_DECREF(tmp2);
    return -1;
  }
  Py_DECREF(tmp);
  Py_DECREF(tmp2);

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "ii", kwlist, &size, &readonly))
    return -1;

  if (size < 0) {
    PyErr_SetString(PyExc_TypeError,
                    "Only non-negative StringList are possible");
    return -1;
  }
  if (size > 0) {
    ((PyListObject *)self)->ob_item =
        (PyObject **)PyMem_Calloc(size, sizeof(PyObject *));
    if (((PyListObject *)self)->ob_item == NULL) {
      PyErr_NoMemory();
      return -1;
    }
  } else
    ((PyListObject *)self)->ob_item = NULL;

  ((PyVarObject *)self)->ob_size = size;
  ((PyListObject *)self)->allocated = size;

  for (int k = 0; k < size; k++) {
    Py_INCREF(Py_None);
    ((PyListObject *)self)->ob_item[k] = Py_None;
  }

  if (readonly)
    self->readonly = 1;
  else
    self->readonly = 0;

  return 0;
}

/*
==========================================================================================
C_API functions
==========================================================================================
*/
int StringList_SetItemInit(PyObject *self, PyObject *key, PyObject *value) {
  StringListObject *tmp;
  int r, readonly;

  tmp = (StringListObject *)self;
  readonly = tmp->readonly;
  tmp->readonly = 0;
  r = StringList_SetItem(self, key, value);

  tmp->readonly = readonly;

  return r;
}

int StringList_Update(PyObject *self, PyObject *value) {
  PyObject *slice, *start, *stop;
  int r;

  start = PyLong_FromLong(0);
  stop = PyLong_FromLong(Py_SIZE(value));
  slice = PySlice_New(start, stop, NULL);
  r = StringList_SetItem(self, slice, value);
  Py_DECREF(start);
  Py_DECREF(stop);
  Py_DECREF(slice);

  return r;
}

PyObject *StringList_New(int size, int readonly) {
  PyObject *argList, *ob;

  argList = Py_BuildValue("(ii)", size, readonly);
  ob = PyObject_CallObject((PyObject *)&StringListType, argList);
  Py_DECREF(argList);
  return ob;
}

/*
==========================================================================================
StringList module definition
==========================================================================================
*/
PyMODINIT_FUNC PyInit__StringList(void) {
  PyObject *m;

  static void *StringList_API[StringList_API_pointers];
  PyObject *c_api_object;

  m = PyModule_Create(&StringListModule);
  if (m == NULL)
    return NULL;

  /* Initialize the C API pointer array */
  StringList_API[StringList_isStringList_NUM] = (void *)StringList_isStringList;
  StringList_API[StringList_SetItemInit_NUM] = (void *)StringList_SetItemInit;
  StringList_API[StringList_Update_NUM] = (void *)StringList_Update;
  StringList_API[StringList_New_NUM] = (void *)StringList_New;

  /* Create a Capsule containing the API pointer array's address */
  c_api_object =
      PyCapsule_New((void *)StringList_API, "sund._StringList._C_API", NULL);

  // StringList/Simulation
  StringListType.tp_base = &PyList_Type;
  if (PyType_Ready(&StringListType) < 0) {
    Py_DECREF(m);
    return NULL;
  }

  Py_INCREF(&StringListType);

  if (PyModule_AddObject(m, "StringList", (PyObject *)&StringListType) < 0 ||
      PyModule_AddObject(m, "_C_API", c_api_object) < 0) {
    Py_DECREF(&StringListType);
    Py_XDECREF(c_api_object);
    Py_DECREF(m);
    return NULL;
  }

  import_array();
  return m;
}
