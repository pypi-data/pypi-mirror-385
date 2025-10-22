/* * * * * * * * * * * * * * * * * * * *
 *  ZcurvePy C/C++ Core Module         *
 *                                     *
 *  @author      Zhang ZT, Gao F       *
 *  @copyright   Copyright 2025 TUBIC  *
 *  @date        2025-09-09            *
 *  @version     1.7.0                 *
 * * * * * * * * * * * * * * * * * * * */
#include"ZcurvePyCore.h"
/* 
 * Map for converting ASCII chars into one-hot vectors
 *
 * A = [1, 0, 0, 0] G = [0, 1, 0, 0]
 * C = [0, 0, 1, 0] T = [0, 0, 0, 1]
 * 
 * Degenerate symbols are calculated by probabilities
 */
static float ONE_HOT[][4] = 
{   
    {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, 
    {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, 
    {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, 
    {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, 
    {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, 
    {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, 
    {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, 
    {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, 
    {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, 
    {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, 
    {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, 
    {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, 
    {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, 
    {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, 
    {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, 
    {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0},
    {0, 0, 0, 0},  
    {1, 0, 0, 0}, {0, W, W, W}, {0, 0, 1, 0}, {W, W, 0, W},
    {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 1, 0, 0}, {W, 0, W, W}, 
    {Q, Q, Q, Q}, {0, 0, 0, 0}, {0, V, 0, V}, {0, 0, 0, 0},
    {V, 0, V, 0}, {Q, Q, Q, Q}, {0, 0, 0, 0}, {0, 0, 0, 0},
    {0, 0, 0, 0}, {V, V, 0, 0}, {0, V, V, 0}, {0, 0, 0, 1},
    {0, 0, 0, 1}, {W, W, W, 0}, {V, 0, 0, V}, {0, 0, 0, 0}, 
    {0, 0, V, V}, {1, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0},
    {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, 
    {1, 0, 0, 0}, {0, W, W, W}, {0, 0, 1, 0}, {W, W, 0, W},
    {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 1, 0, 0}, {W, 0, W, W}, 
    {Q, Q, Q, Q}, {0, 0, 0, 0}, {0, V, 0, V}, {0, 0, 0, 0}, 
    {V, 0, V, 0}, {Q, Q, Q, Q}, {0, 0, 0, 0}, {0, 0, 0, 0}, 
    {0, 0, 0, 0}, {V, V, 0, 0}, {0, V, V, 0}, {0, 0, 0, 1},
    {0, 0, 0, 1}, {W, W, W, 0}, {V, 0, 0, V}, {0, 0, 0, 0},
    {0, 0, V, V}, {1, 0, 0, 0}
};

/* 
 * Map for converting ASCII chars into one-hot vectors
 * A or G = [1, 0] C or T = [0, 1]
 * 
 * Degenerate symbols are calculated by probabilities
 */
static float RY_HOT[][2] = 
{
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0},
    {1, 0}, {W, R}, {0, 1}, {R, W},
    {0, 0}, {0, 0}, {1, 0}, {W, R}, 
    {V, V}, {0, 0}, {V, V}, {0, 0},
    {V, V}, {V, V}, {0, 0}, {0, 0},
    {0, 0}, {1, 0}, {V, V}, {0, 1},
    {0, 1}, {R, W}, {V, V}, {0, 0}, 
    {0, 1}, {1, 0}, {0, 0}, {0, 0},
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {1, 0}, {W, R}, {0, 1}, {R, W},
    {0, 0}, {0, 0}, {1, 0}, {W, R}, 
    {V, V}, {0, 0}, {V, V}, {0, 0},
    {V, V}, {V, V}, {0, 0}, {0, 0},
    {0, 0}, {1, 0}, {V, V}, {0, 1},
    {0, 1}, {R, W}, {V, V}, {0, 0}, 
    {0, 1}, {1, 0}
};

/* 
 * Map for converting ASCII chars into one-hot vectors
 * A or C = [1, 0] G or T = [0, 1]
 * 
 * Degenerate symbols are calculated by probabilities
 */
static float MK_HOT[][2] = 
{
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0},
    {1, 0}, {W, R}, {1, 0}, {W, R},
    {0, 0}, {0, 0}, {0, 1}, {W, R}, 
    {V, V}, {0, 0}, {0, 1}, {0, 0},
    {1, 0}, {V, V}, {0, 0}, {0, 0},
    {0, 0}, {V, V}, {V, V}, {0, 1},
    {0, 1}, {R, W}, {V, V}, {0, 0}, 
    {V, V}, {1, 0}, {0, 0}, {0, 0},
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {1, 0}, {W, R}, {1, 0}, {W, R},
    {0, 0}, {0, 0}, {0, 1}, {W, R}, 
    {V, V}, {0, 0}, {0, 1}, {0, 0},
    {1, 0}, {V, V}, {0, 0}, {0, 0},
    {0, 0}, {V, V}, {V, V}, {0, 1},
    {0, 1}, {R, W}, {V, V}, {0, 0}, 
    {V, V}, {1, 0}
};

/* 
 * Map for converting ASCII chars into one-hot vectors
 * G or C = [1, 0] A or T = [0, 1]
 * 
 * Degenerate symbols are calculated by probabilities
 */
static float WS_HOT[][2] = 
{
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0},
    {0, 1}, {R, W}, {1, 0}, {W, R},
    {0, 0}, {0, 0}, {1, 0}, {W, R}, 
    {V, V}, {0, 0}, {V, V}, {0, 0},
    {V, V}, {V, V}, {0, 0}, {0, 0},
    {0, 0}, {V, V}, {1, 0}, {0, 1},
    {0, 1}, {R, W}, {0, 1}, {0, 0}, 
    {V, V}, {0, 1}, {0, 0}, {0, 0},
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 1}, {R, W}, {1, 0}, {W, R},
    {0, 0}, {0, 0}, {1, 0}, {W, R},
    {V, V}, {0, 0}, {V, V}, {0, 0}, 
    {V, V}, {V, V}, {0, 0}, {0, 0}, 
    {0, 0}, {V, V}, {1, 0}, {0, 1},
    {0, 1}, {R, W}, {0, 1}, {0, 0},
    {V, V}, {0, 1}
};

/* 
 * Map for converting ASCII chars into one-hot vectors
 * A = [1, 0] T = [0, 1]
 * 
 * Degenerate symbols are calculated by probabilities
 */
static float AT_HOT[][2] = 
{
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0},
    {1, 0}, {0, W}, {0, 0}, {W, W},
    {0, 0}, {0, 0}, {0, 0}, {W, W}, 
    {Q, Q}, {0, 0}, {0, V}, {0, 0},
    {V, 0}, {Q, Q}, {0, 0}, {0, 0},
    {0, 0}, {V, 0}, {0, 0}, {0, 1},
    {0, 1}, {W, 0}, {V, V}, {0, 0}, 
    {0, V}, {1, 0}, {0, 0}, {0, 0},
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {1, 0}, {0, W}, {0, 0}, {W, W},
    {0, 0}, {0, 0}, {0, 0}, {W, W}, 
    {Q, Q}, {0, 0}, {0, V}, {0, 0},
    {V, 0}, {Q, Q}, {0, 0}, {0, 0},
    {0, 0}, {V, 0}, {0, 0}, {0, 1},
    {0, 1}, {W, 0}, {V, V}, {0, 0}, 
    {0, V}, {1, 0}
};

/* 
 * Map for converting ASCII chars into one-hot vectors
 * G = [1, 0] C = [0, 1]
 * 
 * Degenerate symbols are calculated by probabilities
 */
static float GC_HOT[][2] = 
{
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0},
    {0, 0}, {W, W}, {0, 1}, {W, 0},
    {0, 0}, {0, 0}, {1, 0}, {0, W},
    {Q, Q}, {0, 0}, {V, 0}, {0, 0},
    {0, V}, {Q, Q}, {0, 0}, {0, 0},
    {0, 0}, {V, 0}, {V, V}, {0, 0},
    {0, 0}, {W, W}, {0, 0}, {0, 0}, 
    {0, V}, {0, 0}, {0, 0}, {0, 0},
    {0, 0}, {0, 0}, {0, 0}, {0, 0}, 
    {0, 0}, {W, W}, {0, 1}, {W, 0},
    {0, 0}, {0, 0}, {1, 0}, {0, W},
    {Q, Q}, {0, 0}, {V, 0}, {0, 0},
    {0, V}, {Q, Q}, {0, 0}, {0, 0},
    {0, 0}, {V, 0}, {V, V}, {0, 0},
    {0, 0}, {W, W}, {0, 0}, {0, 0}, 
    {0, V}, {0, 0}
};

/* 
 * Map for converting ASCII chars into Z-curve coordinate
 *
 * A = [+1, +1, +1]  G = [+1, -1, -1]
 * C = [-1, +1, -1]  T = [-1, -1, +1]
 * 
 * Degenerate symbols are calculated by weighted vector sum
 */
static float Z_HOT[][3] = {
    {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0},
    {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0},
    {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0},
    {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0},
    {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0},
    {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0},
    {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0},
    {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0},
    {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0},
    {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0},
    {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0},
    {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0},
    {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0},
    {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0},
    {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0},
    {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0},
    {+0, +0, +0},
    {+1, +1, +1}, {-W, -W, -W}, {-1, +1, -1}, {+W, -W, +W},
    {+0, +0, +0}, {+0, +0, +0}, {+1, -1, -1}, {-W, +W, +W},
    {+0, +0, +0}, {+0, +0, +0}, {+0, -1, +0}, {+0, +0, +0},
    {+0, +1, +0}, {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0},
    {+0, +0, +0}, {+1, +0, +0}, {+0, +0, -1}, {-1, -1, +1},
    {-1, -1, +1}, {+W, +W, -W}, {+0, +0, +1}, {+0, +0, +0},
    {+1, +0, +0}, {+1, +1, +1}, {+0, +0, +0}, {+0, +0, +0},
    {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0},
    {+1, +1, +1}, {-W, -W, -W}, {-1, +1, -1}, {+W, -W, +W},
    {+0, +0, +0}, {+0, +0, +0}, {+1, -1, -1}, {-W, +W, +W},
    {+0, +0, +0}, {+0, +0, +0}, {+0, -1, +0}, {+0, +0, +0},
    {+0, +1, +0}, {+0, +0, +0}, {+0, +0, +0}, {+0, +0, +0},
    {+0, +0, +0}, {+1, +0, +0}, {+0, +0, -1}, {-1, -1, +1},
    {-1, -1, +1}, {+W, +W, -W}, {+0, +0, +1}, {+0, +0, +0},
    {+1, +0, +0}, {+1, +1, +1}
};
/* 
 * Mean-value smoothing progress for curves' y-values
 * Choose 'same' as the mode of convolution calculation
 * Using variable window so there is no padding method
 */
static void meanSmoothing(float *params, int len, int window) {
    // window = 0 means do nothing
    if (window) {
        float *buf = new float[len], ySum;
        int i, s, e, half = window / 2;

        // Init sum quene
        for (i = 0, ySum = 0; i < half - 1; i ++)
            ySum += params[i];

        /* 
         * In the following progress, every time a value added
         * from the front, a value substract from the back 
         */
        for (i = 0; i < len; i ++) {
            // s points the first element of the region
            s = (i - half) > 0 ? (i - half) : 0;
            // e points the last element of the region
            /* when e = len, it is to avoid adding the last element repeatedly */
            e = (i + half - 1) < len ? (i + half - 1) : len;

            if (s > 0) 
                ySum -= params[s - 1];

            if (e < len) 
                ySum += params[e];
            else if (e == len) 
                e -= 1; // rollback to calculate the length of region correctly

            buf[i] = ySum / (e - s + 1);
        }

        for (i = 0; i < len; i ++)
            params[i] = buf[i];

        delete[] buf;
    }
}

#ifdef __cplusplus
extern "C" {
#endif

void monoTrans(char *seq, int len, float *params, bool norml, bool local) {
    int i;

    for (i = 0; i < len; i ++) {
        params[X] += Z_HOT[seq[i]][X];
        params[Y] += Z_HOT[seq[i]][Y];
        params[Z] += Z_HOT[seq[i]][Z];
    }

    if (norml && len > 0) {
        params[X] /= len;
        params[Y] /= len;
        params[Z] /= len;
    }
}

void diTrans(char *seq, int len, float *params, bool norml, bool local) {
    float counts[4][4] = {{0.0f}};
    int i, j, sublen = len - 1;
    float denom;

    for (i = 0; i < sublen; i ++)
        for (j = 0; j < 4; j ++) {
            counts[j][X] += ONE_HOT[seq[i]][j] * Z_HOT[seq[i + 1]][X];
            counts[j][Y] += ONE_HOT[seq[i]][j] * Z_HOT[seq[i + 1]][Y];
            counts[j][Z] += ONE_HOT[seq[i]][j] * Z_HOT[seq[i + 1]][Z];
            counts[j][L] += ONE_HOT[seq[i]][j];
        }
        
    for (i = 0; i < 4; i ++, params += 3) {
        params[X] = counts[i][X];
        params[Y] = counts[i][Y];
        params[Z] = counts[i][Z];

        if (norml) {
            denom = local ? counts[i][L] : sublen;

            if (denom > 0) {
                params[X] /= denom;
                params[Y] /= denom;
                params[Z] /= denom;
            }
        }
    }
}

void triTrans(char *seq, int len, float *params, bool norml, bool local) {
    float counts[4][4][4] = {{{0.0f}}};
    int i, j, l, sublen = len - 2;
    float denom;

    for (i = 0; i < sublen; i ++)
        for (j = 0; j < 4; j ++)
        for (l = 0; l < 4; l ++) {
            counts[j][l][X] += ONE_HOT[seq[i]][j] * ONE_HOT[seq[i + 1]][l] * Z_HOT[seq[i + 2]][X];
            counts[j][l][Y] += ONE_HOT[seq[i]][j] * ONE_HOT[seq[i + 1]][l] * Z_HOT[seq[i + 2]][Y];
            counts[j][l][Z] += ONE_HOT[seq[i]][j] * ONE_HOT[seq[i + 1]][l] * Z_HOT[seq[i + 2]][Z];
            counts[j][l][L] += ONE_HOT[seq[i]][j] * ONE_HOT[seq[i + 1]][l];
        }

    for (i = 0; i < 4; i ++)
    for (j = 0; j < 4; j ++, params += 3) {
        params[X] = counts[i][j][X];
        params[Y] = counts[i][j][Y];
        params[Z] = counts[i][j][Z];

        if (norml) {
            denom = local ? counts[i][j][L] : sublen;

            if (denom > 0) {
                params[X] /= denom;
                params[Y] /= denom;
                params[Z] /= denom;
            }
        }
    }
}

void monoPhaseTrans(char *seq, int len, float *params, int phase, bool norml, bool local) {
    float counts[6][3] = {{0.0f}};
    int phaseCount[6] = {0};
    int base = len / phase, residue = len % phase;
    int i, p;

    for (i = 0; i < phase; i ++)
        phaseCount[i] += base;

    for (i = 0; i < residue; i ++)
        phaseCount[i] ++;
        
    for (i = 0; i < len; i ++) {
        p = i % phase;

        counts[p][X] += Z_HOT[seq[i]][X];
        counts[p][Y] += Z_HOT[seq[i]][Y];
        counts[p][Z] += Z_HOT[seq[i]][Z];
    }
        
    for (p = 0; p < phase; p ++, params += 3) {
        params[X] = counts[p][X];
        params[Y] = counts[p][Y];
        params[Z] = counts[p][Z];

        if (norml && phaseCount[p] > 0) {
            params[X] /= phaseCount[p];
            params[Y] /= phaseCount[p];
            params[Z] /= phaseCount[p];
        }
    }
}

void diPhaseTrans(char *seq, int len, float *params, int phase, bool norml, bool local) {
    float counts[6][4][4] = {{{0.0f}}};
    int phaseCount[6] = {0};
    int sublen = len - 1;
    int base = sublen / phase, residue = sublen % phase;
    int i, p, b;
    float denom;

    for (i = 0; i < phase; i ++)
        phaseCount[i] += base;

    for (i = 0; i < residue; i ++)
        phaseCount[i] ++;

    for (i = 0; i < sublen; i++) {
        p = i % phase;
        for (b = 0; b < 4; b ++) {
            counts[p][b][X] += ONE_HOT[seq[i]][b] * Z_HOT[seq[i + 1]][X];
            counts[p][b][Y] += ONE_HOT[seq[i]][b] * Z_HOT[seq[i + 1]][Y];
            counts[p][b][Z] += ONE_HOT[seq[i]][b] * Z_HOT[seq[i + 1]][Z];
            counts[p][b][L] += ONE_HOT[seq[i]][b];
        }
    }
        
    for (p = 0; p < phase; p ++)
        for (b = 0; b < 4; b ++, params += 3) {
            params[X] = counts[p][b][X];
            params[Y] = counts[p][b][Y];
            params[Z] = counts[p][b][Z];

            if (norml) {
                denom = local ? counts[p][b][L] : phaseCount[p];

                if (denom > 0) {
                    params[X] /= denom;
                    params[Y] /= denom;
                    params[Z] /= denom;
                }
            }
        }
}

void triPhaseTrans(char *seq, int len, float *params, int phase, bool norml, bool local) {
    float counts[6][4][4][4] = {{{{0.0f}}}};
    int phaseCount[6] = {0};
    int sublen = len - 2;
    int base = sublen / phase, residue = sublen % phase;
    int i, p, s, b;
    float denom;

    for (i = 0; i < phase; i ++)
        phaseCount[i] += base;

    for (i = 0; i < residue; i ++)
        phaseCount[i] ++;

    for (i = 0; i < sublen; i ++) {
        p = i % phase;
        for (s = 0; s < 4; s ++)
        for (b = 0; b < 4; b ++) {
            counts[p][s][b][X] += ONE_HOT[seq[i]][s] * ONE_HOT[seq[i + 1]][b] * Z_HOT[seq[i + 2]][X];
            counts[p][s][b][Y] += ONE_HOT[seq[i]][s] * ONE_HOT[seq[i + 1]][b] * Z_HOT[seq[i + 2]][Y];
            counts[p][s][b][Z] += ONE_HOT[seq[i]][s] * ONE_HOT[seq[i + 1]][b] * Z_HOT[seq[i + 2]][Z];
            counts[p][s][b][L] += ONE_HOT[seq[i]][s] * ONE_HOT[seq[i + 1]][b];
        }
    }

    for (p = 0; p < phase; p ++)
    for (s = 0; s < 4; s ++)
    for (b = 0; b < 4; b ++, params += 3) {
        params[X] = counts[p][s][b][X];
        params[Y] = counts[p][s][b][Y];
        params[Z] = counts[p][s][b][Z];

        if (norml) {
            denom = local ? counts[p][s][b][L] : phaseCount[p];

            if (denom > 0) {
                params[X] /= denom;
                params[Y] /= denom;
                params[Z] /= denom;
            }
        }
    }
}

void quartPhaseTrans(char *seq, int len, float *params, int phase, bool norml, bool local) {
    float counts[6][4][4][4][4] = {{{{{0.0f}}}}};
    int phaseCount[6] = {0};
    int sublen = len - 3;
    int base = sublen / phase, residue = sublen % phase;
    int i, p, s, b, t;
    float denom;

    for (i = 0; i < phase; i ++)
        phaseCount[i] += base;

    for (i = 0; i < residue; i ++)
        phaseCount[i] ++;

    for (i = 0; i < sublen; i ++) {
        p = i % phase;
        for (s = 0; s < 4; s ++)
        for (b = 0; b < 4; b ++)
        for (t = 0; t < 4; t ++) {
            counts[p][s][b][t][X] += ONE_HOT[seq[i]][s] * ONE_HOT[seq[i + 1]][b] * ONE_HOT[seq[i + 2]][t] * Z_HOT[seq[i + 3]][X];
            counts[p][s][b][t][Y] += ONE_HOT[seq[i]][s] * ONE_HOT[seq[i + 1]][b] * ONE_HOT[seq[i + 2]][t] * Z_HOT[seq[i + 3]][Y];
            counts[p][s][b][t][Z] += ONE_HOT[seq[i]][s] * ONE_HOT[seq[i + 1]][b] * ONE_HOT[seq[i + 2]][t] * Z_HOT[seq[i + 3]][Z];
            counts[p][s][b][t][L] += ONE_HOT[seq[i]][s] * ONE_HOT[seq[i + 1]][b] * ONE_HOT[seq[i + 2]][t];
        }
    }

    for (p = 0; p < phase; p ++)
    for (s = 0; s < 4; s ++)
    for (b = 0; b < 4; b ++)
    for (t = 0; t < 4; t ++, params += 3) {
        params[X] = counts[p][s][b][t][X];
        params[Y] = counts[p][s][b][t][Y];
        params[Z] = counts[p][s][b][t][Z];

        if (norml) {
            denom = local ? counts[p][s][b][t][L] : phaseCount[p];

            if (denom > 0) {
                params[X] /= denom;
                params[Y] /= denom;
                params[Z] /= denom;
            }
        }
    }
}

void quintPhaseTrans(char *seq, int len, float *params, int phase, bool norml, bool local) {
    float counts[6][4][4][4][4][4] = {{{{{0.0f}}}}};
    int phaseCount[6] = {0};
    int sublen = len - 4;
    int base = sublen / phase, residue = sublen % phase;
    int i, p, s, b, t, l;
    float denom;

    for (i = 0; i < phase; i ++)
        phaseCount[i] += base;

    for (i = 0; i < residue; i ++)
        phaseCount[i] ++;

    for (i = 0; i < sublen; i ++) {
        p = i % phase;
        for (s = 0; s < 4; s ++)
        for (b = 0; b < 4; b ++)
        for (t = 0; t < 4; t ++)
        for (l = 0; l < 3; l ++) {
            counts[p][s][b][t][l][X] += ONE_HOT[seq[i]][s] * ONE_HOT[seq[i + 1]][b] * ONE_HOT[seq[i + 2]][t] *
                                        ONE_HOT[seq[i + 3]][l] * Z_HOT[seq[i + 4]][X];
            counts[p][s][b][t][l][Y] += ONE_HOT[seq[i]][s] * ONE_HOT[seq[i + 1]][b] * ONE_HOT[seq[i + 2]][t] *
                                        ONE_HOT[seq[i + 3]][l] * Z_HOT[seq[i + 4]][Y];
            counts[p][s][b][t][l][Z] += ONE_HOT[seq[i]][s] * ONE_HOT[seq[i + 1]][b] * ONE_HOT[seq[i + 2]][t] *
                                        ONE_HOT[seq[i + 3]][l] * Z_HOT[seq[i + 4]][Z];
            counts[p][s][b][t][l][L] += ONE_HOT[seq[i]][s] * ONE_HOT[seq[i + 1]][b] * 
                                        ONE_HOT[seq[i + 2]][t] * ONE_HOT[seq[i + 3]][l];
        }
    }

    for (p = 0; p < phase; p ++)
    for (s = 0; s < 4; s ++)
    for (b = 0; b < 4; b ++)
    for (t = 0; t < 4; t ++)
    for (l = 0; l < 4; l ++, params += 3) {
        params[X] = counts[p][s][b][t][l][X];
        params[Y] = counts[p][s][b][t][l][Y];
        params[Z] = counts[p][s][b][t][l][Z];

        if (norml) {
            denom = local ? counts[p][s][b][t][l][L] : phaseCount[p];

            if (denom > 0) {
                params[X] /= denom;
                params[Y] /= denom;
                params[Z] /= denom;
            }
        }
    }
}

void sexPhaseTrans(char *seq, int len, float *params, int phase, bool norml, bool local) {
    float counts[6][4][4][4][4][4][4] = {{{{{{0.0f}}}}}};
    int phaseCount[6] = {0};
    int sublen = len - 5;
    int base = sublen / phase, residue = sublen % phase;
    int i, p, s, b, t, l, m;
    float denom;

    for (i = 0; i < phase; i ++)
        phaseCount[i] += base;

    for (i = 0; i < residue; i ++)
        phaseCount[i] ++;

    for (i = 0; i < sublen; i ++) {
        p = i % phase;
        for (s = 0; s < 4; s ++)
        for (b = 0; b < 4; b ++)
        for (t = 0; t < 4; t ++)
        for (l = 0; l < 4; l ++)
        for (m = 0; m < 4; m ++) {
            counts[p][s][b][t][l][m][X] += ONE_HOT[seq[i + 0]][s] * ONE_HOT[seq[i + 1]][b] * ONE_HOT[seq[i + 2]][t] * 
                                           ONE_HOT[seq[i + 3]][l] * ONE_HOT[seq[i + 4]][m] * Z_HOT[seq[i + 5]][X];
            counts[p][s][b][t][l][m][Y] += ONE_HOT[seq[i + 0]][s] * ONE_HOT[seq[i + 1]][b] * ONE_HOT[seq[i + 2]][t] * 
                                           ONE_HOT[seq[i + 3]][l] * ONE_HOT[seq[i + 4]][m] * Z_HOT[seq[i + 5]][Y];
            counts[p][s][b][t][l][m][Z] += ONE_HOT[seq[i + 0]][s] * ONE_HOT[seq[i + 1]][b] * ONE_HOT[seq[i + 2]][t] * 
                                           ONE_HOT[seq[i + 3]][l] * ONE_HOT[seq[i + 4]][m] * Z_HOT[seq[i + 5]][Z];
            counts[p][s][b][t][l][m][L] += ONE_HOT[seq[i + 0]][s] * ONE_HOT[seq[i + 1]][b] * ONE_HOT[seq[i + 2]][t] * 
                                           ONE_HOT[seq[i + 3]][l] * ONE_HOT[seq[i + 4]][m];
        }
    }

    for (p = 0; p < phase; p ++)
    for (s = 0; s < 4; s ++)
    for (b = 0; b < 4; b ++)
    for (t = 0; t < 4; t ++)
    for (l = 0; l < 4; l ++)
    for (m = 0; m < 4; m ++, params += 3) {
        params[X] = counts[p][s][b][t][l][m][X];
        params[Y] = counts[p][s][b][t][l][m][Y];
        params[Z] = counts[p][s][b][t][l][m][Z];

        if (norml) {
            denom = local ? counts[p][s][b][t][l][m][L] : phaseCount[p];

            if (denom > 0) {
                params[X] /= denom;
                params[Y] /= denom;
                params[Z] /= denom;
            }
        }
    }
}

void (*PhaseTrans[6])(char *, int, float *, int, bool, bool) = {
    monoPhaseTrans,  diPhaseTrans,    triPhaseTrans,
    quartPhaseTrans, quintPhaseTrans, sexPhaseTrans
};

void kPhaseTrans(char *seq, int len, float *params, int k, int phase, bool norml, bool local) {
    if (k < 7) {
        (*PhaseTrans[k - 1])(seq, len, params, phase, norml, local);
    } else {
        float phaseCount[6] = {0};
        int base = (len - k + 1) / phase, residue = (len - k + 1) % phase;
        float weight;
        int i;

        for (i = 0; i < phase; i ++)
            phaseCount[i] += base;

        for (i = 0; i < residue; i ++)
            phaseCount[i] ++;
        
        int num;

        for (i = 0, num = 1; i < k - 1; i ++) num *= 4;
        int size = num * 4;

        float *counts[6];

        for (i = 0; i < phase; i ++)
            counts[i] = new float[size]();
        
        int j, l;

        for (i = 0; i < len - k + 1; i ++) {
            int p = i % phase;
            for (l = 0; l < num; l ++) {
                weight = 1.0F;
                int m = l;
                for (j = 0; j < k - 1; j ++) {
                    weight *= ONE_HOT[seq[i + j]][m % 4];
                    m /= 4;
                }
                m = l * 4;
                counts[p][m + X] = weight * Z_HOT[seq[i + j]][X];
                counts[p][m + Y] = weight * Z_HOT[seq[i + j]][Y];
                counts[p][m + Z] = weight * Z_HOT[seq[i + j]][Z];
                counts[p][m + L] = weight;
            }
        }

        for (i = 0; i < phase; i ++)
            for (j = 0; j < num; j += 4, params += 3) {
                params[X] = counts[i][j + X];
                params[Y] = counts[i][j + Y];
                params[Z] = counts[i][j + Z];

                if (norml) {
                    weight = local ? counts[i][j + L] : phaseCount[i];

                    if (weight > 0) {
                        params[X] /= weight;
                        params[Y] /= weight;
                        params[Z] /= weight;
                    }
                }
            }
            
        for (i = 0; i < phase; i ++)
            delete[] counts[i];
    }
}

float genomeOrderIndex(char *seq, int len) {
    float counts[4] = {0}, s;
    int i, j;

    for (i = 0; i < len; i ++)
        for (j = 0; j < 4; j ++)
            counts[j] += ONE_HOT[seq[i]][j];
    
    for (i = 0, s = 0; i < 4; i ++)
        s += (counts[i] / len * counts[i] / len);

    return s;
}

float ryOrderIndex(char *seq, int len) {
    float counts[2] = {0}, s;
    int i, j;

    for (i = 0; i < len; i ++)
        for (j = 0; j < 2; j ++)
            counts[j] += RY_HOT[seq[i]][j];
    
    for (i = 0, s = 0; i < 2; i ++)
        s += (counts[i] / len * counts[i] / len);

    return s;
}

float mkOrderIndex(char *seq, int len) {
    float counts[2] = {0}, s;
    int i, j;

    for (i = 0; i < len; i ++)
        for (j = 0; j < 2; j ++)
            counts[j] += MK_HOT[seq[i]][j];
    
    for (i = 0, s = 0; i < 2; i ++)
        s += (counts[i] / len * counts[i] / len);

    return s;
}

float wsOrderIndex(char *seq, int len) {
    float counts[2] = {0}, s;
    int i, j;

    for (i = 0; i < len; i ++)
        for (j = 0; j < 2; j ++)
            counts[j] += WS_HOT[seq[i]][j];
    
    for (i = 0, s = 0; i < 2; i ++)
        s += (counts[i] / len * counts[i] / len);

    return s;
}

float atOrderIndex(char *seq, int len) {
    float counts[2] = {0}, s;
    int i, j;

    for (i = 0; i < len; i ++)
        for (j = 0; j < 2; j ++)
            counts[j] += AT_HOT[seq[i]][j];
    
    for (i = 0, s = 0; i < 2; i ++)
        s += (counts[i] / len * counts[i] / len);

    return s;
}

float gcOrderIndex(char *seq, int len) {
    float counts[2] = {0}, s;
    int i, j;

    for (i = 0; i < len; i ++)
        for (j = 0; j < 2; j ++)
            counts[j] += GC_HOT[seq[i]][j];
    
    for (i = 0, s = 0; i < 2; i ++)
        s += (counts[i] / len * counts[i] / len);

    return s;
}

float CpGOrderIndex(char *seq, int len) {
    float counts[2] = {0}, s;
    int i, j, k;

    for (i = 0; i < len; i ++)
        for (j = 0; j < 4; j ++)
            for (k = 0; k < 4; k ++)
                counts[j == 2 && k == 1] += ONE_HOT[seq[i]][j] * ONE_HOT[seq[i + 1]][k];
    
    for (i = 0, s = 0; i < 2; i ++)
        s += (counts[i] / (len - 1) * counts[i] / (len - 1));
    
    return s;
}

void zTrans(char *seq, int len, float **params, int window) {
    float counts[3] = {0.0f};
    int i, j;

    for (i = 0; i < len; i ++)
        for (j = 0; j < 3; j ++) {
            counts[j] += Z_HOT[seq[i]][j];
            params[j][i] = counts[j];
        }

    if (window) for (i = 0; i < 3; i ++)
        meanSmoothing(params[i], len, window);
}

void ryTrans(char *seq, int len, float *params, int window) {
    float counts = 0.0f;
    int i;

    for (i = 0; i < len; i ++) {
        counts += Z_HOT[seq[i]][X];
        params[i] = counts;
    }

    meanSmoothing(params, len, window);
}

void mkTrans(char *seq, int len, float *params, int window) {
    float counts = 0.0f;
    int i;

    for (i = 0; i < len; i ++) {
        counts += Z_HOT[seq[i]][Y];
        params[i] = counts;
    }

    meanSmoothing(params, len, window);
}

void wsTrans(char *seq, int len, float *params, int window) {
    float counts = 0.0f;
    int i;

    for (i = 0; i < len; i ++) {
        counts += Z_HOT[seq[i]][Z];
        params[i] = counts;
    }

    meanSmoothing(params, len, window);
}

void atTrans(char *seq, int len, float *params, int window) {
    float counts[4] = {0.0f};
    int i, j;

    for (i = 0; i < len; i ++, params ++) {
        for (j = 0; j < 4; j += 3)
            counts[j] += ONE_HOT[seq[i]][j];

        *params = counts[0] - counts[3];
    }

    meanSmoothing(params - len, len, window);
}

void gcTrans(char *seq, int len, float *params, int window) {
    float counts[4] = {0.0f};
    int i, j;

    for (i = 0; i < len; i ++, params ++) {
        for (j = 1; j < 3; j ++)
            counts[j] += ONE_HOT[seq[i]][j];

        *params = counts[1] - counts[2];
    }

    meanSmoothing(params - len, len, window);
}

float xPrimeTrans(char *seq, int len, float *params, int window) {
    float counts = 0.0f;
    double ySum, xySum, kp;
    int i;

    for (i = 0; i < len; i ++) {
        counts += Z_HOT[seq[i]][X];
        params[i] = counts;
    }
    
    if (len <= MAX_FIT_LEN) {
        for (i = 0, ySum = 0, xySum = 0; i < len; i ++)
            ySum += params[i], xySum += params[i] * i;

        kp = (xySum / (len - 1) - ySum / 2) / len / (len + 1) * 12;
    } else kp = ((double) (params[len - 1] - params[0])) / (len - 1);
    
    for (i = 1; i < len; i++)
        params[i] -= ((float) kp) * i;
    
    meanSmoothing(params, len, window);
    
    return (float) kp;
}

float yPrimeTrans(char *seq, int len, float *params, int window) {
    float counts = 0.0f;
    double ySum, xySum, kp;
    int i;

    for (i = 0; i < len; i ++) {
        counts += Z_HOT[seq[i]][Y];
        params[i] = counts;
    }
    
    if (len <= MAX_FIT_LEN) {
        for (i = 0, ySum = 0, xySum = 0; i < len; i ++)
            ySum += params[i], xySum += i * params[i];

        kp = (xySum / (len - 1) - ySum / 2) / len / (len + 1) * 12;
    } else kp = ((double) (params[len - 1] - params[0])) / (len - 1);
    
    for (i = 1; i < len; i++)
        params[i] -= ((float) kp) * i;
    
    meanSmoothing(params, len, window);
    
    return (float) kp;
}

float zPrimeTrans(char *seq, int len, float *params, int window) {
    float counts = 0.0f;
    double ySum, xySum, kp;
    int i;

    for (i = 0; i < len; i ++) {
        counts += Z_HOT[seq[i]][Z];
        params[i] = counts;
    }

    if (len <= MAX_FIT_LEN) {
        for (i = 0, ySum = 0, xySum = 0; i < len; i ++)
            ySum += params[i], xySum += i * params[i];

        kp = (xySum / (len - 1) - ySum / 2) / len / (len + 1) * 12;
    } else kp = ((double) (params[len - 1] - params[0])) / (len - 1);
    
    for (i = 1; i < len; i++)
        params[i] -= ((float) kp) * i;
    
    meanSmoothing(params, len, window);
    
    return (float) kp;
}

float atPrimeTrans(char *seq, int len, float *params, int window) {
    float counts[4] = { 0.0f };
    double ySum, xySum, kp;
    int i, j;

    for (i = 0; i < len; i ++) {
        for (j = 0; j < 4; j += 3)
            counts[j] += ONE_HOT[seq[i]][j];

        params[i] = counts[0] - counts[3];
    }

    if (len <= MAX_FIT_LEN) {
        for (i = 0, ySum = 0, xySum = 0; i < len; i ++)
            ySum += params[i], xySum += i * params[i];

        kp = (xySum / (len - 1) - ySum / 2) / len / (len + 1) * 12;
    } else kp = ((double) (params[len - 1] - params[0])) / (len - 1);
    
    for (i = 1; i < len; i++)
        params[i] -= ((float) kp) * i;
    
    meanSmoothing(params, len, window);
    
    return (float) kp;
}

float gcPrimeTrans(char *seq, int len, float *params, int window) {
    float counts[4] = { 0.0f };
    double ySum, xySum, kp;
    int i, j;

    for (i = 0; i < len; i ++) {
        for (j = 1; j < 3; j ++)
            counts[j] += ONE_HOT[seq[i]][j];

        params[i] = counts[1] - counts[2];
    }

    if (len <= MAX_FIT_LEN) {
        for (i = 0, ySum = 0, xySum = 0; i < len; i ++)
            ySum += params[i], xySum += i * params[i];

        kp = (xySum / (len - 1) - ySum / 2) / len / (len + 1) * 12;
    } else kp = ((double) (params[len - 1] - params[0])) / (len - 1);
    
    for (i = 1; i < len; i++)
        params[i] -= ((float) kp) * i;
    
    meanSmoothing(params, len, window);
    
    return (float) kp;
}

float CpGPrimeTrans(char *seq, int len, float *params, int window) {
    float counts[2] = {0};
    double ySum, xySum, kp;
    int i, j, k;

    for (i = 0; i < len - 1; i ++) {
        for (j = 0; j < 4; j ++)
            for (k = 0; k < 4; k ++)
                counts[j == 2 && k == 1] += ONE_HOT[seq[i]][j] * ONE_HOT[seq[i + 1]][k];
        
        params[i] = counts[1] - counts[0];
    }

    params[i] = params[i - 1];

    if (len <= MAX_FIT_LEN) {
        for (i = 0, ySum = 0, xySum = 0; i < len; i ++)
            ySum += params[i], xySum += i * params[i];

            kp = (xySum / (len - 1) - ySum / 2) / len / (len + 1) * 12;
    } else kp = ((double) (params[len - 1] - params[0])) / (len - 1);
    
    for (i = 1; i < len; i ++)
        params[i] -= ((float) kp) * i;
    
    meanSmoothing(params, len, window);

    return (float) kp;
}

int genomeDeltaSTrans(char *seq, int len, float *params, int window, float &max) {
    float p[4] = {0}, q[4] = {0}, dif[4] = {0}, s;
    int i, j, maxPoint = -1;

    for (i = 0; i < len; i ++)
        for (j = 0; j < 4; j ++)
            q[j] += ONE_HOT[seq[i]][j];
    
    for (i = 0; i < len - 1; i ++) {
        for (j = 0, s = 0; j < 4; j ++) {
            p[j] += ONE_HOT[seq[i]][j];
            q[j] -= ONE_HOT[seq[i]][j];
            dif[j] = p[j] / (i + 1) - q[j] / (len - i - 1);
            s += dif[j] * dif[j];
        }

        params[i] = (s * (i + 1) / len * (len - i - 1));
    }

    params[len - 1] = 0.0;

    meanSmoothing(params, len, window);

    for (i = 0, max = -1; i < len; i ++)
        if (params[i] > max)
            max = params[i], maxPoint = i;
    
    return maxPoint;
}

int ryDeltaSTrans(char *seq, int len, float *params, int window, float &max) {
    float p[2] = {0}, q[2] = {0}, dif[2] = {0}, s;
    int i, j, maxPoint = -1;

    for (i = 0; i < len; i ++)
        for (j = 0; j < 2; j ++)
            q[j] += RY_HOT[seq[i]][j];
    
    for (i = 0; i < len - 1; i ++) {
        for (j = 0, s = 0; j < 2; j ++) {
            p[j] += RY_HOT[seq[i]][j];
            q[j] -= RY_HOT[seq[i]][j];
            dif[j] = p[j] / (i + 1) - q[j] / (len - i - 1);
            s += dif[j] * dif[j];
        }

        params[i] = (s * (i + 1) / len * (len - i - 1));
    }

    params[len - 1] = 0;

    meanSmoothing(params, len, window);

    for (i = 0, max = -1; i < len; i ++)
        if (params[i] > max)
            max = params[i], maxPoint = i;
    
    return maxPoint;
}

int mkDeltaSTrans(char *seq, int len, float *params, int window, float &max) {
    float p[2] = {0}, q[2] = {0}, dif[2] = {0}, s;
    int i, j, maxPoint = -1;

    for (i = 0; i < len; i ++)
        for (j = 0; j < 2; j ++)
            q[j] += MK_HOT[seq[i]][j];
    
    for (i = 0; i < len - 1; i ++) {
        for (j = 0, s = 0; j < 2; j ++) {
            p[j] += MK_HOT[seq[i]][j];
            q[j] -= MK_HOT[seq[i]][j];
            dif[j] = p[j] / (i + 1) - q[j] / (len - i - 1);
            s += dif[j] * dif[j];
        }

        params[i] = (s * (i + 1) / len * (len - i - 1));
    }

    params[len - 1] = 0;

    meanSmoothing(params, len, window);

    for (i = 0, max = -1; i < len; i ++)
        if (params[i] > max)
            max = params[i], maxPoint = i;
    
    return maxPoint;
}

int wsDeltaSTrans(char *seq, int len, float *params, int window, float &max) {
    float p[2] = {0}, q[2] = {0}, dif[2] = {0}, s;
    int i, j, maxPoint = -1;

    for (i = 0; i < len; i ++)
        for (j = 0; j < 2; j ++)
            q[j] += WS_HOT[seq[i]][j];
    
    for (i = 0; i < len - 1; i ++) {
        for (j = 0, s = 0; j < 2; j ++) {
            p[j] += WS_HOT[seq[i]][j];
            q[j] -= WS_HOT[seq[i]][j];
            dif[j] = p[j] / (i + 1) - q[j] / (len - i - 1);
            s += dif[j] * dif[j];
        }

        params[i] = (s * (i + 1) / len * (len - i - 1));
    }

    params[len - 1] = 0;

    meanSmoothing(params, len, window);

    for (i = 0, max = -1; i < len; i ++)
        if (params[i] > max)
            max = params[i], maxPoint = i;
    
    return maxPoint;
}

int atDeltaSTrans(char *seq, int len, float *params, int window, float &max) {
    float p[2] = {0}, q[2] = {0}, dif[2] = {0}, s, sp, sq;
    int i, maxPoint = -1;

    for (i = 0; i < len; i ++) {
        q[0] += AT_HOT[seq[i]][0];
        q[1] += AT_HOT[seq[i]][1];
    }

    const float ts = q[0] + q[1] + 1E-3F;
    
    for (i = 0; i < len - 1; i ++) {
        p[0] += AT_HOT[seq[i]][0];
        q[0] -= AT_HOT[seq[i]][0];
        p[1] += AT_HOT[seq[i]][1];
        q[1] -= AT_HOT[seq[i]][1];

        sp = p[0] + p[1] + 1E-3F;
        sq = q[0] + q[1] + 1E-3F;

        dif[0] = p[0] / sp - q[0] / sq;
        dif[1] = p[1] / sp - q[1] / sq;
        
        s = dif[0] * dif[0] + dif[1] * dif[1];

        params[i] = (s * sp / ts * sq);
    }

    params[len - 1] = 0;

    meanSmoothing(params, len, window);

    for (i = 0, max = -1; i < len; i ++)
        if (params[i] > max)
            max = params[i], maxPoint = i;
    
    return maxPoint;
}

int gcDeltaSTrans(char *seq, int len, float *params, int window, float &max) {
    float p[2] = {0}, q[2] = {0}, dif[2] = {0}, s, sp, sq;
    int i, maxPoint = -1;

    for (i = 0; i < len; i ++) {
        q[0] += GC_HOT[seq[i]][0];
        q[1] += GC_HOT[seq[i]][1];
    }

    const float ts = q[0] + q[1] + 1E-3F;
    
    for (i = 0; i < len - 1; i ++) {
        p[0] += GC_HOT[seq[i]][0];
        q[0] -= GC_HOT[seq[i]][0];
        p[1] += GC_HOT[seq[i]][1];
        q[1] -= GC_HOT[seq[i]][1];

        sp = p[0] + p[1] + 1E-3F;
        sq = q[0] + q[1] + 1E-3F;

        dif[0] = p[0] / sp - q[0] / sq;
        dif[1] = p[1] / sp - q[1] / sq;
        
        s = dif[0] * dif[0] + dif[1] * dif[1];

        params[i] = (s * sp / ts * sq);
    }

    params[len - 1] = 0;

    meanSmoothing(params, len, window);

    for (i = 0, max = -1; i < len; i ++)
        if (params[i] > max)
            max = params[i], maxPoint = i;
    
    return maxPoint;
}

int CpGDeltaSTrans(char *seq, int len, float *params, int window, float &max) {
    float p[2] = {0}, q[2] = {0}, dif[2] = {0}, s;
    int i, j, k, maxPoint = -1;

    for (i = 0; i < len; i ++)
        for (j = 0; j < 4; j ++)
            for (k = 0; k < 4; k ++)
                q[j == 2 && k == 1] += ONE_HOT[seq[i]][j] * ONE_HOT[seq[i + 1]][k];
    
    for (i = 0; i < len - 1; i ++) {
        for (j = 0; j < 4; j ++)
            for (k = 0; k < 4; k ++) {
                p[j == 2 && k == 1] += ONE_HOT[seq[i]][j] * ONE_HOT[seq[i + 1]][k];
                q[j == 2 && k == 1] -= ONE_HOT[seq[i]][j] * ONE_HOT[seq[i + 1]][k];
            }
        
        for (j = 0, s = 0; j < 2; j ++) {
            dif[j] = p[j] / (i + 1) - q[j] / (len - i - 1);
            s += dif[j] * dif[j];
        }

        params[i] = (s * (i + 1) / len * (len - i - 1));
    }

    params[len - 1] = 0;

    meanSmoothing(params, len, window);

    for (i = 0, max = -1; i < len; i ++)
        if (params[i] > max)
            max = params[i], maxPoint = i;
    
    return maxPoint;
}

void tetrahedron(char *seq, int len, float **params) {
    for (int i = 0; i < 3; i ++)
        for (int j = 0; j < len; j ++)
            params[i][j] = Z_HOT[seq[j]][i];
}

void WSSkew(char *seq, int len, int window, float *params) {
    float countW = 0.0F, countS = 0.0F;
    int half = (int) (window / 2);
    
    int i;
    for (i = 0; i < half - 1; i ++) {
        countS += WS_HOT[seq[i]][0];
        countW += WS_HOT[seq[i]][1];
    }

    int s, e;
    for (i = 0; i < len; i ++) {
        s = (i - half) > 0 ? (i - half) : 0;
        e = (i + half - 1) < len ? (i + half - 1) : len;

        if (s > 0) {
            countS -= WS_HOT[seq[s - 1]][0];
            countW -= WS_HOT[seq[s - 1]][1];
        }

        if (e < len) {
            countS += WS_HOT[seq[e]][0];
            countW += WS_HOT[seq[e]][1];
        }

        params[i] = (countW - countS) / window;
    }
}

void ATSkew(char *seq, int len, int window, float *params) {
    float countA = 0.0F, countT = 0.0F;
    int half = (int) (window / 2);

    int i;
    for (i = 0; i < half - 1; i ++) {
        countA += AT_HOT[seq[i]][0];
        countT += AT_HOT[seq[i]][1];
    }

    int s, e;
    for (i = 0; i < len; i ++) {
        s = (i - half) > 0 ? (i - half) : 0;
        e = (i + half - 1) < len ? (i + half - 1) : len;

        if (s > 0) {
            countA -= AT_HOT[seq[s - 1]][0];
            countT -= AT_HOT[seq[s - 1]][1];
        }

        if (e < len) {
            countA += AT_HOT[seq[e]][0];
            countT += AT_HOT[seq[e]][1];
        }

        float sum = countA + countT;
        params[i] = sum == 0.0F ? 0.0F : ((countA - countT) / sum);
    }
}

void GCSkew(char *seq, int len, int window, float *params) {
    float countG = 0.0F, countC = 0.0F;
    int half = (int) (window / 2);

    int i;
    for (i = 0; i < half - 1; i ++) {
        countG += GC_HOT[seq[i]][0];
        countC += GC_HOT[seq[i]][1];
    }

    int s, e;
    for (i = 0; i < len; i ++) {
        s = (i - half) > 0 ? (i - half) : 0;
        e = (i + half - 1) < len ? (i + half - 1) : len;

        if (s > 0) {
            countG -= GC_HOT[seq[s - 1]][0];
            countC -= GC_HOT[seq[s - 1]][1];
        }

        if (e < len) {
            countG += GC_HOT[seq[e]][0];
            countC += GC_HOT[seq[e]][1];
        }
        
        float sum = countG + countC;
        params[i] = sum == 0.0F ? 0.0F : ((countG - countC) / sum);
    }
}

void ATFraction(char *seq, int len, int window, float *params) {
    for (int i = 0; i < len; i ++)
        params[i] = WS_HOT[seq[i]][1];
    meanSmoothing(params, len, window);
}

void GCFraction(char *seq, int len, int window, float *params) {
    for (int i = 0; i < len; i ++)
        params[i] = WS_HOT[seq[i]][0];
    meanSmoothing(params, len, window);
}

float gcFraction(char *pseq, int len) {
    float gcCount = 0.0F;
    for (int i = 0; i < len; i ++)
        gcCount += WS_HOT[pseq[i]][0];
    return (gcCount / len);
}

#ifdef __cplusplus
}
#endif
