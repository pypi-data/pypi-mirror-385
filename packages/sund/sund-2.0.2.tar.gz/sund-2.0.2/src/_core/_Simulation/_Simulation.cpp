#define _SIMULATION_C

#include "_Simulation.h"
#include "Activity_API.h"
#include "Models_C_API.h"
#include "_StringList_C_API.h"
#include "debug.h"
#include "pyarraymacros.h"
#include "sund_sundials_interface.h"
#include "timescales.h"

// Undefine the macro to avoid conflicts, then redefine it for 2-parameter calls
#ifdef debugPrint
#undef debugPrint
#endif

// Redefine debugPrint to automatically add "_Simulation" as first parameter
#define debugPrint(function, message)                                          \
  do {                                                                         \
    if (debug::DEBUG)                                                          \
      debug::debugPrint("_Simulation", function, message);                     \
  } while (0)

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#define NPY_NO_DEPRECATED_API NPY_2_3_API_VERSION
#include <numpy/arrayobject.h>

#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <iterator>
#include <limits>
#include <set>
#include <string>
#include <unordered_map>
#include <vector>

#define SIMULATION_STATE 0
#define SIMULATION_FEATURE 1
#define SIMULATION_OUTPUT 2
#define SIMULATION_INPUT 3
#define SIMULATION_EVENT 4
#define SIMULATION_PARAMETER 5
#define SIMULATION_MODEL 6
#define SIMULATION_ACTIVITY 7

static double default_0_input = 0.0;

using namespace SIMULATION;

/*
========================================================================================================================
Global state tracking variables
========================================================================================================================
*/

// Global state tracking map and reset flag - used for activity state
// manipulations This allows us to track state transitions and apply them only
// when necessary
static std::unordered_map<int, std::vector<double>> g_lastStateValues;
static bool g_resetStateTracking = true;

/*
========================================================================================================================
Helper functions
========================================================================================================================
*/

/*
 * Check if event conditions are true before simulation and apply appropriate
 * events
 */
void applyInitialEvents(SimulationObject *self) {
  // Initialize activity outputs
  for (int i{}; i < self->numberof[SIMULATION_ACTIVITY]; i++) {
    SimulationActivity *act = &self->activities[i];
    // Compute outputs only
    int nOutputs = nrOutputs(act->activityObject);
    std::vector<double> tmpOutputs(nOutputs);
    outputFeature(act->activityObject, act->scale * PYDATA(self->timevector)[0],
                  tmpOutputs.data(), nullptr, 0);
    // Copy outputs into the simulation buffer (manipulations are applied
    // separately)
    if (nOutputs > 0) {
      std::memcpy(&self->outputbuffer[act->offset[ACTIVITY_OUTPUT]],
                  tmpOutputs.data(), nOutputs * sizeof(double));
    }
  }

  for (int i{}; i < self->numberof[SIMULATION_MODEL]; i++) {
    SimulationModel *mod{&self->models[i]};
    const int numberOfEvents = Model_numberof(mod->modelObject)[MODEL_EVENT];
    if (numberOfEvents > 0) {
      std::vector<double> events{};
      events.resize(numberOfEvents);

      mod->function(
          mod->scale * PYDATA(self->timevector)[0], mod->scale,
          &PYDATA(self->statevalues)[mod->offset[MODEL_STATE]], nullptr,
          nullptr, &PYDATA(self->parametervalues)[mod->offset[MODEL_PARAMETER]],
          nullptr, nullptr, &self->inputptr[mod->offset[MODEL_INPUT]],
          events.data(), nullptr, DOFLAG_EVENT);

      std::vector<int> eventstatus{};
      eventstatus.resize(numberOfEvents);
      for (int j{}; j < numberOfEvents; j++) {
        if (events[j] + 0.5) {
          eventstatus[j] = 1;
        }
      }
      mod->function(
          mod->scale * PYDATA(self->timevector)[0], mod->scale,
          &PYDATA(self->statevalues)[mod->offset[MODEL_STATE]], nullptr,
          nullptr, &PYDATA(self->parametervalues)[mod->offset[MODEL_PARAMETER]],
          nullptr, nullptr, &self->inputptr[mod->offset[MODEL_INPUT]], nullptr,
          eventstatus.data(), DOFLAG_EVENTASSIGN);
    }
  }

  return;
}

/*
 * Process activity state manipulations and apply them to simulation state
 * values This function should only set states when there are actual state
 * transitions, not continuously override the integrated values.
 */

/*
 * Reset activity state tracking - called at the beginning of each simulation
 */
static void resetActivityStateTracking() { g_resetStateTracking = true; }

static void processActivityStateOutputs(SimulationObject *self,
                                        int activityIndex, double *statevalues,
                                        double *activityManipulations) {
  // Clear all state tracking if reset was requested
  if (g_resetStateTracking) {
    g_lastStateValues.clear();
    g_resetStateTracking = false;
  }

  PyObject *activityManipulationNames =
      manipulationNames(self->activities[activityIndex].activityObject);
  int activityNrManipulations = PyList_Size(activityManipulationNames);
  int totalManipulations = activityNrManipulations; // tracking per-manipulation

  // Initialize last state values if not exist
  if (g_lastStateValues.find(activityIndex) == g_lastStateValues.end()) {
    g_lastStateValues[activityIndex].resize(totalManipulations,
                                            NAN); // Use NaN to detect first run
  }

  // Process state manipulations
  for (int i = 0; i < activityNrManipulations; i++) {
    PyObject *manipulationName = PyList_GetItem(activityManipulationNames, i);
    const char *stateName = PyUnicode_AsUTF8(manipulationName);

    // Find the corresponding state index in the simulation
    int stateIndex = findStateIndex(self, stateName);
    if (stateIndex >= 0) {
      double currentActivityValue = activityManipulations[i];

      // Skip processing entirely if current value is the "no assignment" marker
      if (isnan(currentActivityValue)) {
        // Don't update tracking values for nan - preserve last valid
        // manipulation
        continue;
      }

      // Get the manipulation mode for this state using the C API function
      // pointer (needed for decision logic)
      typedef int (*getManipulationMode_t)(PyObject *, const char *);
      getManipulationMode_t getManipulationMode_func =
          (getManipulationMode_t)Activity_API[getManipulationMode_NUM];
      int manipulationMode = getManipulationMode_func(
          self->activities[activityIndex].activityObject, stateName);

      // Apply state manipulation when we have a valid (non-nan) value
      bool shouldApplyState = false;

      if (isnan(g_lastStateValues[activityIndex][i])) {
        // First time seeing a valid (non-marker) value - apply it
        shouldApplyState = true;
      } else if (std::abs(g_lastStateValues[activityIndex][i] -
                          currentActivityValue) > 1e-12) {
        // Value has changed from last valid manipulation - apply new value
        shouldApplyState = true;
      } else if (manipulationMode == 0 &&
                 std::abs(statevalues[stateIndex] - currentActivityValue) >
                     1e-12) {
        // 'set' mode: value identical to last applied, but the underlying state
        // has drifted due to ODE integration. Re-apply to enforce the intended
        // piecewise assignment (e.g., same value at a later time point).
        shouldApplyState = true;
      }

      if (shouldApplyState) {
        if (manipulationMode == 0) {
          // Set mode: replace the state value
          statevalues[stateIndex] = currentActivityValue;
        } else if (manipulationMode == 1) {
          // Add mode: add to the current state value
          statevalues[stateIndex] += currentActivityValue;
        } else {
          // Fallback: treat as set mode if mode is not found or invalid
          statevalues[stateIndex] = currentActivityValue;
        }

        // Only update tracking value when we actually applied a valid
        // manipulation
        g_lastStateValues[activityIndex][i] = currentActivityValue;
      }
    }
  }
}

/*
 * Find the index of a state variable by name
 */
static int findStateIndex(SimulationObject *self, const char *stateName) {
  for (int i = 0; i < self->numberof[SIMULATION_STATE]; i++) {
    PyObject *stateNameObj = PyList_GetItem(self->statenames, i);
    const char *existingStateName = PyUnicode_AsUTF8(stateNameObj);

    // Handle compartment prefixes in state names
    if (strcmp(existingStateName, stateName) == 0) {
      return i;
    }

    // Also check if state name contains compartment prefix
    const char *colonPos = strchr(stateName, ':');
    if (colonPos != NULL) {
      // If stateName has compartment prefix, compare the full name
      if (strcmp(existingStateName, stateName) == 0) {
        return i;
      }
    } else {
      // If stateName doesn't have compartment prefix, check if existing name
      // ends with it
      const char *existingColonPos = strchr(existingStateName, ':');
      if (existingColonPos != NULL) {
        // Compare just the part after the colon
        if (strcmp(existingColonPos + 1, stateName) == 0) {
          return i;
        }
      }
    }
  }

  return -1; // State not found
}

// Simulations method
void model(void *simData, double time_local, double *statevalues,
           double *derivativevalues, double *RESvector, double *featurevector,
           int DOflag, int timeindex, double *eventvector, int *eventstatus) {
  SimulationObject *self;
  SimulationModel *mod;
  SimulationActivity *act;
  self = (SimulationObject *)simData;
  int k, *offset;
  double *parametervalues;
  parametervalues = PYDATA(self->parametervalues);

  // Activities
  for (k = 0; k < self->numberof[SIMULATION_ACTIVITY]; k++) {
    act = &self->activities[k];
    offset = act->offset;
    int nOutputs = nrOutputs(act->activityObject);
    std::vector<double> tmpOutputs(nOutputs);
    outputFeature(act->activityObject, A_SCALE * time_local, tmpOutputs.data(),
                  A_FEATUREVECTOR, DOflag);
    // Copy outputs into the simulation buffer
    if (nOutputs > 0) {
      std::memcpy(A_OUTPUTVECTOR, tmpOutputs.data(), nOutputs * sizeof(double));
    }

    // Process state manipulations for this activity, but NOT during derivative
    // calculations
    if (DOflag != DOFLAG_DDT) {
      int nManip = PyList_Size(manipulationNames(act->activityObject));
      if (nManip > 0) {
        std::vector<double> tmpManip(nManip);
        manipulationValues(act->activityObject, A_SCALE * time_local,
                           tmpManip.data());
        processActivityStateOutputs(self, k, statevalues, tmpManip.data());
      }
    }
  }

  // Models
  // Update outputs
  for (k = 0; k < self->numberof[SIMULATION_MODEL]; k++) {
    mod = &self->models[k];
    offset = mod->offset;
    if (HASOUTPUT)
      MODELFUNCTION(SCALE * time_local, SCALE, STATEVECTOR, DERIVATEVECTOR,
                    NULL, PARAMETERVECTOR, NULL, OUTPUTVECTOR, INPUTVECTOR,
                    NULL, NULL, DOFLAG_OUTPUT);
  }
  // do what is ask for
  for (k = 0; k < self->numberof[SIMULATION_MODEL]; k++) {
    mod = &self->models[k];
    offset = mod->offset;
    MODELFUNCTION(SCALE * time_local, SCALE, STATEVECTOR, DERIVATEVECTOR,
                  RESIDUALVECTOR, PARAMETERVECTOR, FEATUREVECTOR, OUTPUTVECTOR,
                  INPUTVECTOR, EVENTVECTOR, EVENTSTATUS, DOflag);
  }
}

static int Simulation_outputOwner(SimulationObject *self, int output) {
  int k;
  if (output < 0) // default input
    return -1;
  for (k = 0; k < self->numberof[SIMULATION_MODEL]; k++) {
    if (output <
            self->models[k].offset[MODEL_OUTPUT] +
                Model_numberof(self->models[k].modelObject)[MODEL_OUTPUT] &&
        output >= self->models[k].offset[MODEL_OUTPUT])
      return k;
  }
  return -2; // activity output
}

