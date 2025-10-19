/* -----------------------------------------------------------------
 * Programmer(s): Cody J. Balos, Aaron Collier and Radu Serban @ LLNL
 * -----------------------------------------------------------------
 * SUNDIALS Copyright Start
 * Copyright (c) 2002-2024, Lawrence Livermore National Security
 * and Southern Methodist University.
 * All rights reserved.
 *
 * See the top-level LICENSE and NOTICE files for details.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 * SUNDIALS Copyright End
 * -----------------------------------------------------------------
 * SUNDIALS configuration header file.
 * -----------------------------------------------------------------*/

#ifndef _SUNDIALS_CONFIG_H
#define _SUNDIALS_CONFIG_H

#include "sundials/sundials_export.h"

/* Indicates that the function will not report an error via last_err,
   a return code. In C++, it is just defined as noexcept. */
#if defined(__cplusplus)
#define SUNDIALS_NOEXCEPT noexcept
#else
#define SUNDIALS_NOEXCEPT
#endif

#ifndef SUNDIALS_DEPRECATED_MSG
/* Provide compiler-portable deprecation with message. */
#if defined(_MSC_VER) && !defined(__clang__)
/* MSVC syntax */
#define SUNDIALS_DEPRECATED_MSG(msg) __declspec(deprecated(msg))
#else
/* GCC/Clang syntax */
#define SUNDIALS_DEPRECATED_MSG(msg) __attribute__((deprecated(msg)))
#endif
#endif

#ifndef SUNDIALS_DEPRECATED_EXPORT_MSG
#define SUNDIALS_DEPRECATED_EXPORT_MSG(msg)                                    \
  SUNDIALS_EXPORT SUNDIALS_DEPRECATED_MSG(msg)
#endif

#ifndef SUNDIALS_DEPRECATED_NO_EXPORT_MSG
#define SUNDIALS_DEPRECATED_NO_EXPORT_MSG(msg)                                 \
  SUNDIALS_NO_EXPORT SUNDIALS_DEPRECATED_MSG(msg)
#endif

/* ------------------------------------------------------------------
 * Define SUNDIALS version numbers
 * -----------------------------------------------------------------*/

#define SUNDIALS_VERSION "7.4.0"
#define SUNDIALS_VERSION_MAJOR 7
#define SUNDIALS_VERSION_MINOR 4
#define SUNDIALS_VERSION_PATCH 0
#define SUNDIALS_VERSION_LABEL ""
#define SUNDIALS_GIT_VERSION ""

/* ------------------------------------------------------------------
 * SUNDIALS build information
 * -----------------------------------------------------------------*/

#define SUNDIALS_C_COMPILER_HAS_BUILTIN_EXPECT
#define SUNDIALS_C_COMPILER_HAS_ATTRIBUTE_ASSUME
/* #undef SUNDIALS_C_COMPILER_HAS_BUILTIN_ASSUME */
/* #undef SUNDIALS_C_COMPILER_HAS_ASSUME */

/* Define precision of SUNDIALS data type 'sunrealtype'
 * Depending on the precision level, one of the following
 * three macros will be defined:
 *     #define SUNDIALS_SINGLE_PRECISION 1
 *     #define SUNDIALS_DOUBLE_PRECISION 1
 *     #define SUNDIALS_EXTENDED_PRECISION 1
 */
#define SUNDIALS_DOUBLE_PRECISION 1

/* Define type of vector indices in SUNDIALS 'sunindextype'.
 * Depending on user choice of index type, one of the following
 * two macros will be defined:
 *     #define SUNDIALS_INT64_T 1
 *     #define SUNDIALS_INT32_T 1
 */
#define SUNDIALS_INT64_T 1

/* Define the type of vector indices in SUNDIALS 'sunindextype'.
 * The macro will be defined with a type of the appropriate size.
 */
#define SUNDIALS_INDEX_TYPE int64_t

/* Use POSIX timers if available.
 *     #define SUNDIALS_HAVE_POSIX_TIMERS
 */
/* #undef SUNDIALS_HAVE_POSIX_TIMERS */

/* Define the type used for 'suncountertype'.
 * The macro will be defined with a type of the appropriate size.
 */
#define SUNDIALS_COUNTER_TYPE long int

/* ------------------------------------------------------------------
 * SUNDIALS TPL macros
 * -----------------------------------------------------------------*/

/* Set if SUNDIALS is built with MPI support, then
 *     #define SUNDIALS_MPI_ENABLED 1
 * otherwise
 *     #define SUNDIALS_MPI_ENABLED 0
 */
#define SUNDIALS_MPI_ENABLED 0

/* oneMKL interface options */
/* #undef SUNDIALS_ONEMKL_USE_GETRF_LOOP */
/* #undef SUNDIALS_ONEMKL_USE_GETRS_LOOP */

/* SUPERLUMT threading type */
#define SUNDIALS_SUPERLUMT_THREAD_TYPE ""

/* Trilinos with MPI is available, then
 *    #define SUNDIALS_TRILINOS_HAVE_MPI
 */
/* #undef SUNDIALS_TRILINOS_HAVE_MPI */

/* ------------------------------------------------------------------
 * SUNDIALS language macros
 * -----------------------------------------------------------------*/

/* #undef SUNDIALS_BUILD_PACKAGE_FUSED_KERNELS */

/* BUILD SUNDIALS with monitoring functionalities
 * the CUDA NVector.
 */

/* SYCL options */
/* #undef SUNDIALS_SYCL_2020_UNSUPPORTED */

/* ------------------------------------------------------------------
 * SUNDIALS modules enabled
 * -----------------------------------------------------------------*/

#define SUNDIALS_CVODE 1
#define SUNDIALS_IDA 1
#define SUNDIALS_NVECTOR_SERIAL 1
#define SUNDIALS_NVECTOR_MANYVECTOR 1
#define SUNDIALS_SUNMATRIX_BAND 1
#define SUNDIALS_SUNMATRIX_DENSE 1
#define SUNDIALS_SUNMATRIX_SPARSE 1
#define SUNDIALS_SUNLINSOL_BAND 1
#define SUNDIALS_SUNLINSOL_DENSE 1
#define SUNDIALS_SUNLINSOL_PCG 1
#define SUNDIALS_SUNLINSOL_SPBCGS 1
#define SUNDIALS_SUNLINSOL_SPFGMR 1
#define SUNDIALS_SUNLINSOL_SPGMR 1
#define SUNDIALS_SUNLINSOL_SPTFQMR 1
#define SUNDIALS_SUNNONLINSOL_NEWTON 1
#define SUNDIALS_SUNNONLINSOL_FIXEDPOINT 1

#endif /* _SUNDIALS_CONFIG_H */
