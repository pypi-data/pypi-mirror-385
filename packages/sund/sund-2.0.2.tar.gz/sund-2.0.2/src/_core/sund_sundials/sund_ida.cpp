#include "sund_sundials_interface.h"

#include "Python.h"

#include "ida/ida.h"
#include "nvector/nvector_serial.h"
#include "sundials/sundials_context.h"
#include "sundials/sundials_types.h"
#include "sunlinsol/sunlinsol_dense.h"
#include "sunmatrix/sunmatrix_dense.h"

#include <cmath>
#include <map>
#include <stdarg.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string>

#include <iostream>

typedef struct {
  SUNDIALSObject sundialsObject;
  SUNContext context;
  // Integrator setup
  void *integrator_mem;
  SUNMatrix A;
  SUNLinearSolver LS;
  N_Vector u;
  N_Vector udot;
  N_Vector id;
  int *eventstatus;
  // User setup
  void *user_data;
  int nrStates;
  int nrEvents;
  int nrFeatures;
  // Simulations options
  int showIntegratorStats;
  int maxStep;
  long int maxNumSteps;
  double relTol;
  double absTol;
  int maxErrTestFails;
  int maxOrd;
  int maxConvFails;
  double initStep;
  int maxNonlinIters;
  int calcIC;
  int maxNumStepsIC;
  int maxNumJacsIC;
  int maxNumItersIC;
  int maxNumBacksIC;
} IDAObject;

/* Internal functions */
int IDA55_setOptions(void *self, std::map<std::string, double> &options);
static int IDA55_integrate(void *self, int nrtimesteps, double *timevector,
                           double *statevector, double *derivativevector);
static void IDA55_free(void *self);
static void handleIDAOptions(IDAObject *, std::map<std::string, double> &);
static void createIDAIntegratorMemory(IDAObject *);
static void setIDAIntegratorOptions(IDAObject *);
static void reportIDAStats(void *integrator_mem);
static void freeIDAIntegratorMemory(IDAObject *);

/* Functions containing the model equations */
extern void model(void *simData, double time_local, double *statevector,
                  double *derivativevector, double *RESvector,
                  double *featurevector, int DOflag, int timeindex,
                  double *eventvector, int *eventstatus);

/*
========================================================================
 IDA init functions
========================================================================
*/
SUNDIALSObject *IDA55_init(void *user_data, int nrstates, int nrevents,
                           int nrfeatures, double *idvector) {
  IDAObject *ida;
  // Create SUNDIALS idaory
  ida = (IDAObject *)malloc(sizeof(IDAObject));

  // Simulation options
  std::map<std::string, double> options = defaultIdaOptions;
  handleIDAOptions(ida, options);
  if (PyErr_Occurred()) {
    free(ida);
    return NULL;
  }

  SUNContext_Create(SUN_COMM_NULL, &ida->context);

  // SUNDIALS Object
  ida->sundialsObject.integrate = IDA55_integrate;
  ida->sundialsObject.setOptions = IDA55_setOptions;
  ida->sundialsObject.free = IDA55_free;
  ida->sundialsObject.simdata.nreventstriggered = 0;
  ida->sundialsObject.simdata.eventstatusdata = NULL;
  ida->sundialsObject.simdata.eventtimedata = NULL;
  // User setup
  ida->user_data = user_data;
  ida->nrStates = nrstates;
  ida->nrEvents = nrevents;
  ida->nrFeatures = nrfeatures;
  // Integrator setup
  ida->u = N_VMake_Serial(nrstates, NULL, ida->context);
  ida->udot = N_VMake_Serial(nrstates, NULL, ida->context);
  ida->id = N_VMake_Serial(nrstates, idvector, ida->context);
  ida->eventstatus = (int *)calloc(nrevents, sizeof(int));
  ida->A = SUNDenseMatrix(nrstates, nrstates, ida->context);
  ida->LS = SUNLinSol_Dense(ida->u, ida->A, ida->context);

  createIDAIntegratorMemory(ida);
  setIDAIntegratorOptions(ida);

  return (SUNDIALSObject *)ida;
}

/*
========================================================================
 IDA set options
========================================================================
*/
int IDA55_setOptions(void *self, std::map<std::string, double> &options) {
  IDAObject *ida = (IDAObject *)self;
  handleIDAOptions(ida, options);
  if (PyErr_Occurred())
    return -1;
  setIDAIntegratorOptions(ida);
  return 0;
}

