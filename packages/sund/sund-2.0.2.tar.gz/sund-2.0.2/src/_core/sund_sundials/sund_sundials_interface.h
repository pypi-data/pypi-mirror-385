#ifndef SUNDIALS_INTERFACE_H
#define SUNDIALS_INTERFACE_H

#include "sund_sundials_flags.h"

#include <map>
#include <string>

typedef int SUNDIALS_Integrate(void *self, int nrtimesteps, double *timevector,
                               double *statevector, double *derivativevector);
typedef int SUNDIALS_SetOptions(void *self,
                                std::map<std::string, double> &options);
typedef void SUNDIALS_Free(void *self);

typedef struct {
  int nreventstriggered;
  double *eventtimedata;
  char *eventstatusdata;
  double *featurevalues;
} SUNDIALS_SimData;

typedef struct {
  SUNDIALS_Integrate *integrate;
  SUNDIALS_SetOptions *setOptions;
  SUNDIALS_Free *free;
  SUNDIALS_SimData simdata;
} SUNDIALSObject;

SUNDIALSObject *CVODE55_init(void *user_data, int nrstates, int nrevents,
                             int nrfeatures);
SUNDIALSObject *IDA55_init(void *user_data, int nrstates, int nrevents,
                           int nrfeatures, double *idvector);

const std::map<std::string, double> defaultCvodeOptions{
    {"abs_tol", 1.0e-6},
    {"init_step", 0.0},
    {"max_conv_fails", 10},
    {"max_err_test_fails", 50},
    {"max_hnil", -1},
    {"max_nonlin_iters", 3},
    {"max_num_steps", 100000},
    {"max_ord", 5},
    {"max_step", 0.0},
    {"method", 0},
    {"min_step", 0.0},
    {"rel_tol", 1.0e-6},
    {"show_integrator_stats", 0}};

const std::map<std::string, double> defaultIdaOptions{
    {"abs_tol", 1.0e-6},
    {"calc_ic", 0},
    {"init_step", 0.0},
    {"max_conv_fails", 10},
    {"max_err_test_fails", 50},
    {"max_nonlin_iters", 3},
    {"max_num_backs_ic", 100000},
    {"max_num_iters_ic", 10000},
    {"max_num_jacs_ic", 5000},
    {"max_num_steps", 100000},
    {"max_num_steps_ic", 5000},
    {"max_ord", 5},
    {"max_step", 0.0},
    {"rel_tol", 1.0e-6},
    {"show_integrator_stats", 0}};

#endif