static int Simulation_inputOwner(SimulationObject *self, int input) {
  int k;
  for (k = 0; k < self->numberof[SIMULATION_MODEL]; k++) {
    if (input < self->models[k].offset[MODEL_INPUT] +
                    Model_numberof(self->models[k].modelObject)[MODEL_INPUT] &&
        input >= self->models[k].offset[MODEL_INPUT])
      return k;
  }
  return -1; // unknown input
}

static int Simulation_determineExOrder(SimulationObject *self, int modIndex,
                                       int *modStat) {
  SimulationModel *model;
  const int *inDep;
  int tmp, k, maxExOrd, output;

  if (modIndex < 0) // default_input = -1 or activity = -2
    return 0;

  model = &self->models[modIndex];
  if (modStat[modIndex] == -1) // model execution order is being calculated
    return -1;                 // fail
  else if (modStat[modIndex] ==
           1) // model execution order has already being calculated
    return model->exOrder;
  else
    modStat[modIndex] = -1;

  // no input dependency
  inDep = Model_inputDependency(model->modelObject);
  if (inDep[0] == 0) {
    model->exOrder = 0;
    modStat[modIndex] = 1;
    return model->exOrder;
  }

  // go through input dependencies
  maxExOrd = -1;
  for (k = 1; k <= inDep[0]; k++) {
    output = self->inputmap[model->offset[MODEL_INPUT] + inDep[k]];
    tmp = Simulation_determineExOrder(
        self, Simulation_outputOwner(self, output), modStat);
    if (tmp < 0) { // fail
      return -1;
    }
    if (tmp > maxExOrd)
      maxExOrd = tmp;
  }

  model->exOrder = maxExOrd + 1;
  modStat[modIndex] = 1;
  return model->exOrder;
}

static int Simulation_compare(const void *p, const void *q) {
  const SimulationModel *x, *y;
  x = (const SimulationModel *)p;
  y = (const SimulationModel *)q;

  if (x->exOrder < y->exOrder)
    return -1;
  else if (x->exOrder > y->exOrder)
    return 1;
  return 0;
}

static int Simulation_CheckSharedVariables(SimulationObject *self) {
  PyObject *indexFunc, *ret, *tmp;
  SimulationModel *inputowner;
  int k, *modStat, mandatory;

  self->sharedvariablescheck = 0;

  indexFunc = PyUnicode_FromString("index");
  for (k = 0; k < self->numberof[SIMULATION_INPUT]; k++) {
    tmp = PyList_GetItem(self->inputnames, k);
    ret = PyObject_CallMethodObjArgs((PyObject *)self->outputnames, indexFunc,
                                     tmp, NULL);
    if (PyErr_Occurred()) { // not in list
      inputowner = &self->models[Simulation_inputOwner(self, k)];
      // check if input is mandatory
      mandatory = Model_mandatoryInputs(inputowner->modelObject)
          [k -
           inputowner->offset[MODEL_INPUT]]; // 0 mandatory, 1 non-mandatory, 2
                                             // non-mandatory - default value 0
      ModelObject *model{(ModelObject *)inputowner->modelObject};
      std::vector<double> defaultValues{model->model->defaultInputs};
      if (mandatory == 0) {
        PyErr_SetObject(
            PyExc_ValueError,
            PyUnicode_FromFormat("Model '%S' is missing mandatory input '%S' "
                                 "which is not among the shared variables",
                                 Model_name(inputowner->modelObject), tmp));
        Py_DECREF(indexFunc);
        return -1;
      } else if (mandatory == 1) { // non-mandatory
        self->inputmap[k] = -1;
        self->defaultInputValues[k] =
            defaultValues[k - inputowner->offset[MODEL_INPUT]];
        self->inputptr[k] = &self->defaultInputValues[k];
      } else { // non-mandatory - default value 0
        self->inputmap[k] = -1;
        self->inputptr[k] = &default_0_input; // default 0 input value used
      }
      PyErr_Clear();
    } else {
      self->inputmap[k] = PyLong_AsLong(ret); // map output index to input
      self->inputptr[k] = &self->outputbuffer[self->inputmap[k]];
    }
  }
  Py_DECREF(indexFunc);

  modStat = static_cast<int *>(PyMem_Calloc(
      self->numberof[SIMULATION_MODEL],
      sizeof(int))); // model status: -1 execution order is being calculated,
                     //  0 no action taken, 1 execution order calculated
  for (k = 0; k < self->numberof[SIMULATION_MODEL]; k++) {
    if (modStat[k] == 0) {
      if (Simulation_determineExOrder(self, k, modStat) < 0) {
        PyMem_Free(modStat);
        PyErr_SetObject(PyExc_ValueError,
                        PyUnicode_FromFormat(
                            "Cannot resolve execution dependency for model %S",
                            Model_name(self->models[k].modelObject)));
        return -2;
      }
    } else if (modStat[k] == -1) {
      printf("%s\n", "Something went wrong...");
    }
  }
  self->sharedvariablescheck = 1;
  PyMem_Free(modStat);

  // sort models
  qsort((void *)self->models, self->numberof[SIMULATION_MODEL],
        sizeof(SimulationModel), Simulation_compare);

  return 1;
}

static void Simulation_updateSimulationData(SimulationObject *self,
                                            SUNDIALS_SimData *simdata,
                                            bool skipFeaturevalues = false) {
  npy_intp dims[2]; //, *currentDims;
  PyObject *tmp;

  dims[0] = simdata->nreventstriggered;
  dims[1] = self->numberof[SIMULATION_EVENT];

  // eventtimedata
  tmp = self->eventtimedata;
  self->eventtimedata = PyArray_SimpleNewFromData(
      1, dims, NPY_DOUBLE, (void *)simdata->eventtimedata);
  PyArray_ENABLEFLAGS((PyArrayObject *)self->eventtimedata, NPY_ARRAY_OWNDATA);
  Py_DECREF(tmp);

  // eventstatusdata
  tmp = self->eventstatusdata;
  self->eventstatusdata = PyArray_SimpleNewFromData(
      2, dims, NPY_BOOL, (void *)simdata->eventstatusdata);
  PyArray_ENABLEFLAGS((PyArrayObject *)self->eventstatusdata,
                      NPY_ARRAY_OWNDATA);
  Py_DECREF(tmp);

  // featurevalues
  if (!skipFeaturevalues) {
    dims[0] = PYSIZE(self->timevector);
    dims[1] = self->numberof[SIMULATION_FEATURE];
    self->featurevalues = PyArray_SimpleNewFromData(
        2, dims, NPY_DOUBLE, (void *)simdata->featurevalues);
    PyArray_ENABLEFLAGS((PyArrayObject *)self->featurevalues,
                        NPY_ARRAY_OWNDATA);
  }
}

static int Simulation_InitSimulation(SimulationObject *self) {
  // check shared variables
  if (!self->sharedvariablescheck) {
    if (Simulation_CheckSharedVariables(self) <=
        0) { // -1 = missing mandatory input, 0 = dependency error
      return -1;
    }
  }
  // check timevector
  if (PYSIZE(self->timevector) <= 1) {
    PyErr_SetString(PyExc_ValueError,
                    "Not enough time points given. At least two time points "
                    "are required to run a simulation.");
    return -1;
  }

  return 0;
}

static double Simulation_lookupTimeScale(const char *timeunit,
                                         TimeScale *table) {
  while (table->name) {
    if (!strcmp(table->name, timeunit))
      return table->scale;
    table++;
  }
  return 0;
}

static const char *Simulation_lookupTimeUnit(double scale, TimeScale *table) {
  while (table->name) {
    if (table->scale == scale)
      return table->name;
    table++;
  }
  return NULL;
}

static int Simulation_updateModelActivityScale(SimulationObject *self) {
  double scale;

  // models
  for (int i{}; i < self->numberof[SIMULATION_MODEL]; i++) {
    scale = Simulation_lookupTimeScale(
        PyUnicode_AsUTF8(Model_timeUnit(self->models[i].modelObject)),
        timeScaleData);
    if (scale == 0) {
      PyErr_SetObject(
          PyExc_ValueError,
          PyUnicode_FromFormat("Incorrect time unit '%S' given in model '%S'.",
                               Model_timeUnit(self->models[i].modelObject),
                               Model_name(self->models[i].modelObject)));
      return -1;
    }
    self->models[i].scale = self->scale / scale;
  }
  // activities
  for (int i{}; i < self->numberof[SIMULATION_ACTIVITY]; i++) {
    scale = Simulation_lookupTimeScale(
        PyUnicode_AsUTF8(timeUnit_API(self->activities[i].activityObject)),
        timeScaleData);
    if (scale == 0) {
      PyErr_SetObject(
          PyExc_ValueError,
          PyUnicode_FromFormat("Incorrect time unit '%S' in activity nr. %d.",
                               timeUnit_API(self->activities[i].activityObject),
                               i + 1));
      return -1;
    }
    self->activities[i].scale = self->scale / scale;
  }
  return 0;
}

void Simulation_updateDerivativeTimeScale(SimulationObject *self,
                                          double conversionFactor) {
  double *derivativeValues{PYDATA(self->derivativevalues)};
  for (int i{}; i < self->numberof[SIMULATION_STATE]; i++) {
    derivativeValues[i] *= conversionFactor;
  }

  return;
}

static int Simulation_CheckActivities(PyObject *activities) {
  if (isActivity(activities))
    return 1;
  if (!PyList_Check(activities))
    return -1;
  for (int i{}; i < Py_SIZE(activities); i++) {
    if (!isActivity(PyList_GetItem(activities, i)))
      return -1;
  }
  return Py_SIZE(activities);
}

static int Simulation_CheckModels(PyObject *models) {
  int k;
  if (Model_isModel(models))
    return 1;
  if (!PyList_Check(models))
    return -1;
  for (k = 0; k < Py_SIZE(models); k++) {
    if (!Model_isModel(PyList_GetItem(models, k)))
      return -1;
  }
  return Py_SIZE(models);
}

static int Simulation_SetAttributeNames(SimulationObject *self) {
  SimulationModel *mod;
  SimulationActivity *act;
  PyObject *obj;
  int k, tmp;
  const int *numberof;
  // Models
  for (k = 0; k < self->numberof[SIMULATION_MODEL]; k++) {
    mod = &self->models[k];
    obj = mod->modelObject;
    numberof = Model_numberof(obj);
    // featurenames
    if (PyList_SetSlice(self->featurenames, mod->offset[MODEL_FEATURE],
                        mod->offset[MODEL_FEATURE] + numberof[MODEL_FEATURE],
                        Model_featureNames(obj)) < 0)
      return -1;
    // featureunits
    if (PyList_SetSlice(self->featureunits, mod->offset[MODEL_FEATURE],
                        mod->offset[MODEL_FEATURE] + numberof[MODEL_FEATURE],
                        Model_featureUnits(obj)) < 0)
      return -1;
    // outputnames
    if (PyList_SetSlice(self->outputnames, mod->offset[MODEL_OUTPUT],
                        mod->offset[MODEL_OUTPUT] + numberof[MODEL_OUTPUT],
                        Model_outputNames(obj)) < 0)
      return -1;
    // inputnames
    if (PyList_SetSlice(self->inputnames, mod->offset[MODEL_INPUT],
                        mod->offset[MODEL_INPUT] + numberof[MODEL_INPUT],
                        Model_inputNames(obj)) < 0)
      return -1;
    // parameternames
    if (PyList_SetSlice(self->parameternames, mod->offset[MODEL_PARAMETER],
                        mod->offset[MODEL_PARAMETER] +
                            numberof[MODEL_PARAMETER],
                        Model_parameterNames(obj)) < 0)
      return -1;
    // statenames
    if (PyList_SetSlice(self->statenames, mod->offset[MODEL_STATE],
                        mod->offset[MODEL_STATE] + numberof[MODEL_STATE],
                        Model_stateNames(obj)) < 0)
      return -1;
    // eventnames
    if (PyList_SetSlice(self->eventnames, mod->offset[MODEL_EVENT],
                        mod->offset[MODEL_EVENT] + numberof[MODEL_EVENT],
                        Model_eventNames(obj)) < 0)
      return -1;
  }
  // Activities
  for (k = 0; k < self->numberof[SIMULATION_ACTIVITY]; k++) {
    act = &self->activities[k];
    obj = act->activityObject;
    tmp = nrFeatures(obj);
    if (PyList_SetSlice(self->featurenames, act->offset[ACTIVITY_FEATURE],
                        act->offset[ACTIVITY_FEATURE] + tmp,
                        featureNames(obj)) < 0)
      return -1;
    if (PyList_SetSlice(self->featureunits, act->offset[ACTIVITY_FEATURE],
                        act->offset[ACTIVITY_FEATURE] + tmp,
                        featureUnits(obj)) < 0)
      return -1;
    // Set activity output names
    if (PyList_SetSlice(self->outputnames, act->offset[ACTIVITY_OUTPUT],
                        act->offset[ACTIVITY_OUTPUT] + nrOutputs(obj),
                        outputNames(obj)) < 0)
      return -1;
  }
  return 0;
}

