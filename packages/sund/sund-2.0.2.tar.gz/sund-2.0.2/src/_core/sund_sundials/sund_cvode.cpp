#include "sund_sundials_interface.h"

#include "Python.h"

#include "cvode/cvode.h"
#include "nvector/nvector_serial.h"
#include "sundials/sundials_types.h"
#include "sunlinsol/sunlinsol_dense.h"
#include "sunmatrix/sunmatrix_dense.h"
#include "sunnonlinsol/sunnonlinsol_fixedpoint.h"

#include <cmath>
#include <cstdlib>
#include <map>
#include <stdarg.h>
#include <stddef.h>
#include <stdio.h>
#include <string>

typedef struct {
  SUNDIALSObject sundialsObject;
  SUNContext context;
  // Integrator setup
  void *integrator_mem;
  SUNMatrix A;
  SUNLinearSolver LS;
  SUNNonlinearSolver NLS;
  N_Vector u;
  int *eventStatus;
  // User setup
  void *user_data;
  int nrStates;
  int nrEvents;
  int nrFeatures;
  // Simulations options
  int showIntegratorStats;
  int minStep;
  int maxStep;
  long int maxNumSteps;
  double relTol;
  double absTol;
  int maxErrTestFails;
  int maxOrd;
  int maxConvFails;
  double initStep;
  int maxNonlinIters;
  int method;
  int maxHNil;
} CVODEObject;

/* Internal functions */
int CVODE55_setOptions(void *self, std::map<std::string, double> &options);
static int CVODE55_integrate(void *self, int nrtimesteps, double *timevector,
                             double *statevector, double *derivativevector);
static void CVODE55_free(void *self);
void handleCVODEOptions(CVODEObject *, std::map<std::string, double> &);
static void createCVODEIntegratorMemory(CVODEObject *);
static void setCVODEIntegratorOptions(CVODEObject *);
static void reportCVODEStats(void *cvode_mem);
static void freeCVODEIntegratorMemory(CVODEObject *);

/* Functions containing the model equations */
extern void model(void *simData, double time_local, double *statevector,
                  double *derivativevector, double *RESvector,
                  double *featurevector, int DOflag, int timeindex,
                  double *eventvector, int *eventstatus);

/*
========================================================================
 CVODE init functions
========================================================================
*/
SUNDIALSObject *CVODE55_init(void *user_data, int nrstates, int nrevents,
                             int nrfeatures) {
  CVODEObject *cvode;
  // Create SUNDIALS memory
  cvode = (CVODEObject *)malloc(sizeof(CVODEObject));

  // Simulation options
  std::map<std::string, double> options = defaultCvodeOptions;
  handleCVODEOptions(cvode, options);
  if (PyErr_Occurred()) {
    free(cvode);
    return NULL;
  }

  SUNContext_Create(SUN_COMM_NULL, &cvode->context);

  // SUNDIALS Object
  cvode->sundialsObject.integrate = CVODE55_integrate;
  cvode->sundialsObject.setOptions = CVODE55_setOptions;
  cvode->sundialsObject.free = CVODE55_free;
  cvode->sundialsObject.simdata.nreventstriggered = 0;
  cvode->sundialsObject.simdata.eventstatusdata = NULL;
  cvode->sundialsObject.simdata.eventtimedata = NULL;
  // User setup
  cvode->user_data = user_data;
  cvode->nrStates = nrstates;
  cvode->nrEvents = nrevents;
  cvode->nrFeatures = nrfeatures;
  // Integrator setup
  cvode->u = N_VMake_Serial(nrstates, NULL, cvode->context);
  cvode->eventStatus = (int *)calloc(nrevents, sizeof(int));

  createCVODEIntegratorMemory(cvode);
  setCVODEIntegratorOptions(cvode);

  return (SUNDIALSObject *)cvode;
}

/*
========================================================================
 CVODE set options
========================================================================
*/
int CVODE55_setOptions(void *self, std::map<std::string, double> &options) {
  int old_method;
  CVODEObject *cvode;

  cvode = (CVODEObject *)self;
  old_method = cvode->method;

  handleCVODEOptions(cvode, options);
  if (PyErr_Occurred())
    return -1;
  // check if method is change, CVODE integrator memory needs to be re-created
  if (old_method != cvode->method) {
    freeCVODEIntegratorMemory(cvode);
    createCVODEIntegratorMemory(cvode);
  }
  setCVODEIntegratorOptions(cvode);
  return 0;
}

