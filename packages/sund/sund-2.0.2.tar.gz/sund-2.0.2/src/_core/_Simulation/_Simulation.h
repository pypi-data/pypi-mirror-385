#ifndef _SIMULATION_H
#define _SIMULATION_H

#include "Models_C_API.h"
#include "debug.h"
#include "sund_sundials_interface.h"
#include "timescales.h"

#include "Python.h"

#include <map>
#include <string>
#include <vector>

/*
==========================================================================================
Simulation defines
==========================================================================================
*/
// MODEL MACROS
#define STATEVECTOR &statevalues[offset[MODEL_STATE]]
#define DERIVATEVECTOR &derivativevalues[offset[MODEL_STATE]]
#define RESIDUALVECTOR &RESvector[offset[MODEL_STATE]]
#define PARAMETERVECTOR &parametervalues[offset[MODEL_PARAMETER]]
#define FEATUREVECTOR &featurevector[offset[MODEL_FEATURE]]
#define OUTPUTVECTOR &self->outputbuffer[offset[MODEL_OUTPUT]]
#define INPUTVECTOR &self->inputptr[offset[MODEL_INPUT]]
#define EVENTVECTOR &eventvector[offset[MODEL_EVENT]]
#define EVENTSTATUS &eventstatus[offset[MODEL_EVENT]]
#define MODELFUNCTION (mod->function)
#define HASOUTPUT (mod->hasoutput)
#define SCALE (mod->scale)

// ACTIVITY MACROS
#define A_OUTPUTVECTOR &self->outputbuffer[offset[ACTIVITY_OUTPUT]]
#define A_FEATUREVECTOR &featurevector[offset[ACTIVITY_FEATURE]]
#define A_SCALE (act->scale)

#define ATTRIBUTE_FEATURE_NAME 0
#define ATTRIBUTE_FEATURE_UNIT 1
#define ATTRIBUTE_OUTPUT_NAME 2
#define ATTRIBUTE_INPUT_NAME 3
#define ATTRIBUTE_PARAMETER_NAME 4
#define ATTRIBUTE_STATE_NAME 5
#define ATTRIBUTE_EVENT_NAME 6
#define ATTRIBUTE_STATE_VALUE 7
#define ATTRIBUTE_DERIVATE_VALUE 8
#define ATTRIBUTE_PARAMETER_VALUE 9

/*
==========================================================================================
Structure definitions
==========================================================================================
*/

typedef struct {
  PyObject *modelObject;
  ModelFunction *function;
  int offset[6];
  int hasoutput;
  int exOrder;
  double scale;
  int originalIndex;
} SimulationModel;

typedef struct {
  PyObject *activityObject;
  int offset[2];
  double scale;
} SimulationActivity;

typedef struct SimulationObject {
  PyObject_HEAD
      // models and activities
      SimulationModel *models;
  SimulationActivity *activities;
  // model simulation data
  PyObject *statevalues;
  PyObject *derivativevalues;
  PyObject *idvector;
  PyObject *parametervalues;
  // model attributes
  PyObject *featurenames;
  PyObject *featureunits;
  PyObject *outputnames;
  PyObject *inputnames;
  PyObject *parameternames;
  PyObject *statenames;
  PyObject *eventnames;
  // simulation data
  SUNDIALSObject *sundials;
  PyObject *timevector;
  PyObject *featurevalues;
  PyObject *featuredata; // deprecated
  PyObject *eventtimedata;
  PyObject *eventstatusdata;
  int sharedvariablescheck;
  int numberof[8];
  double *outputbuffer;
  double **inputptr;
  int *inputmap;
  double *defaultInputValues;
  double scale;
  int has_algebraic_eq;
  bool sundials_initialized;
  // For iterative simulation
  std::vector<std::vector<double>> subTimeVectors;
  PyObject *internalTimeVector; // Internal vector used for calculating the
                                // subTimeVectors, and simulation
  // SUNDIALS options
  // std::map is for some reason incompatible with current structure (only on
  // Windows, apparently). Replaced with separate containers for keys and
  // values.
  std::vector<std::string> optionKeys{};
  std::vector<double> optionValues{};
} SimulationObject;