static void Simulation_idVectorAlgebraicEqs(SimulationObject *self) {
  SimulationModel *mod;
  int k;
  const int *numberof;

  for (k = 0; k < self->numberof[SIMULATION_MODEL]; k++) {
    mod = &self->models[k];
    numberof = Model_numberof(mod->modelObject);
    memcpy(PYDATA(self->idvector) + mod->offset[MODEL_STATE],
           PYDATA(Model_idVector(mod->modelObject)),
           numberof[MODEL_STATE] * sizeof(double));
    // has algebraic states
    if (Model_hasAlgebraicEq(mod->modelObject))
      self->has_algebraic_eq = 1;
  }
}

bool parseKeywords(PyObject *&ptr, std::vector<PyObject *> keys,
                   std::string keywordString) {
  for (PyObject *key : keys) {
    if (key != nullptr) {
      if (ptr != nullptr) {
        PyErr_Format(
            PyExc_SyntaxError,
            "Only one attribute key can be used simultaneously! Use either %s!",
            keywordString.c_str());
        return false;
      }

      ptr = key;
    }
  }

  return true;
}

bool parseAndSetTimevector(SimulationObject *self, PyObject *key1,
                           PyObject *key2, PyObject *key3,
                           bool augmentTimeVector = true,
                           bool constructor = false) {
  PyObject *timeVector{};
  if (!parseKeywords(timeVector, {key1, key2, key3},
                     "'time_vector', 'time' or 't'")) {
    return false;
  }

  if (timeVector != nullptr) {
    if (setTimeVector(self, timeVector, augmentTimeVector) < 0) {
      return false;
    }
  } else if (self->timevector == NULL) {
    if (!constructor) {
      PyErr_SetString(
          PyExc_AttributeError,
          "The 'time_vector' attribute has not been previously set! Set it "
          "before calling this function or include it in the function call.");
      return false;
    }
  }

  return true;
}

bool parseAndSetTimeunit(SimulationObject *self, PyObject *key1,
                         PyObject *key2) {
  PyObject *timeUnit{};
  if (!parseKeywords(timeUnit, {key1, key2}, "'time_unit' or 'tu'")) {
    return false;
  }

  if (timeUnit != nullptr) {
    if (setTimeUnit(self, timeUnit) < 0) {
      return false;
    }
  }

  return true;
}

bool parseAndSetStateValues(SimulationObject *self, PyObject *key1,
                            PyObject *key2) {
  PyObject *stateValues{};

  if (!parseKeywords(stateValues, {key1, key2}, "'state_values' or 'x0'")) {
    return false;
  }

  if (stateValues != nullptr) {
    if (setStateValues(self, stateValues) < 0) {
      return false;
    }
  }

  return true;
}

bool parseAndSetDerivativeValues(SimulationObject *self, PyObject *key1,
                                 PyObject *key2) {
  PyObject *derivativeValues{};

  if (!parseKeywords(derivativeValues, {key1, key2},
                     "'derivative_values' or 'xdot'")) {
    return false;
  }

  if (derivativeValues != nullptr) {
    if (setDerivativeValues(self, derivativeValues) < 0) {
      return false;
    }
  }

  return true;
}

bool parseAndSetStateDerivativeAndResetValues(
    SimulationObject *self, PyObject *stateKey1, PyObject *stateKey2,
    PyObject *derivativeKey1, PyObject *derivativeKey2, PyObject *resetKey1) {
  PyObject *stateValues{};
  PyObject *derivativeValues{};
  PyObject *reset{};

  if (!parseKeywords(stateValues, {stateKey1, stateKey2},
                     "'state_values' or 'x0'")) {
    return false;
  }
  if (!parseKeywords(derivativeValues, {derivativeKey1, derivativeKey2},
                     "'derivative_values' or 'xdot'")) {
    return false;
  }
  if (!parseKeywords(reset, {resetKey1}, "'reset'")) {
    return false;
  }

  // Check for conflict
  if (reset != nullptr &&
      (stateValues != nullptr || derivativeValues != nullptr)) {
    PyErr_SetString(PyExc_SyntaxError,
                    "Argument 'reset' is incompatible with the 'state_values' "
                    "and 'derivative_values' arguments!");
    return false;
  }

  if (stateValues != nullptr) {
    if (setStateValues(self, stateValues) < 0) {
      return false;
    }
  }

  if (derivativeValues != nullptr) {
    if (setDerivativeValues(self, derivativeValues) < 0) {
      return false;
    }
  }

  // Give a default value to reset depending on if state or derivative values
  // were provided
  if (reset == nullptr) {
    if (stateValues != nullptr || derivativeValues != nullptr) {
      reset = Py_False;
    } else {
      reset = Py_True;
    }
  }

  if (reset != nullptr) {
    if (!PyBool_Check(reset)) {
      PyErr_SetString(PyExc_ValueError,
                      "Argument 'reset' must be a Boolean value!");
      return false;
    }
    if (reset == Py_True) {
      resetStates(self);
    }
  }

  return true;
}

bool parseAndSetParameterValues(SimulationObject *self, PyObject *key1,
                                PyObject *key2, PyObject *key3) {
  PyObject *parameterValues{};
  if (!parseKeywords(parameterValues, {key1, key2, key3},
                     "'parameter_values', 'theta' or 'p'")) {
    return false;
  }

  if (parameterValues != nullptr) {
    if (setParameterValues(self, parameterValues) < 0) {
      return false;
    }
  }

  return true;
}

/*
========================================================================================================================
SETTERS AND GETTERS
========================================================================================================================
*/

// GETTERS

PyObject *SIMULATION::getDerivativeValues(SimulationObject *self) {
  Py_INCREF(self->derivativevalues);
  return self->derivativevalues;
}

PyObject *SIMULATION::getEventNames(SimulationObject *self) {
  Py_INCREF(self->eventnames);
  return self->eventnames;
}

PyObject *SIMULATION::getEventStatus(SimulationObject *self) {
  Py_INCREF(self->eventstatusdata);
  return self->eventstatusdata;
}

PyObject *SIMULATION::getEventTimes(SimulationObject *self) {
  Py_INCREF(self->eventtimedata);
  return self->eventtimedata;
}

// Deprecated alias (kept for backward compatibility). Will be removed in a
// future major release.
PyObject *SIMULATION::getFeatureDataDeprecated(SimulationObject *self) {
  if (PyErr_WarnEx(
          PyExc_DeprecationWarning,
          "The 'feature_data' method is deprecated and will be removed in a "
          "future version. Use the 'feature_values' method instead!",
          1) < 0) {
    return NULL;
  }
  return getFeatureValues(self);
}

PyObject *SIMULATION::getFeatureValues(SimulationObject *self) {
  // Check if featurevalues is valid (not NULL)
  if (self->featurevalues == NULL) {
    Py_INCREF(Py_None);
    return Py_None;
  }

  Py_INCREF(self->featurevalues);
  return self->featurevalues;
}

PyObject *SIMULATION::getFeatureNames(SimulationObject *self) {
  Py_INCREF(self->featurenames);
  return self->featurenames;
}

PyObject *SIMULATION::getFeatureUnits(SimulationObject *self) {
  Py_INCREF(self->featureunits);
  return self->featureunits;
}

PyObject *SIMULATION::getParameterNames(SimulationObject *self) {
  Py_INCREF(self->parameternames);
  return self->parameternames;
}

PyObject *SIMULATION::getParameterValues(SimulationObject *self) {
  Py_INCREF(self->parametervalues);
  return self->parametervalues;
}

PyObject *SIMULATION::getInputNames(SimulationObject *self) {
  Py_INCREF(self->inputnames);
  return self->inputnames;
}

PyObject *SIMULATION::getOutputNames(SimulationObject *self) {
  Py_INCREF(self->outputnames);
  return self->outputnames;
}

PyObject *SIMULATION::getStateNames(SimulationObject *self) {
  Py_INCREF(self->statenames);
  return self->statenames;
}

PyObject *SIMULATION::getStateValues(SimulationObject *self) {
  Py_INCREF(self->statevalues);
  return self->statevalues;
}

PyObject *SIMULATION::getTimeUnit(SimulationObject *self) {
  const char *timeunit = Simulation_lookupTimeUnit(self->scale, timeScaleData);
  if (timeunit) {
    return PyUnicode_FromString(timeunit);
  } else {
    // Fallback: fuzzy match in case of tiny floating point discrepancies
    TimeScale *table = timeScaleData;
    while (table->name) {
      double target = table->scale;
      double diff = std::fabs(self->scale - target);
      double tol = std::numeric_limits<double>::epsilon() *
                   std::max(1.0, std::fabs(target));
      if (diff <= tol) {
        return PyUnicode_FromString(table->name);
      }
      table++;
    }
    return PyUnicode_FromString("Undefined-time-scale");
  }
}

PyObject *SIMULATION::getTimeVector(SimulationObject *self) {
  Py_INCREF(self->timevector);
  return self->timevector;
}

// SETTERS

int SIMULATION::setDerivativeValues(SimulationObject *self,
                                    PyObject *derivativeValues) {
  PyObject *valueArray = PyArray_FROM_OTF(
      derivativeValues, NPY_DOUBLE, NPY_ARRAY_DEFAULT | NPY_ARRAY_ENSURECOPY);
  if (!valueArray) {
    PyErr_SetString(PyExc_TypeError,
                    "The given value does not match the derivative_values "
                    "attribute type. Expected a 1D list or array of numbers.");
    Py_XDECREF(valueArray);
    return -1;
  }

  // Check number of elements
  int diff{self->numberof[SIMULATION_STATE] -
           static_cast<int>(PYSIZE(valueArray))};

  if (diff > 0) {
    PyErr_Format(PyExc_ValueError,
                 "Incorrect number of derivative values: %i too few values!",
                 diff);
    Py_XDECREF(valueArray);
    return -1;
  } else if (diff < 0) {
    PyErr_Format(PyExc_ValueError,
                 "Incorrect number of derivative values: %i too many values!",
                 -diff);
    Py_XDECREF(valueArray);
    return -1;
  }

  PyObject *tmp{self->derivativevalues};
  self->derivativevalues = valueArray;
  Py_DECREF(tmp);

  return 0;
}

