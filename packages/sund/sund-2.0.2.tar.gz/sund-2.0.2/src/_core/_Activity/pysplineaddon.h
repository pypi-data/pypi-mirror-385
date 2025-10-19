#include "Python.h"
#include <cmath>

/*
 *========================================================================
 * INTERFACE FUNCTION to piecewise function
 *========================================================================
 */
static double piecewise(int n, double xx, double *x, double *y) {
  /*
  n is the the number of x-points
  n + 1 is the number of intervals i.e. the number of y-points
  return value:
  {
      y[0]    , xx < x[0]
      y[1]    , x[0] <= xx < x[1]
      y[2]    , x[1] <= xx < x[2]
      ...
      y[n-1]  , x[n-2] <= xx < x[n-1]
      y[n]    , xx >= x[n-1]
  }
  */
  int index;

  if (n < 0) {
    PyErr_SetString(PyExc_ValueError,
                    "Incorrect number of points given to piecewise function");
    return -1;
  }

  for (index = 0; index < n && xx >= x[index]; index++)
    ;
  return y[index];
}

/*
 *========================================================================
 * INTERFACE FUNCTION to linear interpolation
 *========================================================================
 */

static double linearInterpolate(int n, double xx, double *x, double *y) {
  int index;

  if (n < 2) {
    PyErr_SetString(PyExc_ValueError,
                    "At least two points needed for linear interpolation");
    return -1;
  }
  // handle of interval values
  if (xx <= x[0])
    return y[0];
  if (xx >= x[n - 1])
    return y[n - 1];

  // find interval
  for (index = 0; xx >= x[index + 1]; index++)
    ;

  return y[index] + (xx - x[index]) * (y[index + 1] - y[index]) /
                        (x[index + 1] - x[index]);
}

/*
 *========================================================================
 * INTERFACE FUNCTION to cubic interpolation
 *========================================================================
 */

static void spline(int n, int e1, int e2, double s1, double s2, double x[],
                   double y[], double b[], double c[], double d[], int *flag);
static double seval(int n, double xx, double x[], double y[], double b[],
                    double c[], double d[], int *last);

static int cubicCalcCoef(int n, int slope, double slope1, double slope2,
                         double *x, double *y, double *b, double *c,
                         double *d) {
  int flag = 0;

  spline(n, slope, slope, slope1, slope2, x, y, b, c, d, &flag);

  if (flag == 1) {
    PyErr_SetString(PyExc_ValueError,
                    "Cubic interpolation requires at least two points");
    return -1;
  } else if (flag == 2) {
    PyErr_SetString(PyExc_ValueError,
                    "The x-values need to be in ascending order");
    return -1;
  }

  return 0;
}

