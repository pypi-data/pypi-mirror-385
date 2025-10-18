#ifndef NDARRAY
#define NDARRAY

#ifdef __cplusplus
extern "C" {
#endif

#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <Python.h> 
#include <unicodeobject.h> 

/*
 * Editors Notes
 * I kinda couldn't decide between camal case and underscores for var names because I was simulataneously thinking in Python and C.
 * Also has anyone else ever noticed some words look better in camel case and some look better with underscore.
 * 
 */ 

/*
 * Data Types
 * 0x0: float32
 * 0x1: float64
 * 0x2: int32
 * 0x3: int64
 */

typedef struct {
    PyObject_HEAD
    // dimensions
    size_t nd;
    // shape owned by this view
    size_t* dims;
    // strides owned by this view
    size_t* strides;
    // first pointer references data shared
    char* data;
    // See comment above Data Types
    uint8_t dtype;
    // LENGTH 1 ARRAY/just a pointer to a long shared
    size_t* refs;
    // data for the first array shared
    char* originaldata;

} ndarray;

// func type functions
typedef void (*func)(void* elem, const size_t* idx, size_t nd);
void zero4(void* elem, const size_t* idx, size_t nd);
void ndForeach(ndarray* arr, func visit);
void ndPrint(ndarray* arr);

// Python handling
static void ndarray_dealloc(ndarray *self);
static PyObject * ndarray_str(ndarray *self);
static PyObject * ndarray_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int ndarray_init(ndarray *self, PyObject *args, PyObject *kwds);
extern PyMethodDef ndarray_methods[];
extern PyGetSetDef ndarray_getset[];
extern PyTypeObject ndarrayType;

// C Functions
ndarray arrayCInit(size_t nd, u_int8_t dtype, size_t* dims);
int arrayGetElement(ndarray arr, void* out, size_t* idx);
int arraySetElement(ndarray arr, void* in, size_t* idx);
inline void fastGet2D4(ndarray arr, size_t i, size_t j, void* out);
inline void fastGet2D8(ndarray arr, size_t i, size_t j, void* out);
inline void fastSet2D4(ndarray arr, size_t i, size_t j, void* in);
inline void fastSet2D8(ndarray arr, size_t i, size_t j, void* in);
inline void fastIncInt32(ndarray arr, size_t i, size_t j, int32_t val);
inline void fastIncInt64(ndarray arr, size_t i, size_t j, void* out);
void printElemI32(void* elem, const size_t* idx, size_t nd);

#include "ndarray.cpp"

#ifdef __cplusplus
}
#endif

#endif