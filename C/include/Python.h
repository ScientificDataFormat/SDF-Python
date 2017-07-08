/* Copyright (c) 2017 Dassault Systemes. All rights reserved. */

// The following ifdef block is the standard way of creating macros which make exporting 
// from a DLL simpler. All files within this DLL are compiled with the PYTHON_EXPORTS
// symbol defined on the command line. This symbol should not be defined on any project
// that uses this DLL. This way any other project whose source files include this file see 
// PYTHON_API functions as being imported from a DLL, whereas this DLL sees symbols
// defined with this macro as being exported.
#ifdef _WIN32
#define PYTHON_API __declspec(dllexport)
#else
#define PYTHON_API
#endif

#include "NDTable.h"


PYTHON_API NDTable_h create_table(int ndims, const int *dims, const double *data, const double **scales);

PYTHON_API void close_table(NDTable_h table);

PYTHON_API int evaluate(
	NDTable_h table,
	int ndims,
	const double **params,
	NDTable_InterpMethod_t interp_method,
	NDTable_ExtrapMethod_t extrap_method,
	int nvalues,
	double *values);

PYTHON_API int evaluate_derivative(
	NDTable_h table, 
	int nparams, 
	const double params[],
	const double delta_params[],
	NDTable_InterpMethod_t interp_method,
	NDTable_ExtrapMethod_t extrap_method, 
	double *value);