PyObject *SIMULATION::setOptions(SimulationObject *self, PyObject *options) {
  debugPrint("setOptions", "CALLED");
  if (!PyDict_Check(options)) {
    PyErr_SetString(PyExc_TypeError, "'options' argument must be a dict");
    return NULL;
  }

  debugPrint("setOptions", "INITIALIZE NEW MAP");
  std::map<std::string, double> newOptions{};

  PyObject *key{};
  PyObject *value{};
  Py_ssize_t pos{0};
  debugPrint("setOptions", "ITERATE THROUGH PYTHON DICT");
  while (PyDict_Next(options, &pos, &key, &value)) {
    std::string dictKey{PyUnicode_AsUTF8(key)};
    double dictValue{PyFloat_AsDouble(value)};
    if (PyErr_Occurred() != nullptr) {
      PyErr_SetString(PyExc_TypeError, "Failed to parse dict value as double.");
      return NULL;
    }

    if ((self->has_algebraic_eq && !defaultIdaOptions.contains(dictKey)) ||
        (!self->has_algebraic_eq && !defaultCvodeOptions.contains(dictKey))) {
      PyErr_Format(PyExc_KeyError, "Key: '%s' is not a valid option.",
                   dictKey.c_str());
      return NULL;
    }

    debugPrint("setOptions", "INSERT KEY '" + dictKey + "' WITH VALUE '" +
                                 std::to_string(dictValue) + "'");
    newOptions.insert({dictKey, dictValue});
  }

  for (auto it{newOptions.begin()}; it != newOptions.end(); it++) {
    self->optionValues.at(std::distance(self->optionKeys.begin(),
                                        std::find(self->optionKeys.begin(),
                                                  self->optionKeys.end(),
                                                  it->first))) = it->second;
  }

  // update sundials options
  if (self->sundials->setOptions(self->sundials, newOptions) < 0)
    return NULL;

  debugPrint("setOptions", "SUNDIALSOptions:");
  for (size_t i{}; i < self->optionKeys.size(); i++) {
    debugPrint("setOptions", self->optionKeys.at(i) + ":" +
                                 std::to_string(self->optionValues.at(i)));
  }

  for (auto it{newOptions.begin()}; it != newOptions.end(); it++) {
    debugPrint("setOptions", it->first + ":" + std::to_string(it->second));
  }

  debugPrint("setOptions", "RETURN");
  Py_INCREF(Py_None);
  return Py_None;
}

int SIMULATION::setParameterValues(SimulationObject *self,
                                   PyObject *parameterValues) {
  PyObject *valueArray = PyArray_FROM_OTF(
      parameterValues, NPY_DOUBLE, NPY_ARRAY_DEFAULT | NPY_ARRAY_ENSURECOPY);

  if (!valueArray) {
    PyErr_SetString(PyExc_TypeError,
                    "The given value does not match the parameter_values "
                    "attribute type. Expected a 1D list or array of numbers.");
    Py_XDECREF(valueArray);
    return -1;
  }

  // Check number of elements
  int diff{self->numberof[SIMULATION_PARAMETER] -
           static_cast<int>(PYSIZE(valueArray))};

  if (diff > 0) {
    // int diff{self->numberof[SIMULATION_PARAMETER] -
    // static_cast<int>(PYSIZE(valueArray))};
    PyErr_Format(PyExc_ValueError,
                 "Incorrect number of parameter values: %i too few values!",
                 diff);
    Py_XDECREF(valueArray);
    return -1;
  } else if (diff < 0) {
    // int diff{static_cast<int>(PYSIZE(valueArray))
    // - self->numberof[SIMULATION_PARAMETER]};
    PyErr_Format(PyExc_ValueError,
                 "Incorrect number of parameter values: %i too many values!",
                 -diff);
    Py_XDECREF(valueArray);
    return -1;
  }

  PyObject *tmp = self->parametervalues;
  self->parametervalues = valueArray;
  Py_DECREF(tmp);

  return 0;
}

int SIMULATION::setStateValues(SimulationObject *self, PyObject *stateValues) {
  PyObject *valueArray = PyArray_FROM_OTF(
      stateValues, NPY_DOUBLE, NPY_ARRAY_DEFAULT | NPY_ARRAY_ENSURECOPY);
  if (!valueArray) {
    PyErr_SetString(PyExc_TypeError,
                    "The given value does not match the state_values "
                    "attribute type. Expected a 1D list or array of numbers.");
    Py_XDECREF(valueArray);
    return -1;
  }

  // Check number of elements
  int diff{self->numberof[SIMULATION_STATE] -
           static_cast<int>(PYSIZE(valueArray))};

  if (diff > 0) {
    PyErr_Format(PyExc_ValueError,
                 "Incorrect number of state values: %i too few values!", diff);
    Py_XDECREF(valueArray);
    return -1;
  } else if (diff < 0) {
    PyErr_Format(PyExc_ValueError,
                 "Incorrect number of state values: %i too many values!",
                 -diff);
    Py_XDECREF(valueArray);
    return -1;
  }

  PyObject *tmp = self->statevalues;
  self->statevalues = valueArray;
  Py_DECREF(tmp);

  return 0;
}

int SIMULATION::setTimeUnit(SimulationObject *self, PyObject *timeunit) {
  // Normalize Greek mu (U+03BC, 'μ') to micro sign (U+00B5, 'µ') when setting
  // the time unit. This ensures users typing 'μs' are treated the same as 'µs'.
  PyObject *effectiveTimeUnit = timeunit; // borrowed reference
  PyObject *tmpNormalized = NULL;         // owned reference if created

  if (PyUnicode_Check(timeunit)) {
    const char *tu8 = PyUnicode_AsUTF8(timeunit);
    if (tu8 != nullptr && std::string(tu8) == "μs") {
      tmpNormalized = PyUnicode_FromString("µs");
      if (tmpNormalized != NULL) {
        effectiveTimeUnit = tmpNormalized; // use normalized value
      }
    }
  }

  double scale = getTimeScale(self, effectiveTimeUnit);
  if (tmpNormalized != NULL) {
    Py_DECREF(tmpNormalized);
  }

  if (scale < 0) {
    return -1;
  } else if (scale != self->scale) {
    double old_scale = self->scale;
    self->scale = scale;

    if (Simulation_updateModelActivityScale(self) == 0) {
      Simulation_updateDerivativeTimeScale(self, scale / old_scale);
    } else {
      return -1;
    }
  }

  return 0;
}