/*
========================================================================
 CVODE integrate
========================================================================
*/
static int CVODE55_integrate(void *self, int nrtimesteps, double *timevector,
                             double *statevector, double *derivativevector) {
  // int k, flag, timeindex;
  // double treturn, tendstep, *eventtimedata, *featurevalues;
  // double treturn, *eventtimedata, *featurevalues;
  double treturn{};
  double *eventtimedata{};
  double *featurevalues{};
  int nrevents{};
  int nreventstriggered{};
  int *eventstatus{};
  int nrfeatures{};
  char *eventstatusdata{};
  void *cvode_mem{};
  void *user_data{};
  N_Vector u{};
  CVODEObject *cvode{};

  cvode = (CVODEObject *)self;
  cvode_mem = cvode->integrator_mem;
  user_data = cvode->user_data;
  eventstatus = cvode->eventStatus;
  nrevents = cvode->nrEvents;
  nrfeatures = cvode->nrFeatures;
  u = cvode->u;
  N_VSetArrayPointer(statevector, u);

  /* Simulations data */
  nreventstriggered = 0;
  eventstatusdata = NULL;
  eventtimedata = NULL;
  featurevalues =
      (double *)std::malloc(nrtimesteps * nrfeatures * sizeof(double));

  // Fill featurevalues with statevector values
  model(user_data, timevector[0], statevector, NULL, NULL, featurevalues,
        DOFLAG_FEATURE, 0, NULL, NULL);

  CVodeReInit(cvode_mem, timevector[0], u);

  // Integrate towards each timepoint in timevector
  // Skip initial element of timevector
  for (int timeindex = 1; timeindex < nrtimesteps; timeindex++) {
    // Repeat intergration until tendstep is reached
    while (treturn != timevector[timeindex]) {
      // Perform integration towards tendstep
      int flag =
          CVode(cvode_mem, timevector[timeindex], u, &treturn, CV_NORMAL);

      // Error has occured if flag < 0
      if (flag < 0) {
        if (flag == CV_TOO_MUCH_WORK)
          PyErr_SetString(PyExc_RuntimeError, "CVODE Error: CV_TOO_MUCH_WORK");
        else if (flag == CV_TOO_MUCH_ACC)
          PyErr_SetString(PyExc_RuntimeError, "CVODE Error: CV_TOO_MUCH_ACC");
        else if (flag == CV_ERR_FAILURE || flag == CV_CONV_FAILURE)
          PyErr_SetString(PyExc_RuntimeError, "CVODE Error: CV_ERR_FAILURE");
        else
          PyErr_SetObject(PyExc_RuntimeError,
                          PyUnicode_FromFormat("CVODE Error Flag: %d", flag));
        free(eventstatusdata);
        free(eventtimedata);
        free(featurevalues);
        return -1;
      }

      // Event has triggered if flag == CV_ROOT_RETURN
      if (flag == CV_ROOT_RETURN) {
        // Check which events have been triggered and set eventstatus[event] = 1
        CVodeGetRootInfo(cvode_mem, eventstatus);

        // Apply all events with eventstatus[event] = 1
        model(user_data, treturn, statevector, NULL, NULL, NULL,
              DOFLAG_EVENTASSIGN, -1, NULL, eventstatus);

        // Reinit to show effect of event
        CVodeReInit(cvode_mem, treturn, u);

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

    // Update featurevalues with statevector values
    model(user_data, timevector[timeindex], statevector, NULL, NULL,
          &featurevalues[timeindex * nrfeatures], DOFLAG_FEATURE, timeindex,
          NULL, NULL);
  }

  // Update derivativevector to last timepoint
  model(user_data, timevector[nrtimesteps - 1], statevector, derivativevector,
        NULL, NULL, DOFLAG_DDT, -1, NULL, NULL);

  // Update event data
  cvode->sundialsObject.simdata.nreventstriggered = nreventstriggered;
  cvode->sundialsObject.simdata.eventtimedata = eventtimedata;
  cvode->sundialsObject.simdata.eventstatusdata = eventstatusdata;
  cvode->sundialsObject.simdata.featurevalues = featurevalues;

  if (cvode->showIntegratorStats) {
    reportCVODEStats(cvode->integrator_mem);
  }

  return 0;
}

/*
========================================================================
 CVODE free
========================================================================
*/
static void CVODE55_free(void *self) {
  CVODEObject *cvode = (CVODEObject *)self;
  freeCVODEIntegratorMemory(cvode);
  N_VDestroy_Serial(cvode->u);
  free(cvode->eventStatus);
  free(cvode);
}

/*
========================================================================
 RHS function f(t,u)
========================================================================
*/
static int f(double time, N_Vector u, N_Vector udot, void *user_data) {
  double *statevector, *derivativevector;
  /* connect input and result data */
  statevector = N_VGetArrayPointer(u);
  derivativevector = N_VGetArrayPointer(udot);
  /* run the model */
  model(user_data, time, statevector, derivativevector, NULL, NULL, DOFLAG_DDT,
        -1, NULL, NULL);
  return (0);
}

/*
========================================================================
 Event function
========================================================================
*/
static int g(double time, N_Vector y, double *gout, void *user_data) {
  double *statevec;
  /* connect input data */
  statevec = N_VGetArrayPointer(y);
  /* run the event function */
  model(user_data, time, statevec, NULL, NULL, NULL, DOFLAG_EVENT, -1, gout,
        NULL);
  return (0);
}

/*
========================================================================
 Free integrator memory
========================================================================
*/
static void freeCVODEIntegratorMemory(CVODEObject *cvode) {
  /* Free all CVODE related memory */
  CVodeFree(&cvode->integrator_mem); /* Free the integrator memory */
  SUNNonlinSolFree(cvode->NLS);      /* Free the non-linear solver */
  SUNLinSolFree(cvode->LS);          /* Free the linear solver */
  SUNMatDestroy(cvode->A);           /* Free the matrix used in linear solver */
}

/*
==============================================
INITIALIZE INTEGRATOR
==============================================
*/
static void createCVODEIntegratorMemory(CVODEObject *cvode) {
  int k, *rootdir;
  void *integrator_mem;
  double *vector;

  /* Set integration method (stiff or non-stiff) */
  if (cvode->method == 0) {
    integrator_mem = CVodeCreate(CV_BDF, cvode->context); /* default stiff */
    cvode->NLS = NULL;                                    // Use default newton
    cvode->A = SUNDenseMatrix(cvode->nrStates, cvode->nrStates, cvode->context);
    cvode->LS = SUNLinSol_Dense(cvode->u, cvode->A, cvode->context);
  } else {
    integrator_mem = CVodeCreate(CV_ADAMS, cvode->context); /* nonstiff */
    cvode->NLS = SUNNonlinSol_FixedPoint(cvode->u, 0, cvode->context);
    cvode->A = NULL;
    cvode->LS = NULL;
  }
  // Init
  vector = (double *)malloc(
      cvode->nrStates *
      sizeof(double)); // Dummy variable so initialization can be done
  N_VSetArrayPointer(vector, cvode->u);
  CVodeInit(integrator_mem, f, 0, cvode->u);

  // Attach solvers
  if (cvode->method == 0) {
    CVodeSetLinearSolver(integrator_mem, cvode->LS, cvode->A);
    CVodeSetJacFn(integrator_mem, NULL); // Use a difference quotient Jacobian
  } else {
    CVodeSetNonlinearSolver(integrator_mem, cvode->NLS);
  }

  // Add event function
  if (cvode->nrEvents > 0) {
    CVodeRootInit(integrator_mem, cvode->nrEvents, g);
    // Set root dir = 1 => increasing direction
    rootdir = (int *)malloc(cvode->nrEvents * sizeof(int));
    for (k = 0; k < cvode->nrEvents; k++)
      rootdir[k] = 1;
    CVodeSetRootDirection(integrator_mem, rootdir);
    free(rootdir);
  }

  cvode->integrator_mem = integrator_mem;
  free(vector);
}

static void setCVODEIntegratorOptions(CVODEObject *cvode) {
  void *integrator_mem;
  integrator_mem = cvode->integrator_mem;
  // Set options
  CVodeSStolerances(integrator_mem, cvode->relTol, cvode->absTol);
  CVodeSetUserData(integrator_mem, cvode->user_data);
  if (cvode->minStep > 0)
    CVodeSetMinStep(integrator_mem, cvode->minStep);
  if (cvode->maxStep > 0)
    CVodeSetMaxStep(integrator_mem, cvode->maxStep);
  if (cvode->maxNumSteps > 0)
    CVodeSetMaxNumSteps(integrator_mem, cvode->maxNumSteps);
  CVodeSetMaxErrTestFails(integrator_mem, cvode->maxErrTestFails);
  CVodeSetMaxOrd(integrator_mem, cvode->maxOrd);
  CVodeSetMaxConvFails(integrator_mem, cvode->maxConvFails);
  CVodeSetInitStep(integrator_mem, cvode->initStep);
  CVodeSetMaxNonlinIters(integrator_mem, cvode->maxNonlinIters);
  CVodeSetMaxHnilWarns(integrator_mem, cvode->maxHNil);
}

/*
==============================================
 HANDLE THE SIMULATION OPTIONS
==============================================
*/
void handleCVODEOptions(CVODEObject *cvode,
                        std::map<std::string, double> &options) {
  for (auto it{options.begin()}; it != options.end(); it++) {
    if (it->first == "abs_tol") {
      cvode->absTol = it->second;
    } else if (it->first == "init_step") {
      cvode->initStep = it->second;
    } else if (it->first == "max_conv_fails") {
      cvode->maxConvFails = it->second;
    } else if (it->first == "max_err_test_fails") {
      cvode->maxErrTestFails = it->second;
    } else if (it->first == "max_hnil") {
      cvode->maxHNil = it->second;
    } else if (it->first == "max_nonlin_iters") {
      cvode->maxNonlinIters = it->second;
    } else if (it->first == "max_num_steps") {
      cvode->maxNumSteps = it->second;
    } else if (it->first == "max_ord") {
      if (cvode->method == 0) {
        if (it->second > 5 || it->second <= 0) {
          PyErr_SetString(PyExc_ValueError,
                          "Value of 'max_order' option must be positive "
                          "integer not greater than 5!");
          return;
        }
      } else {
        if (it->second > 12 || it->second <= 0) {
          PyErr_SetString(PyExc_ValueError,
                          "Value of 'max_order' option must be positive "
                          "integer not greater than 12!");
          return;
        }
      }
      cvode->maxOrd = it->second;
    } else if (it->first == "max_step") {
      cvode->maxStep = it->second;
    } else if (it->first == "min_step") {
      cvode->minStep = it->second;
    } else if (it->first == "rel_tol") {
      cvode->relTol = it->second;
    } else if (it->first == "show_integrator_stats") {
      if (it->second != 0.0 && it->second != 1.0) {
        PyErr_SetString(PyExc_ValueError, "Value of 'show_integrator_stats' "
                                          "option must be either 0.0 or 1.0");
        return;
      }
      cvode->showIntegratorStats = it->second;
    } else if (it->first == "method") {
      if (it->second == 0.0) {
        cvode->method = 0;
        cvode->maxOrd = 5;
      } else if (it->second == 1.0) {
        cvode->method = 1;
        cvode->maxOrd = 12;
      } else {
        PyErr_SetString(PyExc_ValueError,
                        "Value of 'method' option must be either 0.0 or 1.0!");
        return;
      }
    }
  }

  return;
}

/*
 ========================================================================
  Integration statistics report function
 ========================================================================
 */
static void reportCVODEStats(void *integrator_mem) {
  long int STATS_nsteps;
  long int STATS_nfevals;
  long int STATS_netfails;
  double STATS_hinused;
  double STATS_tolsfac;
  /* Get the statistics */
  CVodeGetNumSteps(integrator_mem, &STATS_nsteps);
  CVodeGetNumRhsEvals(integrator_mem, &STATS_nfevals);
  CVodeGetNumErrTestFails(integrator_mem, &STATS_netfails);
  CVodeGetActualInitStep(integrator_mem, &STATS_hinused);
  CVodeGetTolScaleFactor(integrator_mem, &STATS_tolsfac);
  /* Report statistics */
  printf("\nIntegrator Statistics\n");
  printf("=====================\n");
  printf("Cumulative number of internal steps:    %ld\n", STATS_nsteps);
  printf("No. of calls to r.h.s. function:        %ld\n", STATS_nfevals);
  printf("No. of local error test failures:       %ld\n", STATS_netfails);
  printf("Actual init step size used:             %g\n", STATS_hinused);
  printf("Suggested factor for tolerance scaling: %g\n\n", STATS_tolsfac);
}