/*
==========================================================================================
Function declaration
==========================================================================================
*/

/*
 * Check if event conditions are true before simulation and apply appropriate
 * events
 */
void applyInitialEvents(SimulationObject *self);

/*
 * Reconstruction helper for serialization support with keyword-only constructor
 */
static PyObject *_reconstruct_simulation(PyObject *self, PyObject *args);

/*
 * Process activity state outputs and apply them to simulation state values
 */
static void processActivityStateOutputs(SimulationObject *self,
                                        int activityIndex, double *statevalues,
                                        double *manipulationValuesBuffer);

/*
 * Find the index of a state variable by name
 */
static int findStateIndex(SimulationObject *self, const char *stateName);

// Simulations method
void model(void *simData, double time_local, double *statevalues,
           double *derivativevalues, double *RESvector, double *featurevector,
           int DOflag, int timeindex, double *eventvector, int *eventstatus);

static int Simulation_outputOwner(SimulationObject *self, int output);

static int Simulation_inputOwner(SimulationObject *self, int input);

static int Simulation_determineExOrder(SimulationObject *self, int modIndex,
                                       int *modStat);

static int Simulation_compare(const void *p, const void *q);

static int Simulation_CheckSharedVariables(SimulationObject *self);

static void Simulation_updateSimulationData(SimulationObject *self,
                                            SUNDIALS_SimData *simdata,
                                            bool skipFeaturevalues);

static int Simulation_InitSimulation(SimulationObject *self);

static double Simulation_lookupTimeScale(const char *timeunit,
                                         TimeScale *table);

static const char *Simulation_lookupTimeUnit(double scale, TimeScale *table);

static int Simulation_updateModelActivityScale(SimulationObject *self);

void Simulation_updateDerivativeTimeScale(SimulationObject *self,
                                          double conversionFactor);

static int Simulation_CheckActivities(PyObject *activities);

static int Simulation_CheckModels(PyObject *models);

static int Simulation_SetAttributeNames(SimulationObject *self);

static void Simulation_idVectorAlgebraicEqs(SimulationObject *self);

bool parseKeywords(PyObject *&ptr, std::vector<PyObject *> keys,
                   std::string keywordString);

bool parseAndSetTimevector(SimulationObject *self, PyObject *key1,
                           PyObject *key2, PyObject *key3,
                           bool augmentTimeVector, bool constructor);

bool parseAndSetTimeunit(SimulationObject *self, PyObject *key1, PyObject *key2,
                         PyObject *key3);

bool parseAndSetStateValues(SimulationObject *self, PyObject *key1,
                            PyObject *key2);

bool parseAndSetDerivativeValues(SimulationObject *self, PyObject *key1,
                                 PyObject *key2);

bool parseAndSetStateDerivativeAndResetValues(
    SimulationObject *self, PyObject *stateKey1, PyObject *stateKey2,
    PyObject *derivativeKey1, PyObject *derivativeKey2, PyObject *resetKey1,
    PyObject *resetKey2);

bool parseAndSetParameterValues(SimulationObject *self, PyObject *key1,
                                PyObject *key2, PyObject *key3);