/*
========================================================================
 IDA integrate
========================================================================
*/
static int IDA55_integrate(void *self, int nrtimesteps, double *timevector,
                           double *statevector, double *derivativevector) {
  int calcic;
  double treturn{};
  double *eventtimedata, *featurevalues;
  int nrevents, nreventstriggered, *eventstatus, nrfeatures;
  char *eventstatusdata;
  void *integrator_mem, *user_data;
  N_Vector u, udot;
  IDAObject *ida;

  if (nrtimesteps <= 1) {
    PyErr_SetString(PyExc_ValueError,
                    "'timevector' input argument needs to be a vector if you "
                    "want to do a simulation.");
    return -1;
  }

  ida = (IDAObject *)self;
  integrator_mem = ida->integrator_mem;
  user_data = ida->user_data;
  eventstatus = ida->eventstatus;
  nrevents = ida->nrEvents;
  nrfeatures = ida->nrFeatures;
  calcic = ida->calcIC;
  u = ida->u;
  udot = ida->udot;
  N_VSetArrayPointer(statevector, u);
  N_VSetArrayPointer(derivativevector, udot);

  /* Simulations data */
  nreventstriggered = 0;
  eventstatusdata = NULL;
  eventtimedata = NULL;
  featurevalues = (double *)malloc(nrtimesteps * nrfeatures * sizeof(double));

  // Fill featurevalues with feature values for t=0
  model(user_data, timevector[0], statevector, derivativevector, NULL,
        featurevalues, DOFLAG_FEATURE, 0, NULL, NULL);

  IDAReInit(integrator_mem, timevector[0], u, udot);
  if (calcic) {
    int calcICFlag = IDACalcIC(integrator_mem, IDA_YA_YDP_INIT, timevector[1]);
    if (calcICFlag < 0) {
      PyErr_SetString(PyExc_RuntimeError,
                      "IDA Error: Could not calculate initial conditions");
      return -1;
    }
  }

  // Integrate towards each timepoint in timevector
  // Skip initial element of timevector
  for (int timeindex = 1; timeindex < nrtimesteps; timeindex++) {
    // Repeat intergration until tendstep is reached
    while (treturn != timevector[timeindex]) {
      // Perform integration towards tendstep
      int flag = IDASolve(integrator_mem, timevector[timeindex], &treturn, u,
                          udot, IDA_NORMAL);

      // Error has occured if flag < 0
      if (flag < 0) {
        if (flag == IDA_TOO_MUCH_WORK)
          PyErr_SetString(PyExc_RuntimeError, "IDA Error: IDA_TOO_MUCH_WORK");
        else if (flag == IDA_TOO_MUCH_ACC)
          PyErr_SetString(PyExc_RuntimeError, "IDA Error: IDA_TOO_MUCH_ACC");
        else if (flag == IDA_ERR_FAIL || flag == IDA_CONV_FAIL)
          PyErr_SetString(PyExc_RuntimeError, "IDA Error: IDA_ERR_FAILURE");
        else
          PyErr_SetObject(PyExc_RuntimeError,
                          PyUnicode_FromFormat("IDA Error Flag: %d", flag));
        free(eventstatusdata);
        free(eventtimedata);
        free(featurevalues);
        return -1;
      }

      // Event has triggered if flag == IDA_ROOT_RETURN
      if (flag == IDA_ROOT_RETURN) {
        // Check which events have been triggered and set eventstatus[event] = 1
        IDAGetRootInfo(integrator_mem, eventstatus);

        // Apply all events with eventstatus[event] = 1
        model(user_data, treturn, statevector, derivativevector, NULL, NULL,
              DOFLAG_EVENTASSIGN, -1, NULL, eventstatus);

        // Reinit to show effect of event
        IDAReInit(integrator_mem, treturn, u, udot);

        if (calcic) {
          int calcICFlag{-1};
          if (treturn != timevector[timeindex])
            calcICFlag = IDACalcIC(integrator_mem, IDA_YA_YDP_INIT,
                                   timevector[timeindex]);
          else if (timeindex < (nrtimesteps - 1))
            calcICFlag = IDACalcIC(integrator_mem, IDA_YA_YDP_INIT,
                                   timevector[timeindex + 1]);
          if (calcICFlag < 0) {
            PyErr_SetString(PyExc_RuntimeError,
                            "IDA Error: Could not calculate initial conditions "
                            "after event");
            free(eventstatusdata);
            free(eventtimedata);
            free(featurevalues);
            return -1;
          }
        }
        nreventstriggered += 1;
        if (nreventstriggered == 1) {
          eventtimedata = (double *)calloc(1, sizeof(double));
          eventstatusdata = (char *)calloc(nrevents, sizeof(char));
        } else {
          eventtimedata = (double *)realloc((void *)eventtimedata,
                                            nreventstriggered * sizeof(double));
          eventstatusdata =
              (char *)realloc((void *)eventstatusdata,
                              nrevents * nreventstriggered * sizeof(char));
        }
        eventtimedata[nreventstriggered - 1] = treturn;
        for (int i = 0; i < nrevents; i++)
          eventstatusdata[nrevents * (nreventstriggered - 1) + i] =
              (char)eventstatus[i];
      }
    }

    // Update featurevalues
    model(user_data, timevector[timeindex], statevector, derivativevector, NULL,
          &featurevalues[timeindex * nrfeatures], DOFLAG_FEATURE, timeindex,
          NULL, NULL);
  }

  ida->sundialsObject.simdata.nreventstriggered = nreventstriggered;
  ida->sundialsObject.simdata.eventtimedata = eventtimedata;
  ida->sundialsObject.simdata.eventstatusdata = eventstatusdata;
  ida->sundialsObject.simdata.featurevalues = featurevalues;

  if (ida->showIntegratorStats) {
    reportIDAStats(ida->integrator_mem);
  }

  return 0;
}

