#ifndef TIMESCALES_H
#define TIMESCALES_H

typedef struct {
  const double scale;
  const char *name;
} TimeScale;

// s, m, h, d
static TimeScale timeScaleData[] = {
    {1e-9, "ns"}, {1e-6, "µs"}, {1e-3, "ms"},  {1, "s"},        {60, "m"},
    {36e2, "h"},  {864e2, "d"}, {6048e2, "w"}, {31536000, "y"}, {0, NULL}};

#endif