/*=========================================================================
   Cubic spline coefficients
   -------------------------
   Evaluate the coefficients b[i], c[i], d[i], i = 0, 1, .. n-1 for
   a cubic interpolating spline

   S(xx) = Y[i] + b[i] * w + c[i] * w**2 + d[i] * w**3
   where w = xx - x[i]
   and   x[i] <= xx <= x[i+1]

   The n supplied data points are x[i], y[i], i = 0 ... n-1.

   Input :
   -------
   n       : The number of data points or knots (n >= 2)
   end1,
   end2    : = 1 to specify the slopes at the end points
             = 0 to obtain the default conditions
   slope1,
   slope2  : the slopes at the end points x[0] and x[n-1]
             respectively
   x[]     : the abscissas of the knots in strictly
             increasing order
   y[]     : the ordinates of the knots

   Output :
   --------
   b, c, d : arrays of spline coefficients as defined above
             (See note 2 for a definition.)
   iflag   : status flag
            = 0 normal return
            = 1 less than two data points; cannot interpolate
            = 2 x[] are not in ascending order

   This C code written by ...  Peter & Nigel,
   ----------------------      Design Software,
                               42 Gubberley St,
                               Kenmore, 4069,
                               Australia.

   Version ... 1.1, 30 September 1987
   -------     2.0, 6 April 1989    (start with zero subscript)
                                     remove ndim from parameter list
               2.1, 28 April 1989   (check on x[])
               2.2, 10 Oct   1989   change number order of matrix

   Notes ...
   -----
   (1) The accompanying function seval() may be used to evaluate the
       spline while deriv will provide the first derivative.
   (2) Using p to denote differentiation
       y[i] = S(X[i])
       b[i] = Sp(X[i])
       c[i] = Spp(X[i])/2
       d[i] = Sppp(X[i])/6  ( Derivative from the right )
   (3) Since the zero elements of the arrays ARE NOW used here,
       all arrays to be passed from the main program should be
       dimensioned at least [n].  These routines will use elements
       [0 .. n-1].
   (4) Adapted from the text
       Forsythe, G.E., Malcolm, M.A. and Moler, C.B. (1977)
       "Computer Methods for Mathematical Computations"
       Prentice Hall
   (5) Note that although there are only n-1 polynomial segments,
       n elements are requird in b, c, d.  The elements b[n-1],
       c[n-1] and d[n-1] are set to continue the last segment
       past x[n-1].
=========================================================================*/
static void spline(int n, int end1, int end2, double slope1, double slope2,
                   double x[], double y[], double b[], double c[], double d[],
                   int *iflag) { /* begin procedure spline() */

  int nm1, ib, i;
  double t;
  int ascend;

  nm1 = n - 1;
  *iflag = 0;

  if (n < 2) { /* no possible interpolation */
    *iflag = 1;
    return;
  }

  ascend = 1;
  for (i = 1; i < n; ++i)
    if (x[i] <= x[i - 1])
      ascend = 0;
  if (!ascend) {
    *iflag = 2;
    return;
  }

  if (n >= 3) { /* ---- At least quadratic ---- */

    /* ---- Set up the symmetric tri-diagonal system
            b = diagonal
            d = offdiagonal
            c = right-hand-side  */
    d[0] = x[1] - x[0];
    c[1] = (y[1] - y[0]) / d[0];
    for (i = 1; i < nm1; ++i) {
      d[i] = x[i + 1] - x[i];
      b[i] = 2.0 * (d[i - 1] + d[i]);
      c[i + 1] = (y[i + 1] - y[i]) / d[i];
      c[i] = c[i + 1] - c[i];
    }

    /* ---- Default End conditions
            Third derivatives at x[0] and x[n-1] obtained
            from divided differences  */
    b[0] = -d[0];
    b[nm1] = -d[n - 2];
    c[0] = 0.0;
    c[nm1] = 0.0;
    if (n != 3) {
      c[0] = c[2] / (x[3] - x[1]) - c[1] / (x[2] - x[0]);
      c[nm1] =
          c[n - 2] / (x[nm1] - x[n - 3]) - c[n - 3] / (x[n - 2] - x[n - 4]);
      c[0] = c[0] * d[0] * d[0] / (x[3] - x[0]);
      c[nm1] = -c[nm1] * d[n - 2] * d[n - 2] / (x[nm1] - x[n - 4]);
    }

    /* Alternative end conditions -- known slopes */
    if (end1 == 1) {
      b[0] = 2.0 * (x[1] - x[0]);
      c[0] = (y[1] - y[0]) / (x[1] - x[0]) - slope1;
    }
    if (end2 == 1) {
      b[nm1] = 2.0 * (x[nm1] - x[n - 2]);
      c[nm1] = slope2 - (y[nm1] - y[n - 2]) / (x[nm1] - x[n - 2]);
    }

    /* Forward elimination */
    for (i = 1; i < n; ++i) {
      t = d[i - 1] / b[i - 1];
      b[i] = b[i] - t * d[i - 1];
      c[i] = c[i] - t * c[i - 1];
    }

    /* Back substitution */
    c[nm1] = c[nm1] / b[nm1];
    for (ib = 0; ib < nm1; ++ib) {
      i = n - ib - 2;
      c[i] = (c[i] - d[i] * c[i + 1]) / b[i];
    }

    /* c[i] is now the sigma[i] of the text */

    /* Compute the polynomial coefficients */
    b[nm1] =
        (y[nm1] - y[n - 2]) / d[n - 2] + d[n - 2] * (c[n - 2] + 2.0 * c[nm1]);
    for (i = 0; i < nm1; ++i) {
      b[i] = (y[i + 1] - y[i]) / d[i] - d[i] * (c[i + 1] + 2.0 * c[i]);
      d[i] = (c[i + 1] - c[i]) / d[i];
      c[i] = 3.0 * c[i];
    }
    c[nm1] = 3.0 * c[nm1];
    d[nm1] = d[n - 2];

  } /* at least quadratic */

  else /* if n >= 3 */
  {    /* linear segment only  */
    b[0] = (y[1] - y[0]) / (x[1] - x[0]);
    c[0] = 0.0;
    d[0] = 0.0;
    b[1] = b[0];
    c[1] = 0.0;
    d[1] = 0.0;
  }
} /* end of spline() */