namespace SIMULATION {
/*
======================================================================================
SETTERS AND GETTERS
======================================================================================
*/

// GETTERS

PyObject *getDerivativeValues(SimulationObject *self);

PyObject *getEventNames(SimulationObject *self);

PyObject *getEventStatus(SimulationObject *self);

PyObject *getEventTimes(SimulationObject *self);

PyObject *getFeatureDataDeprecated(SimulationObject *self); // Deprecated
PyObject *getFeatureValues(SimulationObject *self);

PyObject *getFeatureNames(SimulationObject *self);

PyObject *getFeatureUnits(SimulationObject *self);

PyObject *getParameterNames(SimulationObject *self);

PyObject *getParameterValues(SimulationObject *self);

PyObject *getInputNames(SimulationObject *self);

PyObject *getOutputNames(SimulationObject *self);

PyObject *getStateNames(SimulationObject *self);

PyObject *getStateValues(SimulationObject *self);

PyObject *getTimeUnit(SimulationObject *self);

PyObject *getTimeVector(SimulationObject *self);

// SETTERS

int setDerivativeValues(SimulationObject *self, PyObject *derivativeValues);

int setParameterValues(SimulationObject *self, PyObject *parameterValues);

int setStateValues(SimulationObject *self, PyObject *stateValues);

int setTimeUnit(SimulationObject *self, PyObject *timeUnit);

int setTimeVector(SimulationObject *self, PyObject *timevector,
                  bool augmentTimeVector);

/*
======================================================================================
PyMethods
======================================================================================
*/

PyObject *deepcopy(PyObject *self);

PyObject *differentialStates(SimulationObject *self);

PyObject *executionOrder(SimulationObject *self);

PyObject *features_To_Dict(SimulationObject *self);
PyObject *features_To_Dict_Deprecated(SimulationObject *self); // Deprecated

PyObject *getOptions(SimulationObject *self);

PyObject *hasAlgebraicEquations(SimulationObject *self);

PyObject *reduce(SimulationObject *self);

PyObject *resetStates(SimulationObject *self);

PyObject *resetParameters(SimulationObject *self);

PyObject *setOptions(SimulationObject *self, PyObject *args);

PyObject *setState(SimulationObject *self, PyObject *statetuple);

PyObject *simulate(SimulationObject *self, PyObject *args, PyObject *kwds);

PyObject *validateSimulation(SimulationObject *self, PyObject *args,
                             PyObject *kwds);
} // namespace SIMULATION

static double getTimeScale(SimulationObject *self, PyObject *value);

static PyGetSetDef Simulation_getsetters[] = {
    {"derivative_values", (getter)SIMULATION::getDerivativeValues,
     (setter)SIMULATION::setDerivativeValues, "Simulation derivative values",
     NULL},
    {"event_names", (getter)SIMULATION::getEventNames, NULL,
     "Simulation event names", NULL},
    {"event_status", (getter)SIMULATION::getEventStatus, NULL,
     "Simulation events' status flag", NULL},
    {"event_times", (getter)SIMULATION::getEventTimes, NULL,
     "Simulation event times", NULL},
    // Deprecated
    {"feature_data", (getter)SIMULATION::getFeatureDataDeprecated, NULL,
     "DEPRECATED: use 'feature_values' instead.", NULL},
    {"feature_values", (getter)SIMULATION::getFeatureValues, NULL,
     "Simulation feature values", NULL},
    {"feature_names", (getter)SIMULATION::getFeatureNames, NULL,
     "Simulation feature names", NULL},
    {"feature_units", (getter)SIMULATION::getFeatureUnits, NULL,
     "Simulation feature units", NULL},
    {"parameter_names", (getter)SIMULATION::getParameterNames, NULL,
     "Simulation parameter names", NULL},
    {"parameter_values", (getter)SIMULATION::getParameterValues,
     (setter)SIMULATION::setParameterValues, "Simulation parameter values",
     NULL},
    {"input_names", (getter)SIMULATION::getInputNames, NULL,
     "Simulation input names", NULL},
    {"output_names", (getter)SIMULATION::getOutputNames, NULL,
     "Simulation output names", NULL},
    {"state_names", (getter)SIMULATION::getStateNames, NULL,
     "Simulation state names", NULL},
    {"state_values", (getter)SIMULATION::getStateValues,
     (setter)SIMULATION::setStateValues, "Simulation state values", NULL},
    {"time_unit", (getter)SIMULATION::getTimeUnit,
     (setter)SIMULATION::setTimeUnit, "Simulation time unit", NULL},
    {"time_vector", (getter)SIMULATION::getTimeVector,
     (setter)SIMULATION::setTimeVector, "Simulation time vector", NULL},
    {NULL} /* Sentinel */
};

