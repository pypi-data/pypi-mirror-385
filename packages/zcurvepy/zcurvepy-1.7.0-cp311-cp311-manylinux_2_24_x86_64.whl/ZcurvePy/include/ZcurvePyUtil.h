/* * * * * * * * * * * * * * * * * * * *
 *  ZcurvePy Source Code               *
 *                                     *
 *  @author      Zhang ZT, Gao F       *
 *  @copyright   Copyright 2025 TUBIC  *
 *  @date        2025-09-09            *
 *  @version     1.7.0                 *
 * * * * * * * * * * * * * * * * * * * */

#ifndef ZCURVEPY_UTIL
#define ZCURVEPY_UTIL

#include<Python.h>
#include<structmember.h>
#include<cmath>
#include<vector>

#include "ZcurvePyAPIs.h"

#define MAX_CODON_TYPES 32
#define ORF_VECTOR_RESERVE 30000
#define MAX_NUM_STARTS 8
#define PCC_CONSTANT 3.4641016151

/* Island region list node */
class RegionNode {
    public:
    RegionNode *next;  // Next RegionNode
    int start, end; // Start and end point of region
    RegionNode(int, int);
};

/* Python Type Object Orf*/
extern PyTypeObject OrfType;

#ifdef __cplusplus
extern "C" {
#endif
/* get all ORF sequences as Orf object list */
PyObject *ZcurvePy_getOrfs(PyObject *, PyObject *, PyObject *);
/* ZcurvePy.find_island */
PyObject* ZcurvePy_findIsland(PyObject*, PyObject*, PyObject *);
#ifdef __cplusplus
}
#endif
#endif