/*
========================================================================
 IDA free
========================================================================
*/
static void IDA55_free(void *self) {
  IDAObject *ida = (IDAObject *)self;
  freeIDAIntegratorMemory(ida);
  N_VDestroy_Serial(ida->u);
  N_VDestroy_Serial(ida->udot);
  N_VDestroy_Serial(ida->id);
  SUNLinSolFree(ida->LS); /* Free the linear solver */
  SUNMatDestroy(ida->A);  /* Free the matrix used in linear solver */
  free(ida->eventstatus);
  free(ida);
}

/*
========================================================================
 RES function R(t,u,udot)
========================================================================
*/
static int res(double time, N_Vector u, N_Vector udot, N_Vector res,
               void *user_data) {
  double *statevector, *derivativevector, *resvector;
  /* connect input and result data */
  statevector = N_VGetArrayPointer(u);
  derivativevector = N_VGetArrayPointer(udot);
  resvector = N_VGetArrayPointer(res);
  /* run the model */
  model(user_data, time, statevector, derivativevector, resvector, NULL,
        DOFLAG_RESIDUAL, -1, NULL, NULL);
  return (0);
}

/*
========================================================================
 Event function
========================================================================
*/
static int g(double time, N_Vector u, N_Vector udot, double *gout,
             void *user_data) {
  double *statevec, *derivativevec;
  /* connect input data */
  statevec = N_VGetArrayPointer(u);
  derivativevec = N_VGetArrayPointer(udot);
  /* run the event function */
  model(user_data, time, statevec, derivativevec, NULL, NULL, DOFLAG_EVENT, -1,
        gout, NULL);
  return (0);
}

/*
========================================================================
 Free integrator idaory
========================================================================
*/
static void freeIDAIntegratorMemory(IDAObject *ida) {
  IDAFree(&ida->integrator_mem); /* Free the integrator */
}

/*
==============================================
INITIALIZE INTEGRATOR
==============================================
*/

static void createIDAIntegratorMemory(IDAObject *ida) {
  int k, *rootdir;
  void *integrator_mem;
  double *vector;

  // creaty memory
  integrator_mem = IDACreate(ida->context);
  // Init
  vector = (double *)malloc(
      ida->nrStates *
      sizeof(double)); // Dummy variable so initialization can be done
  N_VSetArrayPointer(vector, ida->u);
  N_VSetArrayPointer(vector, ida->udot);
  IDAInit(integrator_mem, res, 0, ida->u, ida->udot);

  // Attach solvers
  IDASetLinearSolver(integrator_mem, ida->LS, ida->A);
  IDASetJacFn(integrator_mem, NULL); // Use a difference quotient Jacobian

  // Add event function
  if (ida->nrEvents > 0) {
    IDARootInit(integrator_mem, ida->nrEvents, g);
    // Set root dir = 1 => increasing direction
    rootdir = (int *)malloc(ida->nrEvents * sizeof(int));
    for (k = 0; k < ida->nrEvents; k++)
      rootdir[k] = 1;
    IDASetRootDirection(integrator_mem, rootdir);
    free(rootdir);
  }

  ida->integrator_mem = integrator_mem;
  free(vector);
}