int SIMULATION::setTimeVector(SimulationObject *self, PyObject *timeVector,
                              bool augmentTimeVector = true) {
  debugPrint("setTimeVector", "CALLED");

  if (timeVector == NULL) {
    PyErr_SetString(PyExc_TypeError,
                    "The 'time_vector' input argument must be set!");
    return -1;
  }

  debugPrint("setTimeVector", "CONVERT TIMEVECTOR FROM PYTHON OBJECT");

  PyObject *timeVectorArray = PyArray_FROM_OTF(
      timeVector, NPY_DOUBLE, NPY_ARRAY_DEFAULT | NPY_ARRAY_ENSURECOPY);
  if (!timeVectorArray || PyArray_NDIM(PYARRAY(timeVectorArray)) != 1) {
    PyErr_SetString(PyExc_TypeError,
                    "The given value does not match the time_vector attribute "
                    "type. Expected a 1D list or array of numbers.");
    Py_XDECREF(timeVectorArray);
    return -1;
  }

  if (PyArray_Size(timeVectorArray) < 2) {
    PyErr_SetString(
        PyExc_ValueError,
        "The 'time_vector' attribute must have at least 2 elements!");
    Py_XDECREF(timeVectorArray);
    return -1;
  }

  debugPrint("setTimeVector", "ASSIGN NEW TIMEVECTOR");

  PyObject *tmp;
  tmp = self->timevector;
  self->timevector = timeVectorArray;
  Py_XDECREF(tmp);

  // Calculate subTimeVectors
  debugPrint("setTimeVector", "CALCULATE SUBTIMEVECTORS");

  // Erase any old subTimeVectors
  debugPrint("setTimeVector", "ERASE OLD SUBTIMEVECTORS");
  self->subTimeVectors.clear();

  // Gets all unique tvalues from all nonconstant outputs in all activities in
  // SimulationObject into a sorted set.
  debugPrint("setTimeVector", "GET UNIQUE TVALUES FROM ACTIVITIES");

  std::set<double> uniqueActivityTimePoints{};
  if (debug::DEBUG) {
    debugPrint("setTimeVector",
               "NUMBER OF ACTIVITIES: " +
                   std::to_string(self->numberof[SIMULATION_ACTIVITY]));
  }
  for (int i{}; i < self->numberof[SIMULATION_ACTIVITY]; i++) {
    PyObject *actObj = self->activities[i].activityObject;
    int nOutputs = nrOutputs(actObj);
    int nManip = PyList_Size(manipulationNames(actObj));
    if (debug::DEBUG) {
      debugPrint("setTimeVector", "ACTIVITY " + std::to_string(i) +
                                      ": nOutputs=" + std::to_string(nOutputs) +
                                      ", nManip=" + std::to_string(nManip));
    }

    // 1) Collect time points from outputs (non-cubic)
    for (int j{}; j < nOutputs; j++) {
      int outputType = getOutputType(actObj, j);
      if (debug::DEBUG) {
        debugPrint("setTimeVector", "OUTPUT TYPE FOR INPUT " +
                                        std::to_string(j) + ": " +
                                        std::to_string(outputType));
      }
      if (outputType == -1) {
        if (PyErr_Occurred())
          return -1;
        PyErr_Format(
            PyExc_RuntimeError,
            "Failed to determine output type for activity %d, output %d", i, j);
        return -1;
      }
      if (outputType == CUBIC_SPLINE) {
        if (debug::DEBUG)
          debugPrint("setTimeVector",
                     "SKIPPING CUBIC SPLINE OUTPUT: " + std::to_string(j));
        continue;
      }
      PyArrayObject *tvalues_arr{getTValues(actObj, j)};
      if (tvalues_arr != NULL && PyArray_TYPE(tvalues_arr) == NPY_DOUBLE) {
        npy_intp num_elements = PyArray_SIZE(tvalues_arr);
        if (num_elements > 0) {
          double *data = static_cast<double *>(PyArray_DATA(tvalues_arr));
          uniqueActivityTimePoints.insert(data, data + num_elements);
          if (debug::DEBUG)
            for (npy_intp ti = 0; ti < num_elements; ++ti)
              debugPrint("setTimeVector",
                         "ADDING OUTPUT TVALUE: " + std::to_string(data[ti]));
        }
      }
    }

    // 2) Collect time points from manipulations explicitly
    for (int m{}; m < nManip; ++m) {
      int idx = nOutputs + m; // manipulation index in activity space
      PyArrayObject *tvalues_arr{getTValues(actObj, idx)};
      if (tvalues_arr != NULL && PyArray_TYPE(tvalues_arr) == NPY_DOUBLE) {
        npy_intp num_elements = PyArray_SIZE(tvalues_arr);
        if (num_elements > 0) {
          double *data = static_cast<double *>(PyArray_DATA(tvalues_arr));
          uniqueActivityTimePoints.insert(data, data + num_elements);
          if (debug::DEBUG)
            for (npy_intp ti = 0; ti < num_elements; ++ti)
              debugPrint("setTimeVector",
                         "ADDING MANIP TVALUE: " + std::to_string(data[ti]));
        }
      }
    }
  }

  if (debug::DEBUG) {
    debugPrint("setTimeVector", "UNIQUE TVALUES:");
    for (auto timePoint : uniqueActivityTimePoints) {
      debugPrint("setTimeVector", std::to_string(timePoint));
    }
  }

  bool timePointsAdded = false;
  std::vector<double> augmentedTimeVector;

  // Populate augmentedTimeVector directly from self->timevector
  PyArrayObject *py_timevector_arr =
      reinterpret_cast<PyArrayObject *>(self->timevector);
  npy_intp timevector_size =
      PyArray_Size(reinterpret_cast<PyObject *>(py_timevector_arr));

  augmentedTimeVector.reserve(timevector_size +
                              uniqueActivityTimePoints.size());

  if (PyArray_ISCARRAY_RO(py_timevector_arr)) {
    double *tv_data = static_cast<double *>(PyArray_DATA(py_timevector_arr));
    augmentedTimeVector.assign(tv_data, tv_data + timevector_size);
  } else {
    for (npy_intp i = 0; i < timevector_size; ++i) {
      augmentedTimeVector.push_back(
          *static_cast<double *>(PyArray_GetPtr(py_timevector_arr, &i)));
    }
  }

  if (debug::DEBUG) {
    debugPrint("setTimeVector", "INITIAL TIMEVECTOR (FROM SELF->TIMEVECTOR):");
    for (auto timePoint : augmentedTimeVector) {
      debugPrint("setTimeVector", std::to_string(timePoint));
    }
  }

  // If augmentation is enabled, add missing activity time points
  if (augmentTimeVector) {

    npy_intp index = timevector_size - 1;
    double originalTimeVectorMax =
        *static_cast<double *>(PyArray_GetPtr(py_timevector_arr, &index));

    // Create a set of points currently in augmentedTimeVector for efficient
    // lookup. This handles potential duplicates in the initial self->timevector
    // by only storing unique points for the check.
    std::set<double> points_in_augmented_vector_checker(
        augmentedTimeVector.begin(), augmentedTimeVector.end());

    for (double activityTimePoint :
         uniqueActivityTimePoints) // uniqueActivityTimePoints is already a
                                   // std::set
    {
      // Check if the activityTimePoint is already present using the helper set.
      if (points_in_augmented_vector_checker.find(activityTimePoint) ==
          points_in_augmented_vector_checker.end()) {
        // Break early if we've exceeded the time range
        if (activityTimePoint > originalTimeVectorMax) {
          if (debug::DEBUG) {
            debugPrint("setTimeVector",
                       "SKIPPING REMAINING POINTS: BEYOND TIME RANGE");
          }
          break; // All remaining points will also be beyond the range
        }

        if (debug::DEBUG) {
          debugPrint("setTimeVector", "ADDING MISSING TIME POINT: " +
                                          std::to_string(activityTimePoint));
        }
        augmentedTimeVector.push_back(
            activityTimePoint); // Add to the actual vector
        points_in_augmented_vector_checker.insert(
            activityTimePoint); // Add to the helper set for subsequent checks
        timePointsAdded = true;
      }
    }
  }

  if (timePointsAdded) {
    // If we added points, sort the vector to maintain time order
    std::sort(augmentedTimeVector.begin(), augmentedTimeVector.end());

    if (debug::DEBUG) {
      debugPrint("setTimeVector", "AUGMENTED TIMEVECTOR:");
      for (auto timePoint : augmentedTimeVector) {
        debugPrint("setTimeVector", std::to_string(timePoint));
      }
    }

    // Update the Python timevector with the augmented version
    npy_intp dims[1] = {static_cast<npy_intp>(augmentedTimeVector.size())};
    PyObject *newTimeVector = PyArray_SimpleNew(1, dims, NPY_DOUBLE);
    memcpy(PyArray_DATA((PyArrayObject *)newTimeVector),
           augmentedTimeVector.data(),
           augmentedTimeVector.size() * sizeof(double));

    tmp = self->internalTimeVector;
    self->internalTimeVector = newTimeVector;
    Py_XDECREF(tmp);

    debugPrint("setTimeVector", "UPDATED TIMEVECTOR WITH MISSING POINTS");
  } else {
    // Create a deep copy of the time vector
    PyObject *internalTimeVectorCopy = PyArray_FROM_OTF(
        self->timevector, NPY_DOUBLE, NPY_ARRAY_DEFAULT | NPY_ARRAY_ENSURECOPY);
    if (!internalTimeVectorCopy) {
      PyErr_SetString(PyExc_MemoryError,
                      "Failed to create internal time vector");
      return -1;
    }
    self->internalTimeVector = internalTimeVectorCopy;
  }

  // Make a new timevector containing all elements in self->timevector (which
  // may have been updated)
  std::vector<double> remainingTimeVector{};
  for (int i{}; i < PyArray_Size(self->internalTimeVector); i++) {
    npy_intp index{i};
    remainingTimeVector.push_back(*static_cast<double *>(PyArray_GetPtr(
        reinterpret_cast<PyArrayObject *>(self->internalTimeVector), &index)));
  }

  if (debug::DEBUG) {
    debugPrint("setTimeVector", "TIMEVECTOR STARTING POINT:");
    for (auto timePoint : remainingTimeVector) {
      debugPrint("setTimeVector", std::to_string(timePoint));
    }

    debugPrint("setTimeVector", "CREATE SUBTIMEVECTORS");
  }

  // For each timepoint, make a new timevector and remove its timepoints from
  // the remaining timevector
  for (double timepoint : uniqueActivityTimePoints) {
    std::vector<double> subTimeVector{};

    for (auto it{remainingTimeVector.begin()};
         it != std::upper_bound(remainingTimeVector.begin(),
                                remainingTimeVector.end(), timepoint);
         it++) {
      debugPrint("setTimeVector", "PARSE TIMEPOINT: " + std::to_string(*it));
      subTimeVector.push_back(*it);
    }

    if (debug::DEBUG) {
      debugPrint("setTimeVector", "PRELIMINARY SUBTIMEVECTOR WITH TIMEPOINTS:");
      for (auto timePoint : subTimeVector) {
        debugPrint("setTimeVector", std::to_string(timePoint));
      }
    }

    // Only subTimeVectors with at least 2 elements are valid
    if (subTimeVector.size() >= 2) {
      // Remove copied elements from remainder except last one (timevectors must
      // overlap!)
      for (size_t i{}; i < subTimeVector.size() - 1; i++) {
        remainingTimeVector.erase(remainingTimeVector.begin());
      }

      debugPrint("setTimeVector", "NEW SUBTIMEVECTOR WITH TIMEPOINTS:");
      for (auto timePoint : subTimeVector) {
        debugPrint("setTimeVector", std::to_string(timePoint));
      }

      // Store the new timevector
      self->subTimeVectors.push_back(subTimeVector);
    }
  }

  // Store remainder if not empty
  if (!remainingTimeVector.empty()) {
    debugPrint("setTimeVector",
               "REMAINING TIME VECTOR EXISTS WITH TIMEPOINTS:");
    for (auto timePoint : remainingTimeVector) {
      debugPrint("setTimeVector", std::to_string(timePoint));
    }

    if (remainingTimeVector.size() > 1) {
      self->subTimeVectors.push_back(remainingTimeVector);
    }
  }

  return 0;
}

// SETTERS
double getTimeScale(SimulationObject *self, PyObject *timeUnit) {
  if (!PyUnicode_Check(timeUnit)) {
    PyErr_SetString(
        PyExc_TypeError,
        "The 'time_unit' attribute must be a valid (unicode) character. Use "
        "either of: 'ns', 'µs', 'ms', 's', 'm', 'h', 'd', 'w' or 'y'");
    return -1.0;
  }

  const char *timeUnitString{PyUnicode_AsUTF8(timeUnit)};
  if (timeUnitString == nullptr) {
    PyErr_SetString(PyExc_TypeError,
                    "The 'time_unit' attribute must be a valid UTF-8 string!");
    return -1.0;
  }

  double scale = Simulation_lookupTimeScale(timeUnitString, timeScaleData);
  if (scale > 0) {
    return scale;
  } else {
    PyErr_Format(PyExc_ValueError,
                 "Incorrect time_unit given: '%S'. Use either of: 'ns', '%U', "
                 "'ms', 's', 'm', 'h', 'd', 'w' or 'y'",
                 timeUnit, PyUnicode_FromString("µs"));
    return -1.0;
  }
}

/*
========================================================================================================================
PyMethods
========================================================================================================================
*/

PyObject *SIMULATION::deepcopy(PyObject *self) {
  PyErr_SetString(PyExc_NotImplementedError,
                  "Deep copying of simulation objects is not supported. Use a "
                  "shallow copy instead!");
  return NULL;
}

PyObject *SIMULATION::differentialStates(SimulationObject *self) {
  return PyArray_Cast((PyArrayObject *)self->idvector, NPY_BOOL);
}

PyObject *SIMULATION::executionOrder(SimulationObject *self) {
  PyObject *exOrder, *name;
  int k;

  if (!self->sharedvariablescheck) {
    if (Simulation_CheckSharedVariables(self) <
        0) { // -1 = missing mandatory input, 0 = dependency error
      return NULL;
    }
  }
  exOrder = StringList_New(self->numberof[SIMULATION_MODEL], 1);
  for (k = 0; k < self->numberof[SIMULATION_MODEL]; k++) {
    name = Model_name(self->models[k].modelObject);
    Py_INCREF(name);
    PyList_SetItem(exOrder, k, name);
  }

  return exOrder;
}

PyObject *SIMULATION::features_To_Dict(SimulationObject *self) {

  PyObject *feature_values = PyDict_New();

  if (!Py_IS_TYPE(self->featurevalues, Py_TYPE(Py_None))) {
    for (int nbf = 0; nbf < self->numberof[MODEL_FEATURE]; nbf++) {
      PyObject *key = PyList_GetItem(self->featurenames, nbf);
      PyObject *val = PyList_New(0);

      for (int i = 0; i < PyArray_DIMS((PyArrayObject *)self->featurevalues)[0];
           i++) {
        PyObject *featureval = PyFloat_FromDouble(*((double *)PyArray_GETPTR2(
            (PyArrayObject *)self->featurevalues, i,
            nbf))); // take the nbf-th element in the sub-list i
        PyList_Append(val, featureval); //
        Py_DECREF(featureval);
      }

      PyDict_SetItem(feature_values, key, val);
      Py_DECREF(val);
      // Py_DECREF(key);
    }
  }
  return feature_values;
}

PyObject *SIMULATION::features_To_Dict_Deprecated(SimulationObject *self) {
  // Emit a DeprecationWarning
  if (PyErr_WarnEx(
          PyExc_DeprecationWarning,
          "The 'feature_data_as_dict' method is deprecated and will be removed "
          "in a future version. Use the 'features_as_dict' method instead!",
          1) < 0) {
    return NULL; // Propagate error if warning turned into exception
  }

  return features_To_Dict(self);
}

PyObject *SIMULATION::getOptions(SimulationObject *self) {
  debugPrint("getOptions", "CALLED");
  debugPrint("getOptions", "ALLOCATE NEW PYTHON DICT");
  PyObject *options{PyDict_New()};
  debugPrint("getOptions", "ITERATE THROUGH SUNDIALSOptions");
  if (self->optionKeys.size() != self->optionValues.size()) {
    PyErr_SetString(PyExc_RuntimeError,
                    "Integrator option keys and values mismatch. Options "
                    "improperly initialized or modified.");
    return NULL;
  }
  for (size_t i{}; i < self->optionKeys.size(); i++) {
    debugPrint("getOptions", "INSERT KEY '" + self->optionKeys[i] +
                                 "' TO VALUE '" +
                                 std::to_string(self->optionValues[i]) + "'");
    PyDict_SetItemString(options, (self->optionKeys[i]).c_str(),
                         PyFloat_FromDouble(self->optionValues[i]));
  }
  debugPrint("getOptions", "RETURN");
  return options;
}

PyObject *SIMULATION::hasAlgebraicEquations(SimulationObject *self) {
  if (self->has_algebraic_eq)
    Py_RETURN_TRUE;
  else
    Py_RETURN_FALSE;
}

