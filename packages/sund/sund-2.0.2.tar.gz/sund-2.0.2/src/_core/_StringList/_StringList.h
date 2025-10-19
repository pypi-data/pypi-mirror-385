#ifndef _STRINGLIST_H
#define _STRINGLIST_H

#include "Python.h"

/*
==========================================================================================
Structure definitions
==========================================================================================
*/
typedef struct {
  PyListObject list;
  int readonly;
} StringListObject;

int StringList_init(StringListObject *self, PyObject *args, PyObject *kwds);

/*
==========================================================================================
Function declaration
==========================================================================================
*/
int StringList_SetItem(PyObject *self, PyObject *key, PyObject *value);

PyObject *StringList_append(StringListObject *self, PyObject *notuse);

PyObject *StringList_extend(StringListObject *self, PyObject *notuse);

PyObject *StringList_insert(StringListObject *self, PyObject *notuse);

PyObject *StringList_remove(StringListObject *self, PyObject *notuse);

PyObject *StringList_pop(StringListObject *self, PyObject *notuse);

PyObject *StringList_Reduce(StringListObject *self);

PyObject *StringList_SetState(StringListObject *self, PyObject *statetuple);

// Disallow reordering operations that would break external data alignment
PyObject *StringList_sort(StringListObject *self, PyObject *args,
                          PyObject *kwds);
PyObject *StringList_reverse(StringListObject *self, PyObject *args,
                             PyObject *kwds);

/*
==========================================================================================
C_API function declarations
==========================================================================================
*/
int StringList_SetItemInit(PyObject *self, PyObject *key, PyObject *value);

int StringList_Update(PyObject *self, PyObject *value);

PyObject *StringList_New(int size, int readonly);

/*
==========================================================================================
Python module definitions
==========================================================================================
*/
static PyMethodDef StringList_methods[] = {
    {"append", (PyCFunction)StringList_append, METH_VARARGS,
     "Overwritten append function"},
    {"extend", (PyCFunction)StringList_extend, METH_VARARGS,
     "Overwritten extend function"},
    {"insert", (PyCFunction)StringList_insert, METH_VARARGS,
     "Overwritten insert function"},
    {"remove", (PyCFunction)StringList_remove, METH_VARARGS,
     "Overwritten remove function"},
    {"pop", (PyCFunction)StringList_pop, METH_VARARGS,
     "Overwritten pop function"},
    {"__reduce__", (PyCFunction)StringList_Reduce, METH_NOARGS,
     "__reduce__ function"},
    {"__setstate__", (PyCFunction)StringList_SetState, METH_VARARGS,
     "__setstate__ function"},
    {"sort", (PyCFunction)StringList_sort, METH_VARARGS | METH_KEYWORDS,
     "Disabled: sorting a StringList would desynchronize associated data"},
    {"reverse", (PyCFunction)StringList_reverse, METH_VARARGS | METH_KEYWORDS,
     "Disabled: reversing a StringList would desynchronize associated data"},
    {NULL} /* Sentinel */
};

static PyMappingMethods StringListMapping = {
    .mp_ass_subscript = (objobjargproc)StringList_SetItem,
};

static PyTypeObject StringListType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name =
        "sund._StringList.StringList",
    .tp_basicsize = sizeof(StringListObject),
    .tp_itemsize = 0,
    .tp_as_mapping = &StringListMapping,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_doc = "StringList type object",
    .tp_methods = StringList_methods,
    .tp_init = (initproc)StringList_init};

static PyModuleDef StringListModule = {.m_base = PyModuleDef_HEAD_INIT,
                                       .m_name = "sund._StringList",
                                       .m_doc = "StringList Module",
                                       .m_size = -1};

#endif