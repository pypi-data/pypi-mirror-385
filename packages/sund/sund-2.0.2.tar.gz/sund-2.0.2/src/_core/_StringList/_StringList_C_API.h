#ifndef _STRINGLIST_C_API_H
#define _STRINGLIST_C_API_H

#include "_StringList_C_API_defines.h"

#include "Python.h"

/*
==========================================================================================
C_API
==========================================================================================
*/
#define import_StringList()                                                    \
  {                                                                            \
    if (_import_StringList() < 0) {                                            \
      PyErr_Print();                                                           \
      PyErr_SetString(PyExc_ImportError,                                       \
                      "sund._StringList._C_API failed to import");             \
      return NULL;                                                             \
    }                                                                          \
  }
#define StringList_isStringList                                                \
  (*(StringList_isStringList_RETURN(*) StringList_isStringList_PROTO)          \
       StringList_API[StringList_isStringList_NUM])
#define StringList_SetItemInit                                                 \
  (*(StringList_SetItemInit_RETURN(*) StringList_SetItemInit_PROTO)            \
       StringList_API[StringList_SetItemInit_NUM])
#define StringList_Update                                                      \
  (*(StringList_Update_RETURN(*)                                               \
         StringList_Update_PROTO)StringList_API[StringList_Update_NUM])
#define StringList_New                                                         \
  (*(StringList_New_RETURN(*)                                                  \
         StringList_New_PROTO)StringList_API[StringList_New_NUM])

/* Return -1 on error, 0 on success.
 * PyCapsule_Import will set an exception if there's an error.
 */
static void **StringList_API;
static int _import_StringList(void) {
  StringList_API = (void **)PyCapsule_Import("sund._StringList._C_API", 0);
  return (StringList_API != NULL) ? 0 : -1;
}

#endif