// Reconstruction helper for pickle support with keyword-only constructor
static PyObject *_reconstruct_simulation(PyObject *self, PyObject *args) {
  PyObject *cls, *kwargs;
  if (!PyArg_ParseTuple(args, "OO", &cls, &kwargs))
    return NULL;

  // Call the class constructor with keyword arguments
  PyObject *empty_args = PyTuple_New(0); // Empty positional args
  PyObject *result = PyObject_Call(cls, empty_args, kwargs);
  Py_DECREF(empty_args);
  return result;
}

PyObject *SIMULATION::reduce(SimulationObject *self) {
  int k;
  // Deprecated
  PyObject *featurevalues = NULL, *featuredata = NULL;

  PyObject *ret, *args, *kwargs, *state, *timeunit, *models, *activities, *tmp;
  PyObject *reconstruct_func;

  // Deprecated
  if (featurevalues == NULL && featuredata != NULL) {
    featurevalues = featuredata;
  }

  state = Py_BuildValue("OOO", self->eventtimedata, self->eventstatusdata,
                        self->featurevalues);

  models = PyList_New(self->numberof[SIMULATION_MODEL]);
  for (k = 0; k < self->numberof[SIMULATION_MODEL]; k++) {
    tmp = self->models[k].modelObject;
    Py_INCREF(tmp);
    PyList_SetItem(models, self->models[k].originalIndex, tmp);
  }
  activities = PyList_New(self->numberof[SIMULATION_ACTIVITY]);
  for (k = 0; k < self->numberof[SIMULATION_ACTIVITY]; k++) {
    tmp = self->activities[k].activityObject;
    Py_INCREF(tmp);
    PyList_SetItem(activities, k, tmp);
  }
  timeunit = getTimeUnit(self);

  if (self->timevector == NULL) {
    self->timevector = Py_None;
  }

  // Create keyword arguments dictionary for reconstruction
  kwargs = PyDict_New();
  PyDict_SetItemString(kwargs, "models", models);
  if (self->numberof[SIMULATION_ACTIVITY] > 0) {
    PyDict_SetItemString(kwargs, "activities", activities);
  }
  PyDict_SetItemString(kwargs, "time_vector", self->timevector);
  PyDict_SetItemString(kwargs, "time_unit", timeunit);
  PyDict_SetItemString(kwargs, "state_values", self->statevalues);
  PyDict_SetItemString(kwargs, "derivative_values", self->derivativevalues);
  PyDict_SetItemString(kwargs, "parameter_values", self->parametervalues);
  PyDict_SetItemString(kwargs, "options", SIMULATION::getOptions(self));

  // Get the reconstruction function from the module
  PyObject *module = PyImport_ImportModule("sund._Simulation");
  reconstruct_func = PyObject_GetAttrString(module, "_reconstruct_simulation");
  Py_DECREF(module);

  // Create arguments for reconstruction function
  args = Py_BuildValue("(OO)", Py_TYPE(self), kwargs);

  Py_DECREF(models);
  Py_DECREF(activities);
  Py_DECREF(timeunit);
  Py_DECREF(kwargs);

  ret = Py_BuildValue("OOO", reconstruct_func, args, state);
  Py_DECREF(reconstruct_func);
  Py_DECREF(args);
  Py_DECREF(state);

  return ret;
}

PyObject *SIMULATION::resetParameters(SimulationObject *self) {
  debugPrint("resetParameters", "CALLED");

  for (int i{}; i < self->numberof[SIMULATION_MODEL]; i++) {
    debugPrint("resetParameters", "INITIALIZE MODEL");
    SimulationModel *mod = &self->models[i];
    debugPrint("resetParameters", "COPY DEFAULT PARAMETER VALUES");
    memcpy(PYDATA(self->parametervalues) + mod->offset[MODEL_PARAMETER],
           PYDATA(Model_parameters(mod->modelObject)),
           Model_numberof(mod->modelObject)[MODEL_PARAMETER] * sizeof(double));
  }

  debugPrint("resetParameters", "RETURN");
  Py_INCREF(Py_None);
  return Py_None;
}

PyObject *SIMULATION::resetStates(SimulationObject *self) {
  double *to = PYDATA(self->derivativevalues);

  for (int i{}; i < self->numberof[SIMULATION_MODEL]; i++) {
    SimulationModel *mod = &self->models[i];
    int offset = mod->offset[MODEL_STATE];
    int nrstates = Model_numberof(mod->modelObject)[MODEL_STATE];
    // statevalues
    memcpy(PYDATA(self->statevalues) + offset,
           PYDATA(Model_stateValues(mod->modelObject)),
           nrstates * sizeof(double));
    // derivativevalues
    double *from = PYDATA(Model_derivativeValues(mod->modelObject));
    for (int i{}; i < nrstates; i++)
      to[i + offset] = SCALE * from[i];
  }

  Py_INCREF(Py_None);
  return Py_None;
}

PyObject *SIMULATION::setState(SimulationObject *self, PyObject *statetuple) {
  PyObject *tmp;

  PyObject *eventtimedata, *eventstatusdata, *featurevalues;
  if (!PyArg_Parse(statetuple, "((OOO),)", &eventtimedata, &eventstatusdata,
                   &featurevalues))
    return NULL;

  if (eventtimedata != Py_None) {
    if (!PyArray_CheckExact(eventtimedata) ||
        PyArray_NDIM((PyArrayObject *)eventtimedata) != 1) {
      PyErr_SetString(
          PyExc_TypeError,
          "Event time data should be a numpy array with dimension 1");
      return NULL;
    }
  }

  if (eventstatusdata != Py_None) {
    if (!PyArray_CheckExact(eventstatusdata) ||
        PyArray_NDIM((PyArrayObject *)eventstatusdata) != 2) {
      PyErr_SetString(
          PyExc_TypeError,
          "Event time data should be a numpy array with dimension 2");
      return NULL;
    }
  }

  if (featurevalues != Py_None) {
    if (!PyArray_CheckExact(featurevalues) ||
        PyArray_NDIM((PyArrayObject *)featurevalues) != 2) {
      PyErr_SetString(
          PyExc_TypeError,
          "Feature values should be a numpy array with dimension 2");
      return NULL;
    }
    if (PyArray_DIMS((PyArrayObject *)featurevalues)[1] != 0 &&
        PyArray_DIMS((PyArrayObject *)featurevalues)[1] !=
            self->numberof[SIMULATION_FEATURE]) {
      PyErr_SetString(PyExc_TypeError,
                      "Incorrect dimensionality of feature values");
      return NULL;
    }
  }

  if (eventtimedata != Py_None && eventstatusdata != Py_None) {
    if (PyArray_DIMS((PyArrayObject *)eventstatusdata)[1] != 0 &&
        PyArray_DIMS((PyArrayObject *)eventstatusdata)[1] !=
            self->numberof[SIMULATION_EVENT]) {
      PyErr_SetString(PyExc_TypeError,
                      "Incorrect dimensionality of event status data");
      return NULL;
    }

    if (PyArray_DIMS((PyArrayObject *)eventtimedata)[0] !=
        PyArray_DIMS((PyArrayObject *)eventstatusdata)[0]) {
      PyErr_SetString(
          PyExc_TypeError,
          "Dimensions of event time and event status doesn't match");
      return NULL;
    }
  }

  tmp = self->eventtimedata;
  Py_INCREF(eventtimedata);
  self->eventtimedata = eventtimedata;
  Py_DECREF(tmp);

  tmp = self->eventstatusdata;
  Py_INCREF(eventstatusdata);
  self->eventstatusdata = eventstatusdata;
  Py_DECREF(tmp);

  tmp = self->featurevalues;
  Py_INCREF(featurevalues);
  self->featurevalues = featurevalues;
  Py_DECREF(tmp);

  Py_RETURN_NONE;
}

PyObject *SIMULATION::simulate(SimulationObject *self, PyObject *args,
                               PyObject *kwds) {
  static char *kwlist[] = {(char *)"time_vector",
                           (char *)"time",
                           (char *)"t",
                           (char *)"time_unit",
                           (char *)"tu",
                           (char *)"state_values",
                           (char *)"x0",
                           (char *)"derivative_values",
                           (char *)"xdot",
                           (char *)"parameter_values",
                           (char *)"theta",
                           (char *)"p",
                           (char *)"reset",
                           (char *)"options",
                           (char *)"iterative",
                           (char *)"augment_time_vector",
                           NULL};
  PyObject *time_vector{};
  PyObject *time{};
  PyObject *t{};
  PyObject *time_unit{};
  PyObject *tu{};
  PyObject *state_values{};
  PyObject *x0{};
  PyObject *derivative_values{};
  PyObject *xdot{};
  PyObject *parameter_values{};
  PyObject *theta{};
  PyObject *p{};
  PyObject *reset{};
  PyObject *options{};
  PyObject *iterative{};
  PyObject *augment_time_vector{};

  if (!PyArg_ParseTupleAndKeywords(
          args, kwds, "|$OOOOOOOOOOOOOOOO", kwlist, &time_vector, &time, &t,
          &time_unit, &tu, &state_values, &x0, &derivative_values, &xdot,
          &parameter_values, &theta, &p, &reset, &options, &iterative,
          &augment_time_vector)) {
    return NULL;
  }

  bool iterativeFlag{true};
  bool augmentTimeVectorFlag{true}; // Default to true

  // Check augment_time_vector parameter
  if (augment_time_vector != NULL) {
    if (!PyBool_Check(augment_time_vector)) {
      PyErr_SetString(
          PyExc_ValueError,
          "Argument 'augment_time_vector' must be a Boolean value!");
      return NULL;
    }
    if (augment_time_vector == Py_False) {
      augmentTimeVectorFlag = false;
    }
  }

  if (!parseAndSetTimevector(self, time_vector, time, t,
                             augmentTimeVectorFlag)) {
    return NULL;
  }

  if (!parseAndSetTimeunit(self, time_unit, tu)) {
    return NULL;
  }

  if (!parseAndSetStateDerivativeAndResetValues(
          self, state_values, x0, derivative_values, xdot, reset)) {
    return NULL;
  }

  if (!parseAndSetParameterValues(self, parameter_values, theta, p)) {
    return NULL;
  }

  // update options
  if (options) {
    setOptions(self, options);
  }

  if (iterative != NULL) {
    if (!PyBool_Check(iterative)) {
      PyErr_SetString(PyExc_ValueError,
                      "Argument 'iterative' must be a Boolean value!");
      return NULL;
    }
    if (iterative == Py_False) {
      iterativeFlag = false;
    }
  }

  // init simulation
  if (Simulation_InitSimulation(self) < 0) {
    return NULL;
  }

  // Reset activity state tracking to ensure clean state between simulations
  resetActivityStateTracking();

  // Clear old featurevalues
  if (self->featurevalues != NULL) {
    PyObject *tmp{self->featurevalues};
    self->featurevalues = NULL;
    Py_DECREF(tmp);
  }

  applyInitialEvents(self);

  if (!iterativeFlag) {
    if (self->sundials->integrate(
            self->sundials, PYSIZE(self->timevector), PYDATA(self->timevector),
            PYDATA(self->statevalues), PYDATA(self->derivativevalues)) < 0) {
      return NULL;
    }

    // Update event and feature values
    Simulation_updateSimulationData(self, &self->sundials->simdata);
  } else {
    // Create feature values array at the correct final size
    npy_intp dims[2];
    dims[0] = PyArray_Size(self->timevector); // Original time points only
    dims[1] = self->numberof[SIMULATION_FEATURE];
    size_t numFeatures = self->numberof[SIMULATION_FEATURE];

    PyObject *resultfeaturevalues = PyArray_ZEROS(2, dims, NPY_DOUBLE, 0);
    double *destData = static_cast<double *>(
        PyArray_DATA(reinterpret_cast<PyArrayObject *>(resultfeaturevalues)));

    // To track which original time points we've already processed
    std::vector<bool> timePointProcessed(PyArray_Size(self->timevector), false);

    // For fast lookup of time points
    std::unordered_map<double, size_t> timeToOriginalIndex;
    double *origTimeData = static_cast<double *>(
        PyArray_DATA(reinterpret_cast<PyArrayObject *>(self->timevector)));
    {
      const npy_intp originalSize = PyArray_Size(self->timevector);
      for (npy_intp i = 0; i < originalSize; ++i) {
        timeToOriginalIndex[origTimeData[i]] = static_cast<size_t>(i);
      }
    }

    for (std::vector<double> subTimeVector : self->subTimeVectors) {
      if (self->sundials->integrate(
              self->sundials, subTimeVector.size(), subTimeVector.data(),
              PYDATA(self->statevalues), PYDATA(self->derivativevalues)) < 0) {
        return NULL;
      }

      // Directly collect only the feature values we need from this simulation
      // segment
      for (size_t i = 0; i < subTimeVector.size(); i++) {
        double currentTime = subTimeVector[i];
        auto it = timeToOriginalIndex.find(currentTime);

        // Is this time point in our original time vector?
        if (it != timeToOriginalIndex.end() &&
            !timePointProcessed[it->second]) {
          size_t originalIndex = it->second;

          // Copy feature values for this time point directly to the right place
          // in the result
          memcpy(destData + originalIndex * numFeatures,
                 self->sundials->simdata.featurevalues + i * numFeatures,
                 numFeatures * sizeof(double));

          timePointProcessed[it->second] = true;
        }
      }

      // Update event data (no need to update feature values as we're building
      // it separately)
      Simulation_updateSimulationData(self, &self->sundials->simdata, true);

      std::free(self->sundials->simdata.featurevalues);
    }

    // Set the result as the feature values
    self->featurevalues = resultfeaturevalues;
  }

  Py_RETURN_NONE;
}