static PyMethodDef Simulation_methods[] = {
    {"__deepcopy__", (PyCFunction)SIMULATION::deepcopy, METH_VARARGS},
    {"__reduce__", (PyCFunction)SIMULATION::reduce, METH_NOARGS,
     "__reduce__ function"},
    {"__setstate__", (PyCFunction)SIMULATION::setState, METH_VARARGS,
     "__setstate__ function"},
    {"differential_states", (PyCFunction)SIMULATION::differentialStates,
     METH_NOARGS,
     "Return an array of boolean, holds the value True if respective state is "
     "a differential state"},
    {"execution_order", (PyCFunction)SIMULATION::executionOrder, METH_NOARGS,
     "Write out the execution order"},
    // Deprecated
    {"feature_data_as_dict",
     (PyCFunction)SIMULATION::features_To_Dict_Deprecated, METH_NOARGS,
     "Present the feature values under a dictionary form"},
    {"features_as_dict", (PyCFunction)SIMULATION::features_To_Dict, METH_NOARGS,
     "Present the feature values under a dictionary form"},
    {"get_options", (PyCFunction)SIMULATION::getOptions, METH_NOARGS,
     "Returns options and their values"},
    {"has_algebraic_equations", (PyCFunction)SIMULATION::hasAlgebraicEquations,
     METH_NOARGS, "Check if simulation contains algebraic equations"},
    {"reset_parameters", (PyCFunction)SIMULATION::resetParameters, METH_NOARGS,
     "Reset simulation parameter values"},
    {"reset_states", (PyCFunction)SIMULATION::resetStates, METH_NOARGS,
     "Reset simulation state and derivative values"},
    {"set_options", (PyCFunction)SIMULATION::setOptions, METH_O, "Set options"},
    {"simulate", (PyCFunction)SIMULATION::simulate,
     METH_VARARGS | METH_KEYWORDS, "Simulate simulation object"},
    {"validate", (PyCFunction)SIMULATION::validateSimulation,
     METH_VARARGS | METH_KEYWORDS, "Validate simulation object"},
    {NULL} /* Sentinel */
};

static PyMethodDef _SimulationMethods[] = {
    {"_reconstruct_simulation", (PyCFunction)_reconstruct_simulation,
     METH_VARARGS,
     "Internal function for serialization reconstruction with keyword "
     "arguments"},
    {"disable_debug", (PyCFunction)debug::disableDebug, METH_NOARGS,
     "disable debug mode"},
    {"enable_debug", (PyCFunction)debug::enableDebug, METH_NOARGS,
     "enable debug mode"},
    {"is_debug", (PyCFunction)debug::isDebug, METH_NOARGS,
     "Returns true if debug mode is active"},
    {NULL}};

static PyModuleDef Simulation = {.m_base = PyModuleDef_HEAD_INIT,
                                 .m_name = "sund._Simulation",
                                 .m_doc = "Python interface to Simulation.",
                                 .m_size = -1,
                                 .m_methods = _SimulationMethods};

extern int IDA55(void *simObject, int nrtimes, double *timevector, int nrstates,
                 double *statevalues, double *derivativevalues,
                 double *idvector, int nrevents, double **eventtimes,
                 int **eventstatus, int *nreventshappened, PyObject *optionsPY);
static void Simulation_initModel(SimulationObject *self, SimulationModel *mod);
static void Simulation_initActivity(SimulationObject *self,
                                    SimulationActivity *act);

/* Function to_dict */
PyObject *Simulation_Features_To_Dict(SimulationObject *self);

#endif