/*-------------------------------------------------------------------*/
static double seval(int n, double u, double x[], double y[], double b[],
                    double c[], double d[], int *last)
/*-----------------------------------------------------------------*/
/*Purpose ...
  -------
  Evaluate the cubic spline function

  S(xx) = y[i] + b[i] * w + c[i] * w**2 + d[i] * w**3
  where w = u - x[i]
  and   x[i] <= u <= x[i+1]
  Note that Horner's rule is used.
  If u < x[0]   then i = 0 is used.
  If u > x[n-1] then i = n-1 is used.

  Input :
  -------
  n       : The number of data points or knots (n >= 2)
  u       : the abscissa at which the spline is to be evaluated
  Last    : the segment that was last used to evaluate U
  x[]     : the abscissas of the knots in strictly increasing order
  y[]     : the ordinates of the knots
  b, c, d : arrays of spline coefficients computed by spline().

  Output :
  --------
  seval   : the value of the spline function at u
  Last    : the segment in which u lies

  Notes ...
  -----
  (1) If u is not in the same interval as the previous call then a
      binary search is performed to determine the proper interval.

*/
/*-------------------------------------------------------------------*/
{ /* begin function seval() */

  int i, j, k;
  double w;

  i = *last;
  if (i >= n - 1)
    i = 0;
  if (i < 0)
    i = 0;

  if ((x[i] > u) || (x[i + 1] < u)) { /* ---- perform a binary search ---- */
    i = 0;
    j = n;
    do {
      k = (i + j) / 2; /* split the domain to search */
      if (u < x[k])
        j = k; /* move the upper bound */
      if (u >= x[k])
        i = k; /* move the lower bound */
    } /* there are no more segments to search */
    while (j > i + 1);
  }
  *last = i;

  /* ---- Evaluate the spline ---- */
  w = u - x[i];
  w = y[i] + w * (b[i] + w * (c[i] + w * d[i]));
  return (w);
}
/*-------------------------------------------------------------------*/

/*
 *========================================================================
 * INTERFACE FUNCTION to stateManipulation function
 *========================================================================
 */

// State manipulation function with mode support
// mode: 0 = set (replace value), 1 = add (increment value)
// Returns NaN for set mode when no manipulation should occur
// Returns 0.0 for add mode when no addition should occur
static double stateManipulation(int n, double xx, double *x, double *y,
                                int mode) {
  /*
  State manipulation function for equal-length t and f arrays with mode support
  n is the number of x-points (same as number of y-points)
  mode: 0 = set (replace), 1 = add (increment)
  return value:
  {
      For set mode (0):
          y[i]         , xx == x[i] (manipulation applied at exact time points)
          NaN          , xx != x[i] (no manipulation at any other time)
      For add mode (1):
          y[i]         , xx == x[i] (value to add at exact time points)
          0.0          , xx != x[i] (no addition at any other time)
  }
  State manipulations are discrete impulses that only apply at exact time
  points.
  */
  int index;

  if (n < 1) {
    PyErr_SetString(
        PyExc_ValueError,
        "Incorrect number of points given to stateManipulation function");
    return -1;
  }

  // Check for exact time point matches
  for (index = 0; index < n; index++) {
    if (xx == x[index]) {
      return y[index]; // Return the manipulation value
    }
  }

  // No manipulation at this time
  if (mode == 0) {
    return NAN; // Set mode: use NaN to indicate no manipulation
  } else {
    return 0.0; // Add mode: return 0 (no addition)
  }
}