static void setIDAIntegratorOptions(IDAObject *ida) {
  void *integrator_mem;
  integrator_mem = ida->integrator_mem;
  // Set options
  IDASStolerances(integrator_mem, ida->relTol, ida->absTol);
  IDASetId(integrator_mem, ida->id);
  IDASetUserData(integrator_mem, ida->user_data);
  if (ida->maxStep > 0)
    IDASetMaxStep(integrator_mem, ida->maxStep);
  if (ida->maxNumSteps > 0)
    IDASetMaxNumSteps(integrator_mem, ida->maxNumSteps);
  IDASetMaxErrTestFails(integrator_mem, ida->maxErrTestFails);
  IDASetMaxOrd(integrator_mem, ida->maxOrd);
  IDASetMaxConvFails(integrator_mem, ida->maxConvFails);
  IDASetInitStep(integrator_mem, ida->initStep);
  IDASetMaxNonlinIters(integrator_mem, ida->maxNonlinIters);
  // calc IC options
  IDASetMaxNumStepsIC(integrator_mem, ida->maxNumStepsIC);
  IDASetMaxNumJacsIC(integrator_mem, ida->maxNumJacsIC);
  IDASetMaxNumItersIC(integrator_mem, ida->maxNumItersIC);
  IDASetMaxBacksIC(integrator_mem, ida->maxNumBacksIC);
}

/*
==============================================
 HANDLE THE SIMULATION OPTIONS
==============================================
*/
static void handleIDAOptions(IDAObject *ida,
                             std::map<std::string, double> &options) {
  for (auto it{options.begin()}; it != options.end(); it++) {
    if (it->first == "abs_tol") {
      ida->absTol = it->second;
    }
    if (it->first == "calc_ic") {
      ida->calcIC = it->second;
    } else if (it->first == "init_step") {
      ida->initStep = it->second;
    } else if (it->first == "max_conv_fails") {
      ida->maxConvFails = it->second;
    } else if (it->first == "max_err_test_fails") {
      ida->maxErrTestFails = it->second;
    } else if (it->first == "max_nonlin_iters") {
      ida->maxNonlinIters = it->second;
    } else if (it->first == "max_num_backs_ic") {
      ida->maxNumBacksIC = it->second;
    } else if (it->first == "max_num_iters_ic") {
      ida->maxNumItersIC = it->second;
    } else if (it->first == "max_num_jacs_ic") {
      ida->maxNumJacsIC = it->second;
    } else if (it->first == "max_num_steps") {
      ida->maxNumSteps = it->second;
    } else if (it->first == "max_num_steps_ic") {
      ida->maxNumStepsIC = it->second;
    } else if (it->first == "max_ord") {
      if (it->second > 5 || it->second <= 0) {
        PyErr_SetString(PyExc_ValueError,
                        "Value of 'max_order' option must be positive integer "
                        "not greater than 5!");
        return;
      }
      ida->maxOrd = it->second;
    } else if (it->first == "max_step") {
      ida->maxStep = it->second;
    } else if (it->first == "rel_tol") {
      ida->relTol = it->second;
    } else if (it->first == "show_integrator_stats") {
      if (it->second != 0.0 && it->second != 1.0) {
        PyErr_SetString(PyExc_ValueError, "Value of 'show_integrator_stats' "
                                          "option must be either 0.0 or 1.0");
        return;
      }
      ida->showIntegratorStats = it->second;
    }
  }

  return;
}

/*
========================================================================
 Integration statistics report function
========================================================================
*/
static void reportIDAStats(void *integrator_mem) {
  long int STATS_nsteps;
  long int STATS_nfevals;
  long int STATS_netfails;
  double STATS_hinused;
  double STATS_tolsfac;
  /* Get the statistics */
  IDAGetNumSteps(integrator_mem, &STATS_nsteps);
  IDAGetNumResEvals(integrator_mem, &STATS_nfevals);
  IDAGetNumErrTestFails(integrator_mem, &STATS_netfails);
  IDAGetActualInitStep(integrator_mem, &STATS_hinused);
  IDAGetTolScaleFactor(integrator_mem, &STATS_tolsfac);
  /* Report statistics */
  printf("\nIntegrator Statistics\n");
  printf("=====================\n");
  printf("Cumulative number of internal steps:    %ld\n", STATS_nsteps);
  printf("No. of calls to r.h.s. function:        %ld\n", STATS_nfevals);
  printf("No. of local error test failures:       %ld\n", STATS_netfails);
  printf("Actual init step size used:             %g\n", STATS_hinused);
  printf("Suggested factor for tolerance scaling: %g\n\n", STATS_tolsfac);
}
