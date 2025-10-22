/* * * * * * * * * * * * * * * * * * * *
 *  ZcurvePy C/C++ Core Module         *
 *                                     *
 *  @author      Zhang ZT, Gao F       *
 *  @copyright   Copyright 2025 TUBIC  *
 *  @date        2025-09-09            *
 *  @version     1.7.0                 *
 * * * * * * * * * * * * * * * * * * * */

#ifndef ZCURVEPY_CORE
#define ZCURVEPY_CORE

#include<string.h>
#include<math.h>

// Counter offset values
#define X 0
#define Y 1
#define Z 2
#define L 3

// Constant float values
#define V 1.0F / 2
#define W 1.0F / 3
#define Q 1.0F / 4
#define R 2.0F / 3

#define MAX_FIT_LEN 5000000

#ifdef __cplusplus
extern "C" {
#endif
/* Do non-phase mononucleotide Z-curve transform */
void monoTrans(char *, int, float *, bool, bool);
/* Do non-phase dinucleotide Z-curve transform */
void diTrans(char *, int, float *, bool, bool);
/* Do non-phase trinucleotide Z-curve transform */
void triTrans(char *, int, float *, bool, bool);

/* Do phase mononucleotide Z-curve transform */
void monoPhaseTrans(char *, int, float *, int, bool, bool);
/* Do phase dinucleotide Z-curve transform */
void diPhaseTrans(char *, int, float *, int, bool, bool);
/* Do phase trinucleotide Z-curve transform */
void triPhaseTrans(char *, int, float *, int, bool, bool);
/* Do phase quartnucleotide Z-curve transform */
void quartPhaseTrans(char *, int, float *, int, bool, bool);
/* Do phase quintnucleotide Z-curve transform */
void quintPhaseTrans(char *, int, float *, int, bool, bool);
/* Do phase sexnucleotide Z-curve transform */
void sexPhaseTrans(char *, int, float *, int, bool, bool);

/* Do phase n-nucleotide transform */
void kPhaseTrans(char *, int, float *, int, int, bool, bool);

/* Calculate genome order index */
float genomeOrderIndex(char *, int);
/* Calculate RY order index */
float ryOrderIndex(char *, int);
/* Calculate MK order index */
float mkOrderIndex(char *, int);
/* Calculate WS order index */
float wsOrderIndex(char *, int);
/* Calculate AT order index */
float atOrderIndex(char *, int);
/* Calculate GC order index */
float gcOrderIndex(char *, int);
/* Calculate CpG order index */
float CpGOrderIndex(char *, int);

/* Do Z-curve Transform */
void zTrans(char *, int, float **, int);
/* Do RY-disparity Transform */
void ryTrans(char *, int, float *, int);
/* Do MK-disparity Transform */
void mkTrans(char *, int, float *, int);
/* Do SW-disparity Transform */
void wsTrans(char *, int, float *, int);
/* Do AT-disparity Transform */
void atTrans(char *, int, float *, int);
/* Do GC-disparity Transform */
void gcTrans(char *, int, float *, int);
/* Do RY-profile Transform */
float xPrimeTrans(char *, int, float *, int);
/* Do MK-profile Transform */
float yPrimeTrans(char *, int, float *, int);
/* Do WS-profile Transform */
float zPrimeTrans(char *, int, float *, int);
/* Do AT-profile Transform */
float atPrimeTrans(char *, int, float *, int);
/* Do GC-profile Transform */
float gcPrimeTrans(char *, int, float *, int);
/* Do CpG-profile Transform */
float CpGPrimeTrans(char *, int, float *, int);
/* Do dS(P) Transform */
int genomeDeltaSTrans(char *, int, float *, int, float &);
/* Do dS(P) Transform (RY) */
int ryDeltaSTrans(char *, int, float *, int, float &);
/* Do dS(P) Transform (RY) */
int mkDeltaSTrans(char *, int, float *, int, float &);
/* Do dS(P) Transform (WS) */
int wsDeltaSTrans(char *, int, float *, int, float &);
/* Do dS(P) Transform (WS) */
int atDeltaSTrans(char *, int, float *, int, float &);
/* Do dS(P) Transform (WS) */
int gcDeltaSTrans(char *, int, float *, int, float &);
/* Do dS(P) Transform (CpG) */
int CpGDeltaSTrans(char *, int, float *, int, float &);
/* Do tetrahedron Transform */
void tetrahedron(char *, int, float **);

/* Calculate sliding window WS-skew */
void WSSkew(char *, int, int, float *);

/* Calculate sliding window AT-skew */
void ATSkew(char *, int, int, float *);
/* Calculate sliding window GC-skew */
void GCSkew(char *, int, int, float *);
/* Calculate sliding window AT fraction */
void ATFraction(char *, int, int, float *);
/* Calculate sliding window GC fraction */
void GCFraction(char *, int, int, float *);
/* Calculate overall GC fraction */
float gcFraction(char *, int);

#ifdef __cplusplus
}
#endif

#endif