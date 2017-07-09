/* Copyright (c) 2017 Dassault Systemes. All rights reserved. */

#include <stdlib.h>
#include "Python.h"


PYTHON_API NDTable_h create_table(int ndims, const int *dims, const double *data, const double **scales) {
	int i, j;
	NDTable_h table = NDTable_alloc_table();

	table->ndims = ndims;

	for(i = 0; i < ndims; i++) {
		table->dims[i] = dims[i];
		table->scales[i] = (double *)malloc(sizeof(double) * dims[i]);
		for(j = 0; j < dims[i]; j++) {
			table->scales[i][j] = scales[i][j];
		}
	}

	table->numel = NDTable_calculate_numel(table->ndims, table->dims);
	
	table->data = (double *)malloc(sizeof(double) * table->numel);
	for(i = 0; i < table->numel; i++) {
		table->data[i] = data[i];
	}

	return table;
}

PYTHON_API void close_table(NDTable_h table) {
	int i;

	free(table->data);

	for(i = 0; i < MAX_NDIMS; i++) {
		free(table->scales[i]);
	}

	free(table);
}

PYTHON_API int evaluate(
	NDTable_h table,
	int ndims,
	const double **params,
	NDTable_InterpMethod_t interp_method,
	NDTable_ExtrapMethod_t extrap_method,
	int nvalues,
	double *values) {

	int i, j;
	double params_[32];

	for(i = 0; i < nvalues; i++) {
		
		for(j = 0; j < ndims; j++) {
			params_[j] = params[j][i];
		}

		if(NDTable_evaluate(table, ndims, params_, interp_method, extrap_method, &values[i]) != NDTABLE_INTERPSTATUS_OK) {
			return -1;
		}
	}

	return 0;
}

PYTHON_API int evaluate_derivative(
	NDTable_h table, 
	int nparams, 
	const double params[],
	const double delta_params[],
	NDTable_InterpMethod_t interp_method,
	NDTable_ExtrapMethod_t extrap_method, 
	double *value) {

		return NDTable_evaluate_derivative(table, nparams, params, delta_params, interp_method, extrap_method, value);
}
