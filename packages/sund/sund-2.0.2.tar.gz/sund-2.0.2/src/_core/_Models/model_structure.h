#ifndef _MODEL_STRUCTURE_H
#define _MODEL_STRUCTURE_H

#include "Python.h"

#include <vector>

#define MODEL_STATE 0
#define MODEL_FEATURE 1
#define MODEL_OUTPUT 2
#define MODEL_INPUT 3
#define MODEL_EVENT 4
#define MODEL_PARAMETER 5

/*
==========================================================================================
Structure definitions
==========================================================================================
*/
typedef void ModelFunction(double time, double timescale, double *statevalues,
                           double *derivativevalues, double *RESvector,
                           double *parametervector, double *featurevector,
                           double *outputvector, double **inputvector,
                           double *eventvector, int *eventstatus, int DOflag);
typedef void ICFunction(double *icvector, double *dericvector,
                        double *parametervector,
                        const std::vector<double> &inputs);

// Model structure
typedef struct {
  ModelFunction *const function;
  ICFunction *const initialcondition;
  const int *const numberof;
  const char **const statenames;
  const char **const featurenames;
  const char **const featureunits;
  const char **const outputnames;
  const char **const inputnames;
  const char **const parameternames;
  const char **const eventnames;
  const int *const differentialstates;
  const int *const inputdependency;
  const double *const defaultparameters;
  const char *const timeunit;
  const int has_algebraic_eq;
  const int *const mandatoryinputs; // 0 = mandatory, 1 = non-mandatory, 2 =
                                    // non-mandatory - zero default value
  const std::vector<double> defaultInputs;
} ModelStructure;

// Model object
typedef struct {
  PyObject_HEAD ModelStructure *model; // reference to model structure
  PyObject *name;
  PyObject *compartment;
  PyObject *statevalues;
  PyObject *derivativevalues;
  PyObject *idvector;
  PyObject *parametervalues;
  PyObject *statenames;
  PyObject *featurenames;
  PyObject *featureunits;
  PyObject *outputnames;
  PyObject *inputnames;
  PyObject *parameternames;
  PyObject *eventnames;
  PyObject *timeunit;
} ModelObject;

#endif
