#ifndef _MODELS_M_API_H
#define _MODELS_M_API_H

#include "model_structure.h"

#include "Python.h"

#define MODEL_STATE 0
#define MODEL_FEATURE 1
#define MODEL_OUTPUT 2
#define MODEL_INPUT 3
#define MODEL_EVENT 4
#define MODEL_PARAMETER 5

/*
==========================================================================================
Model Core (allocation / base type) API
==========================================================================================
*/
#define Model_alloc_NUM 0
#define Model_alloc_RETURN int
#define Model_alloc_PROTO (ModelObject * self)

#define Model_Base_Type_NUM 1
#define Model_Base_Type_RETURN PyTypeObject *

/* Total number of M API pointers */
#define Models_M_API_pointers 2

static void *
    *Models_API; /* shared pointer table for core (minimal) model API */
/* Import the core (minimal) Model API (allocator + base type) idempotently. */
static inline void import_ModelCoreAPI(void) {
  if (!Models_API) {
    Models_API = (void **)PyCapsule_Import("sund._Models._M_API", 0);
    if (!Models_API)
      Py_FatalError("sund: failed to import capsule 'sund._Models._M_API'");
  }
}
#define Model_alloc                                                            \
  (*(Model_alloc_RETURN(*) Model_alloc_PROTO)Models_API[Model_alloc_NUM])
#define Model_Base_Type ((PyTypeObject *)Models_API[Model_Base_Type_NUM])

#endif
