/* * * * * * * * * * * * * * * * * * * *
 *  ZcurvePy Source Code               *
 *                                     *
 *  @author      Zhang ZT, Gao F       *
 *  @copyright   Copyright 2025 TUBIC  *
 *  @date        2025-09-09            *
 *  @version     1.7.0                 *
 * * * * * * * * * * * * * * * * * * * */
#include "ZcurvePyUtil.h"

/* Methods definition of _ZcurvePy module */
static PyMethodDef _ZcurvePy_methods[] = {
    {"shuffle", (PyCFunction) ZcurvePy_shuffle, METH_VARARGS|METH_KEYWORDS, NULL},
    {"decode", (PyCFunction) ZcurvePy_decode, METH_VARARGS|METH_KEYWORDS, NULL},
    {"find_island", (PyCFunction) ZcurvePy_findIsland, METH_VARARGS|METH_KEYWORDS, NULL},
    {"get_orfs", (PyCFunction) ZcurvePy_getOrfs, METH_VARARGS|METH_KEYWORDS, NULL},
    {NULL, NULL, 0, NULL}
};

/* Definition of _ZcurvePy module */
static struct PyModuleDef _ZcurvePyModule = {
    PyModuleDef_HEAD_INIT,
    "_ZcurvePy",
    NULL,
    -1,
    _ZcurvePy_methods
};

/* Init function of _ZcurvePy */
PyMODINIT_FUNC PyInit__ZcurvePy(void) {
    /* Import necessary third-party modules */
    PyObject *Bio_SeqRecord = PyImport_ImportModule("Bio.SeqRecord");
    SeqRecord = PyObject_GetAttrString(Bio_SeqRecord, "SeqRecord");
    Py_DECREF(Bio_SeqRecord);

    PyObject *Bio_SeqFeature = PyImport_ImportModule("Bio.SeqFeature");
    SeqFeature = PyObject_GetAttrString(Bio_SeqFeature, "SeqFeature");
    FeatureLocation = PyObject_GetAttrString(Bio_SeqFeature, "FeatureLocation");
    Py_DECREF(Bio_SeqFeature);

    /* Key for BatchZcurveEncoder to parse parameters */
    keyK = Py_BuildValue("s", "k");
    keyPhase = Py_BuildValue("s", "phase");
    keyFreq = Py_BuildValue("s", "freq");
    keyLocal = Py_BuildValue("s", "local");
    keyHyper = Py_BuildValue("s", "hyper_params");
    keyNJobs = Py_BuildValue("s", "n_jobs");

    /* Init the _ZcurvePy module object */
    if (
        PyType_Ready(&ZcurveEncoderType) < 0 ||
        PyType_Ready(&ZcurvePlotterType) < 0 ||
        PyType_Ready(&BatchZcurveEncoderType) < 0 ||
        PyType_Ready(&BatchZcurvePlotterType) < 0 ||
        PyType_Ready(&OrfType)
    ) return NULL;
    _ZcurvePy = PyModule_Create(&_ZcurvePyModule);
    if (_ZcurvePy == NULL)
        return NULL;
    
    /* Load Python type objects to the module */
    Py_INCREF(&ZcurveEncoderType);
    Py_INCREF(&ZcurvePlotterType);
    Py_INCREF(&BatchZcurveEncoderType);
    Py_INCREF(&BatchZcurvePlotterType);
    Py_INCREF(&OrfType);

    if (!PyModule_AddObject(_ZcurvePy, "ZcurveEncoder", (PyObject *) &ZcurveEncoderType))
    if (!PyModule_AddObject(_ZcurvePy, "ZcurvePlotter", (PyObject *) &ZcurvePlotterType))
    if (!PyModule_AddObject(_ZcurvePy, "BatchZcurveEncoder", (PyObject *) &BatchZcurveEncoderType))
    if (!PyModule_AddObject(_ZcurvePy, "BatchZcurvePlotter", (PyObject *) &BatchZcurvePlotterType))
    if (!PyModule_AddObject(_ZcurvePy, "OrfType", (PyObject *) &OrfType))
        return _ZcurvePy;

    Py_DECREF(&ZcurveEncoderType);
    Py_DECREF(&ZcurvePlotterType);
    Py_DECREF(&BatchZcurveEncoderType);
    Py_DECREF(&BatchZcurvePlotterType);
    Py_DECREF(&OrfType);
    Py_DECREF(_ZcurvePy);

    return NULL;
}