PyObject *SIMULATION::validateSimulation(SimulationObject *self, PyObject *args,
                                         PyObject *kwds) {
  static char *kwlist[] = {(char *)"print", NULL};
  PyObject *print = NULL;
  int r;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "|$O", kwlist, &print)) {
    return NULL;
  }

  r = Simulation_CheckSharedVariables(self);
  if (PyErr_Occurred()) {
    if (print && PyObject_IsTrue(print))
      PyErr_Print();
    else
      PyErr_Clear();
  }
  if (r > 0) {
    Py_RETURN_TRUE;
  } else {
    Py_RETURN_FALSE;
  }
}

/*
========================================================================================================================
SimulationType definition
========================================================================================================================
*/

static PyObject *Simulation_new(PyTypeObject *type, PyObject *args,
                                PyObject *kwds) {
  debugPrint("Simulation_new", "CALLED");

  debugPrint("Simulation_new", "ALLOCATE SimulationObject");
  SimulationObject *self{(SimulationObject *)type->tp_alloc(type, 0)};

  if (self) {
    debugPrint("Simulation_new", "ALLOCATION SUCCESSFUL");
    debugPrint("Simulation_new", "INITIALIZE MEMBERS");
    // model activities
    self->models = NULL;
    self->activities = NULL;

    // timevector/timeunit - aka. scale
    self->timevector = NULL;
    self->scale = 0.0;
    self->internalTimeVector = NULL;

    // Changed to initiate variables to Py_None - more clean
    // featurevalues
    Py_INCREF(Py_None);
    self->featurevalues = Py_None;
    // eventtimedata
    Py_INCREF(Py_None);
    self->eventtimedata = Py_None;
    // eventstatusdata
    Py_INCREF(Py_None);
    self->eventstatusdata = Py_None;

    // sundials memory
    self->sundials = NULL;
  }

  debugPrint("Simulation_new", "RETURN");
  return (PyObject *)self;
}

static void Simulation_initActivity(SimulationObject *self,
                                    SimulationActivity *act) {
  act->offset[ACTIVITY_OUTPUT] = self->numberof[SIMULATION_OUTPUT];
  act->offset[ACTIVITY_FEATURE] = self->numberof[SIMULATION_FEATURE];

  self->numberof[SIMULATION_FEATURE] += nrFeatures(act->activityObject);
  self->numberof[SIMULATION_OUTPUT] += nrOutputs(act->activityObject);
  setNonEditable(act->activityObject);
}

static void Simulation_initModel(SimulationObject *self, SimulationModel *mod) {
  const int *mod_numberof = Model_numberof(mod->modelObject);

  mod->offset[MODEL_STATE] = self->numberof[SIMULATION_STATE];
  mod->offset[MODEL_FEATURE] = self->numberof[SIMULATION_FEATURE];
  mod->offset[MODEL_OUTPUT] = self->numberof[SIMULATION_OUTPUT];
  mod->offset[MODEL_INPUT] = self->numberof[SIMULATION_INPUT];
  mod->offset[MODEL_EVENT] = self->numberof[SIMULATION_EVENT];
  mod->offset[MODEL_PARAMETER] = self->numberof[SIMULATION_PARAMETER];
  mod->exOrder = -1;

  self->numberof[SIMULATION_STATE] += mod_numberof[MODEL_STATE];
  self->numberof[SIMULATION_FEATURE] += mod_numberof[MODEL_FEATURE];
  self->numberof[SIMULATION_OUTPUT] += mod_numberof[MODEL_OUTPUT];
  self->numberof[SIMULATION_INPUT] += mod_numberof[MODEL_INPUT];
  self->numberof[SIMULATION_EVENT] += mod_numberof[MODEL_EVENT];
  self->numberof[SIMULATION_PARAMETER] += mod_numberof[MODEL_PARAMETER];

  mod->function = Model_modelFunction(mod->modelObject);
  mod->hasoutput = mod_numberof[MODEL_OUTPUT] > 0 ? 1 : 0;
}

static int Simulation_init(PyObject *self_, PyObject *args, PyObject *kwds) {
  debugPrint("Simulation_init", "CALLED");
  SimulationObject *self = (SimulationObject *)self_;
  self->sundials_initialized = false;
  int k, size;
  static char *kwlist[] = {const_cast<char *>("models"),
                           const_cast<char *>("activities"),
                           const_cast<char *>("time_vector"),
                           const_cast<char *>("time"),
                           const_cast<char *>("t"),
                           const_cast<char *>("time_unit"),
                           const_cast<char *>("tu"),
                           const_cast<char *>("state_values"),
                           const_cast<char *>("x0"),
                           const_cast<char *>("derivative_values"),
                           const_cast<char *>("xdot"),
                           const_cast<char *>("parameter_values"),
                           const_cast<char *>("theta"),
                           const_cast<char *>("p"),
                           const_cast<char *>("options"),
                           (char *)"augment_time_vector",
                           NULL};

  debugPrint("Simulation_init", "INITIALIZE PARAMETERS");
  PyObject *models{};
  PyObject *activities{};
  PyObject *time_vector{};
  PyObject *time{};
  PyObject *t{};
  PyObject *time_unit{};
  PyObject *tu{};
  PyObject *state_values{};
  PyObject *x0{};
  PyObject *derivative_values{};
  PyObject *xdot{};
  PyObject *parameter_values{};
  PyObject *theta{};
  PyObject *p{};
  PyObject *options{};
  PyObject *tmp{};
  PyObject *augment_time_vector{};

  debugPrint("Simulation_init", "ASSIGN PYTHON ARGUMENTS");
  if (!PyArg_ParseTupleAndKeywords(
          args, kwds, "|$OOOOOOOOOOOOOOOO", kwlist, &models, &activities,
          &time_vector, &time, &t, &time_unit, &tu, &state_values, &x0,
          &derivative_values, &xdot, &parameter_values, &theta, &p, &options,
          &augment_time_vector)) {
    return -1;
  }

  // Necessary in order to convert input from reduce (copy) function to expected
  // values. Reduce function is incapable of sending NULL.
  if (time_vector == Py_None) {
    time_vector = NULL;
  }
  if (time == Py_None) {
    time = NULL;
  }
  if (t == Py_None) {
    t = NULL;
  }
  if (time_unit == Py_None) {
    time_unit = NULL;
  }
  if (tu == Py_None) {
    tu = NULL;
  }
  if (state_values == Py_None) {
    state_values = NULL;
  }
  if (x0 == Py_None) {
    x0 = NULL;
  }
  if (derivative_values == Py_None) {
    derivative_values = NULL;
  }
  if (xdot == Py_None) {
    xdot = NULL;
  }
  if (parameter_values == Py_None) {
    parameter_values = NULL;
  }
  if (theta == Py_None) {
    theta = NULL;
  }
  if (p == Py_None) {
    p = NULL;
  }
  if (augment_time_vector == Py_None) {
    augment_time_vector = NULL;
  }

  // Check that models argument is provided (now that it's keyword-only)
  if (models == NULL) {
    PyErr_SetString(PyExc_TypeError,
                    "Missing required keyword argument: 'models'");
    return -1;
  }

  bool augmentTimeVectorFlag{true}; // Default to true

  // Check augment_time_vector parameter
  if (augment_time_vector != NULL) {
    if (!PyBool_Check(augment_time_vector)) {
      PyErr_SetString(
          PyExc_ValueError,
          "Argument 'augment_time_vector' must be a Boolean value!");
      return -1;
    }
    if (augment_time_vector == Py_False) {
      augmentTimeVectorFlag = false;
    }
  }

  self->sharedvariablescheck = 0;
  self->numberof[SIMULATION_STATE] = 0;
  self->numberof[SIMULATION_FEATURE] = 0;
  self->numberof[SIMULATION_OUTPUT] = 0;
  self->numberof[SIMULATION_INPUT] = 0;
  self->numberof[SIMULATION_PARAMETER] = 0;

  debugPrint("Simulation_init", "INITIALIZE MODELS");
  // MODEL
  size = Simulation_CheckModels(models);
  if (size <= 0) { // Don't allow for empty list
    PyErr_SetString(PyExc_TypeError, "Incorrect models argument given");
    return -1;
  }

  debugPrint("Simulation_init", "ALLOCATE MODEL MEMORY");
  self->models = static_cast<SimulationModel *>(
      PyMem_Calloc(size, sizeof(SimulationModel)));
  self->numberof[SIMULATION_MODEL] = size;

  if (Model_isModel(models)) {
    Py_INCREF(models);
    self->models[0].modelObject = models;
    self->models[0].originalIndex = 0;
    Simulation_initModel(self, &self->models[0]);
  } else {
    for (k = 0; k < size; k++) {
      tmp = PyList_GetItem(models, k);
      Py_INCREF(tmp);
      self->models[k].modelObject = tmp;
      self->models[k].originalIndex = k;
      Simulation_initModel(self, &self->models[k]);
    }
  }

  debugPrint("Simulation_init", "INITIALIZE ACTIVITIES");
  // activities
  if (activities) {
    size = Simulation_CheckActivities(activities);
    if (size < 0) { // Allow for empty list
      PyErr_SetString(PyExc_TypeError, "Incorrect activities argument given");
      return -1;
    }

    debugPrint("Simulation_init", "ALLOCATE ACTIVITY MEMORY");
    self->activities = static_cast<SimulationActivity *>(
        PyMem_Calloc(size, sizeof(SimulationActivity)));
    self->numberof[SIMULATION_ACTIVITY] = size;

    if (isActivity(activities)) {
      Py_INCREF(activities);
      self->activities[0].activityObject = activities;
      Simulation_initActivity(self, &self->activities[0]);
    } else {
      for (k = 0; k < size; k++) {
        tmp = PyList_GetItem(activities, k);
        Py_INCREF(tmp);
        self->activities[k].activityObject = tmp;
        Simulation_initActivity(self, &self->activities[k]);
      }
    }
  } else {
    self->numberof[SIMULATION_ACTIVITY] = 0;
  }

  debugPrint("Simulation_init", "INITIALIZE MEMBERS");
  // Initialize memory for following members
  npy_intp dims[1];
  dims[0] = self->numberof[SIMULATION_STATE];
  self->statevalues = PyArray_ZEROS(1, dims, NPY_DOUBLE, 0);
  if (!self->statevalues)
    return -1;

  self->derivativevalues = PyArray_ZEROS(1, dims, NPY_DOUBLE, 0);
  if (!self->derivativevalues)
    return -1;

  self->idvector = PyArray_ZEROS(1, dims, NPY_DOUBLE, 0);
  if (!self->idvector)
    return -1;
  dims[0] = self->numberof[SIMULATION_PARAMETER];

  self->parametervalues = PyArray_ZEROS(1, dims, NPY_DOUBLE, 0);
  if (!self->parametervalues)
    return -1;

  // names lists
  // statenames
  self->statenames = StringList_New(self->numberof[SIMULATION_STATE], 1);
  if (!self->statenames)
    return -1;
  // featurenames
  self->featurenames = StringList_New(self->numberof[SIMULATION_FEATURE], 1);
  if (!self->featurenames)
    return -1;
  // featureunits
  self->featureunits = StringList_New(self->numberof[SIMULATION_FEATURE], 1);
  if (!self->featureunits)
    return -1;
  // outputnames
  self->outputnames = StringList_New(self->numberof[SIMULATION_OUTPUT], 1);
  if (!self->outputnames)
    return -1;
  // inputnames
  self->inputnames = StringList_New(self->numberof[SIMULATION_INPUT], 1);
  if (!self->inputnames)
    return -1;
  // parameternames
  self->parameternames =
      StringList_New(self->numberof[SIMULATION_PARAMETER], 1);
  if (!self->parameternames)
    return -1;
  // eventnames
  self->eventnames = StringList_New(self->numberof[SIMULATION_EVENT], 1);
  if (!self->eventnames)
    return -1;

  // Update simulation attribute names
  if (Simulation_SetAttributeNames(self) < 0)
    return -1;

  // Constructor values
  debugPrint("Simulation_init", "ASSIGN ARGUMENTS TO MEMBERS");

  if (!parseAndSetTimevector(self, time_vector, time, t, augmentTimeVectorFlag,
                             true)) {
    return -1;
  }

  if (!parseAndSetTimeunit(self, time_unit, tu)) {
    return -1;
  }
  if (time_unit == nullptr && tu == nullptr) {
    self->scale = 1;
  }
  if (Simulation_updateModelActivityScale(self) < 0) {
    return -1;
  }

  if (!parseAndSetParameterValues(self, parameter_values, theta, p)) {
    return -1;
  }
  if (parameter_values == nullptr && theta == nullptr && p == nullptr) {
    resetParameters(self);
  }

  debugPrint("Simulation_init",
             "COPY CURRENT MODEL VALUES OR USE CONSTRUCTOR VALUES");

  // Copy current state values from models if no constructor values provided
  if (state_values == nullptr && x0 == nullptr) {
    for (int i{}; i < self->numberof[SIMULATION_MODEL]; i++) {
      SimulationModel *mod{&self->models[i]};
      memcpy(&PYDATA(self->statevalues)[mod->offset[MODEL_STATE]],
             PYDATA(Model_stateValues(mod->modelObject)),
             Model_numberof(mod->modelObject)[MODEL_STATE] * sizeof(double));
    }
  } else {
    // Parse and set explicit constructor state values
    if (!parseAndSetStateValues(self, state_values, x0)) {
      return -1;
    }
  }

  // Copy current derivative values from models if no constructor values
  // provided
  if (derivative_values == nullptr && xdot == nullptr) {
    for (int i{}; i < self->numberof[SIMULATION_MODEL]; i++) {
      SimulationModel *mod{&self->models[i]};
      memcpy(&PYDATA(self->derivativevalues)[mod->offset[MODEL_STATE]],
             PYDATA(Model_derivativeValues(mod->modelObject)),
             Model_numberof(mod->modelObject)[MODEL_STATE] * sizeof(double));
    }
  } else {
    // Parse and set explicit constructor derivative values
    if (!parseAndSetDerivativeValues(self, derivative_values, xdot)) {
      return -1;
    }
  }

  // check algebraic states and set id vector
  debugPrint("Simulation_init",
             "CHECK FOR ALGEBRAIC EQUATIONS AND INITIALIZE idvector");
  self->has_algebraic_eq = 0;
  Simulation_idVectorAlgebraicEqs(self);

  // input output buffer/execution list
  debugPrint("Simulation_init", "REALLOCATE INPUT AND OUTPUT BUFFER AGAIN");
  self->sharedvariablescheck = 0;
  self->outputbuffer = static_cast<double *>(
      PyMem_Calloc(self->numberof[SIMULATION_OUTPUT], sizeof(double)));
  self->inputptr = static_cast<double **>(
      PyMem_Calloc(self->numberof[SIMULATION_INPUT], sizeof(double *)));
  self->inputmap = static_cast<int *>(
      PyMem_Calloc(self->numberof[SIMULATION_INPUT], sizeof(int)));
  self->defaultInputValues = static_cast<double *>(
      PyMem_Calloc(self->numberof[SIMULATION_INPUT], sizeof(double)));

  // Validate mandatory inputs
  debugPrint("Simulation_init", "CHECK SHARED VARIABLES");
  if (Simulation_CheckSharedVariables(self) < 0) {
    return -1;
  }

  // sundials object
  debugPrint("Simulation_init", "INITIALIZE SUNDIALS OBJECT");
  if (self->has_algebraic_eq) {
    debugPrint("Simulation_init", "SUNDIALS OBJECT IS IDA");
    self->sundials =
        IDA55_init((void *)self, self->numberof[SIMULATION_STATE],
                   self->numberof[SIMULATION_EVENT],
                   self->numberof[SIMULATION_FEATURE], PYDATA(self->idvector));
    if (!self->sundials)
      return -1;

    debugPrint("Simulation_init", "APPLY DEFAULT IDA OPTIONS");
    for (auto it{defaultIdaOptions.begin()}; it != defaultIdaOptions.end();
         it++) {
      debugPrint("Simulation_init", "INSERT KEY '" + it->first +
                                        "' WITH VALUE '" +
                                        std::to_string(it->second) + "'");
      self->optionKeys.push_back(it->first);
      self->optionValues.push_back(it->second);
    }
  } else {
    debugPrint("Simulation_init", "SUNDIALS OBJECT IS CVODE");
    self->sundials = CVODE55_init(
        (void *)self, self->numberof[SIMULATION_STATE],
        self->numberof[SIMULATION_EVENT], self->numberof[SIMULATION_FEATURE]);
    if (!self->sundials)
      return -1;

    debugPrint("Simulation_init", "APPLY DEFAULT CVODE OPTIONS");
    for (auto it{defaultCvodeOptions.begin()}; it != defaultCvodeOptions.end();
         it++) {
      debugPrint("Simulation_init", "INSERT KEY '" + it->first +
                                        "' WITH VALUE '" +
                                        std::to_string(it->second) + "'");
      self->optionKeys.push_back(it->first);
      self->optionValues.push_back(it->second);
    }
  }
  debugPrint("Simulation_init", "SUNDIALS OBJECT SUCCESSFULLY INITIALIZED");
  self->sundials_initialized = true;

  // sundials options
  debugPrint("Simulation_init",
             "REPLACE SUNDIALS OPTIONS WITH PYTHON ARGUMENT");
  if (options) {
    setOptions(self, options);
  }

  debugPrint("Simulation_init", "RETURN");
  return 0;
}

static void Simulation_dealloc(SimulationObject *self) {
  debugPrint("Simulation_dealloc", "CALLED");
  int k;

  // models
  if (self->models) {
    for (k = 0; k < self->numberof[SIMULATION_MODEL]; k++)
      Py_XDECREF(self->models[k].modelObject);
    PyMem_Free(self->models);
  }

  // activities
  if (self->activities) {
    for (k = 0; k < self->numberof[SIMULATION_ACTIVITY]; k++)
      Py_XDECREF(self->activities[k].activityObject);
    PyMem_Free(self->activities);
  }

  // Python objects
  Py_XDECREF(self->timevector);
  Py_XDECREF(self->internalTimeVector);
  Py_XDECREF(self->statevalues);
  Py_XDECREF(self->derivativevalues);
  Py_XDECREF(self->idvector);
  Py_XDECREF(self->parametervalues);
  Py_XDECREF(self->featurevalues);
  Py_XDECREF(self->featuredata); // Deprecated
  Py_XDECREF(self->eventtimedata);
  Py_XDECREF(self->eventstatusdata);
  Py_XDECREF(self->featurenames);
  Py_XDECREF(self->featureunits);
  Py_XDECREF(self->outputnames);
  Py_XDECREF(self->inputnames);
  Py_XDECREF(self->parameternames);
  Py_XDECREF(self->statenames);
  Py_XDECREF(self->eventnames);

  // Memory buffers
  if (self->outputbuffer)
    PyMem_Free(self->outputbuffer);
  if (self->inputptr)
    PyMem_Free(self->inputptr);
  if (self->inputmap)
    PyMem_Free(self->inputmap);
  if (self->defaultInputValues)
    PyMem_Free(self->defaultInputValues);

  // C++ vectors - explicitly call destructors
  self->subTimeVectors.~vector();
  self->optionKeys.~vector();
  self->optionValues.~vector();

  // sundials object
  if (self->sundials) {
    if (self->sundials_initialized) {
      self->sundials->free(self->sundials);
    } else {
      PyMem_Free(self->sundials);
    }
  }

  Py_TYPE(self)->tp_free((PyObject *)self);

  debugPrint("Simulation_dealloc", "RETURN");
}

static PyTypeObject SimulationType = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name =
        "sund._Simulation.Simulation",
    .tp_basicsize = sizeof(SimulationObject),
    .tp_itemsize = 0,
    .tp_dealloc = (destructor)Simulation_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_doc = "Simulation Object",
    .tp_methods = Simulation_methods,
    .tp_getset = Simulation_getsetters,
    .tp_init = (initproc)Simulation_init,
    .tp_new = Simulation_new,
};

/*
==========================================================================================
C_API FUNCTIONS
==========================================================================================
*/

/*
==========================================================================================
Simulation module definition
==========================================================================================
*/

PyMODINIT_FUNC PyInit__Simulation(void) {
  PyObject *m, *timeScales, *tmp;
  TimeScale *iterator;

  m = PyModule_Create(&Simulation);
  if (m == NULL)
    return NULL;

  // Simulation type
  if (PyType_Ready(&SimulationType) < 0) {
    Py_DECREF(m);
    return NULL;
  }

  Py_INCREF(&SimulationType);

  if (PyModule_AddObject(m, "Simulation", (PyObject *)&SimulationType) < 0) {
    Py_DECREF(&SimulationType);
    Py_DECREF(m);
    return NULL;
  }
  import_array();
  import_StringList();
  import_Activity();
  import_ModelFullAPI();

  // Timescale list
  iterator = timeScaleData;
  timeScales = StringList_New(0, 1);
  if (!timeScales) {
    Py_DECREF(&SimulationType);
    Py_DECREF(m);
    return NULL;
  }
  while (iterator->name) {
    tmp = PyUnicode_FromString(iterator->name);
    if (PyList_Append(timeScales, tmp) < 0) {
      Py_DECREF(timeScales);
      Py_DECREF(tmp);
      Py_DECREF(&SimulationType);
      Py_DECREF(m);
      return NULL;
    }
    Py_DECREF(tmp);
    iterator++;
  }

  if (PyModule_AddObject(m, "TimeScales", timeScales) < 0) {
    Py_DECREF(timeScales);
    Py_DECREF(&SimulationType);
    Py_DECREF(m);
    return NULL;
  }

  return m;
}
