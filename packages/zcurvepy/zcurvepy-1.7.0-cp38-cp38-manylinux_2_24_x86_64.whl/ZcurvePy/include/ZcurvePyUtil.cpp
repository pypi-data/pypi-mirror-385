/* * * * * * * * * * * * * * * * * * * *
 *  ZcurvePy Source Code               *
 *                                     *
 *  @author      Zhang ZT, Gao F       *
 *  @copyright   Copyright 2025 TUBIC  *
 *  @date        2025-09-09            *
 *  @version     1.7.0                 *
 * * * * * * * * * * * * * * * * * * * */
#include"ZcurvePyUtil.h"

/* Complement base map */
static Py_UCS4 COMP_MAP[] = {
    'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 
    'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 
    'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 
    'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 
    'N',
  /* A    B    C    D    E    F    G    H    I    J    K    L    M    N    O    P */
    'T', 'V', 'G', 'H', 'N', 'N', 'C', 'D', 'N', 'N', 'M', 'N', 'K', 'N', 'N', 'N',
  /* Q    R    S    T    U    V    W    X    Y    Z */
    'N', 'Y', 'W', 'A', 'A', 'B', 'S', 'N', 'R', 'T', 'N', 'N', 'N', 'N', 'N', 'N',
  /* a    b    c    d    e    f    g    h    i    j    k    l    m    n    o    p */
    't', 'v', 'g', 'h', 'n', 'n', 'c', 'd', 'n', 'n', 'm', 'n', 'k', 'n', 'n', 'n',
  /* q    r    s    t    u    v    w    x    y    z */
    'n', 'y', 'w', 'a', 'a', 'b', 's', 'n', 'r', 't'
};

/* Default start codons */
static const char *DEFAULT_START_CODONS[] = {"ATG", "TTG", "GTG", nullptr};
/* Default stop codons */
static const char *DEFAULT_STOP_CODONS[] = {"TAA", "TAG", "TGA", nullptr};
/* Default ORF type */
static const char DEFAULT_ORF_TYPE[] = "ORF";

/* Constructor of RegionNode */
RegionNode::RegionNode(int start, int end) {
    this->next = nullptr;
    this->start = start;
    this->end = end;
}

/* ORF Python Object */
/* PASS 2025-07-08 */
typedef struct {
    PyObject_HEAD
    char *hostname;  // host genome name
    int *starts;  // possible ORF start codon positions
    int *startTypes; // possible start codon types
    int numStarts;  // number of possible ORF start codon positions
    int end;  // end position (stop codon)
    char strand;  // strand of the ORF (+/-)
    int frame;  // reading frame
    float gcFrac; // G+C fraction
} OrfObject;

/* Orf.__dealloc__ */
static void OrfObject_dealloc(OrfObject *self) {
    delete[] self->hostname;
    delete[] self->starts;
    delete[] self->startTypes;
    self->hostname = nullptr;
    self->starts = nullptr;
    self->startTypes = nullptr;
    Py_TYPE(self)->tp_free((PyObject *)self);
}

/* Orf.__len__ */
static Py_ssize_t OrfObject_len(OrfObject *self) {
    /* PASS 2025-07-19 */
    int length = std::abs(self->end - self->starts[0]);
    return ((Py_ssize_t) length);
}

/* Orf.__repr__ */
static PyObject *OrfObject_repr(OrfObject *self) {
    PyObject *reprseq = PyUnicode_FromFormat(
        "OrfObject(hostname='%s', start=%d, end=%d, strand='%c', frame=%d)",
        self->hostname, self->starts[0], self->end, self->strand, self->frame);
    return reprseq;
}
/* Orf.extract */
/* 
 * Extract sequence from the host genome 
 * 
 * @param seq  Genome sequence (str)
 * @return  Orf Sequence (str)
 */
static PyObject *OrfObject_extract(OrfObject *self, PyObject *args, PyObject *kw) {
    /* PASS 2025-07-19 */
    static char *kwlist[] = {"seq", nullptr};
    PyObject *PyStr = nullptr;

    if (!PyArg_ParseTupleAndKeywords(args, kw, "U", kwlist, &PyStr)) {
        return NULL;
    }

    int length = (int) PyUnicode_GetLength(PyStr);
    int realStart = std::min(self->starts[0], self->end);
    int realEnd = std::max(self->starts[0], self->end);

    if (length < realEnd) {
        PyErr_SetString(PyExc_IndexError, "sequence ended prematurely");
        return NULL;
    }

    if (self->strand == '+') {
        return PyUnicode_Substring(PyStr, realStart, realEnd);
    } else {
        int sublen = realEnd - realStart;

        PyObject *result = PyUnicode_New(sublen, 127);
        if (!result) return NULL;

        for (int i = 0, j = realEnd - 1; i < sublen; i++, j--) {
            Py_UCS4 ch = PyUnicode_ReadChar(PyStr, j);
            PyUnicode_WriteChar(result, i, COMP_MAP[ch]);
        }

        return result;
    }
}
/* Orf.to_SeqFeature */
/*
 * Convert to Bio.SeqFeature.SeqFeature
 *
 * @param type  the type of SeqFeature
 * @return SeqFeature  object
 */
static PyObject *OrfObject_toSeqFeature(OrfObject *self, PyObject *args, PyObject *kw) {
    static char *kwlist[] = {"type", nullptr};
    char *strtype = nullptr;

    if (!PyArg_ParseTupleAndKeywords(args, kw, "|s", kwlist, &strtype)) {
        return NULL;
    }

    if (!strtype) {
        strtype = (char *) DEFAULT_ORF_TYPE;
    }

    long realStart = (long) std::min(self->starts[0], self->end);
    long realEnd = (long) std::max(self->starts[0], self->end);
    long strand = (long) self->strand == '+' ? 1 : -1;

    PyObject* locationArgs = PyTuple_New(3);

    if (!locationArgs) {
        return NULL;
    }

    PyTuple_SET_ITEM(locationArgs, 0, PyLong_FromLong(realStart)); 
    PyTuple_SET_ITEM(locationArgs, 1, PyLong_FromLong(realEnd)); 
    PyTuple_SET_ITEM(locationArgs, 2, PyLong_FromLong(strand));

    PyObject* location = PyObject_CallObject(FeatureLocation, locationArgs);
    Py_DECREF(locationArgs);

    if (!location) {
        PyErr_SetString(PyExc_MemoryError, "failed to create new FeatureLocation object");
        return NULL;
    }

    PyObject* featureArgs = PyTuple_New(2);

    if (!featureArgs) {
        Py_DECREF(location);
        return NULL;
    }

    PyObject* typeObj = PyUnicode_FromString(strtype);

    PyTuple_SET_ITEM(featureArgs, 0, location);
    PyTuple_SET_ITEM(featureArgs, 1, typeObj);

    PyObject* seqFeature = PyObject_CallObject(SeqFeature, featureArgs);

    Py_DECREF(featureArgs);

    return seqFeature;
}
/* Get start codon position by index */
static PyObject *OrfObject_start(OrfObject *self, PyObject *args, PyObject *kw) {
    static char *kwlist[] = {"index", nullptr};
    int index = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kw, "|i", kwlist, &index)) {
        return NULL;
    }

    if (index >= self->numStarts) {
        PyErr_SetString(PyExc_IndexError, "index out of range");
        return NULL;
    }

    return PyLong_FromLong((long) self->starts[index]);
}
/* Get start codon type by index */
static PyObject *OrfObject_startType(OrfObject *self, PyObject *args, PyObject *kw) {
    static char *kwlist[] = { "index", nullptr };
    int index = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kw, "|i", kwlist, &index)) {
        return NULL;
    }

    if (index >= self->numStarts) {
        PyErr_SetString(PyExc_IndexError, "index out of range");
        return NULL;
    }

    return PyLong_FromLong((long) self->startTypes[index]);
}
/* Extract upstream sequence */
static PyObject *OrfObject_upstream(OrfObject *self, PyObject *args, PyObject *kw) {
    static char *kwlist[] = { "seq", "index", "start", "end", nullptr };
    PyObject *PyStr = nullptr;
    int index = 0;
    int start = -90;
    int end = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kw, "U|iii", kwlist, &PyStr, &index, &start, &end)) {
        return NULL;
    }

    if (start >= end) {
        PyErr_SetString(PyExc_IndexError, "end should be larger than start");
        return NULL;
    }

    if (index >= self->numStarts) return PyUnicode_FromString("");

    int seqlen = (int) PyUnicode_GetLength(PyStr);
    int startPos = self->starts[index];

    PyObject *upstream = PyUnicode_New(end - start, 127);
    Py_UCS4 ch;
    int pos;

    if (self->strand == '+') {
        for (int i = start; i < end; i ++) {
            pos = (startPos + i) % seqlen;
            if (pos < 0) pos += seqlen;
            ch = PyUnicode_ReadChar(PyStr, pos);
            PyUnicode_WriteChar(upstream, i - start, ch);
        }
    } else {
        for (int i = start; i < end; i ++) {
            pos = (startPos-i-1) % seqlen;
            if (pos < 0) pos += seqlen;
            ch = PyUnicode_ReadChar(PyStr, pos);
            PyUnicode_WriteChar(upstream, i - start, COMP_MAP[ch]);
        }
    }
    
    return upstream;
}
/* Extract downstream sequence */
static PyObject *OrfObject_downstream(OrfObject *self, PyObject *args, PyObject *kw) {
    static char *kwlist[] = { "seq", "start", "end", nullptr };
    PyObject *PyStr = nullptr;
    int start = 0;
    int end = 90;

    if (!PyArg_ParseTupleAndKeywords(args, kw, "U|ii", kwlist, &PyStr, &start, &end)) {
        return NULL;
    }
    
    if (start >= end) {
        PyErr_SetString(PyExc_IndexError, "end should be larger than start");
        return NULL;
    }

    int seqlen = (int) PyUnicode_GetLength(PyStr);
    PyObject *downstream = PyUnicode_New(end - start, 127);
    Py_UCS4 ch;
    int pos;

    if (self->strand == '+') {
        for (int i = start; i < end; i ++) {
            pos = (self->end + i) % seqlen;
            if (pos < 0) pos += seqlen;
            ch = PyUnicode_ReadChar(PyStr, pos);
            PyUnicode_WriteChar(downstream, i - start, ch);
        }
    } else {
        for (int i = start; i < end; i ++) {
            pos = (self->end-i-1) % seqlen;
            if (pos < 0) pos += seqlen;
            ch = PyUnicode_ReadChar(PyStr, pos);
            PyUnicode_WriteChar(downstream, i - start, COMP_MAP[ch]);
        }
    }
    
    return downstream;
}
static PyObject *OrfObject_subOrf(OrfObject *self, PyObject *args, PyObject *kw) {
    static char *kwlist[] = { "index", nullptr };
    int index;

    if (!PyArg_ParseTupleAndKeywords(args, kw, "i", kwlist, &index)) {
        return NULL;
    }

    OrfObject *subOrf = PyObject_New(OrfObject, &OrfType);

    if (!subOrf) {
        PyErr_SetString(PyExc_MemoryError, "cannot create new Orf object");
        return NULL;
    }

    int subNumStarts = self->numStarts - index;

    subOrf->hostname = new char[(int)strlen(self->hostname)+1];
    subOrf->starts = new int[subNumStarts];
    subOrf->startTypes = new int[subNumStarts];
    subOrf->numStarts = subNumStarts;
    subOrf->end = self->end;
    subOrf->strand = self->strand;
    subOrf->frame = self->frame;

    strcpy(subOrf->hostname, self->hostname);
    memcpy(subOrf->starts, self->starts + index, sizeof(int) * subNumStarts);
    memcpy(subOrf->startTypes, self->startTypes + index, sizeof(int) * subNumStarts);

    return (PyObject *) subOrf;
}
/* tp_sq_methods */
static PySequenceMethods OrfObject_sequence_methods = {
    (lenfunc) OrfObject_len
};
/* tp_members */
static PyMemberDef OrfObject_members[] = {
    {"hostname", T_STRING, offsetof(OrfObject, hostname), READONLY, NULL},
    {"num_starts", T_INT, offsetof(OrfObject, numStarts), READONLY, NULL},
    {"end", T_INT, offsetof(OrfObject, end), READONLY, NULL},
    {"strand", T_CHAR, offsetof(OrfObject, strand), READONLY, NULL},
    {"frame", T_INT, offsetof(OrfObject, frame), READONLY, NULL},
    {"gc_frac", T_FLOAT, offsetof(OrfObject, gcFrac), READONLY, NULL},
    {NULL, NULL, 0, NULL, NULL}  // Sentinel
};

/* tp_methods */
static PyMethodDef OrfObject_methods[] = {
    {"start", (PyCFunction) OrfObject_start, METH_VARARGS|METH_KEYWORDS, NULL},
    {"start_type", (PyCFunction) OrfObject_startType, METH_VARARGS|METH_KEYWORDS, NULL},
    {"suborf", (PyCFunction) OrfObject_subOrf, METH_VARARGS|METH_KEYWORDS, NULL},
    {"extract", (PyCFunction) OrfObject_extract, METH_VARARGS|METH_KEYWORDS, NULL},
    {"upstream", (PyCFunction) OrfObject_upstream, METH_VARARGS|METH_KEYWORDS, NULL},
    {"downstream", (PyCFunction) OrfObject_downstream, METH_VARARGS|METH_KEYWORDS, NULL},
    {"to_SeqFeature", (PyCFunction) OrfObject_toSeqFeature, METH_VARARGS|METH_KEYWORDS, NULL},
    {NULL, 0, NULL, NULL}
};

/* Python Type Object Orf*/
PyTypeObject OrfType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_ZcurvePy.Orf",
    sizeof(OrfObject),
    0,
    (destructor) OrfObject_dealloc,
    NULL, /* tp_vectorcall_offset */
    NULL, /* tp_getattr */
    NULL, /* tp_setattr */
    NULL, /* tp_as_async */
    (reprfunc) OrfObject_repr,
    NULL, /* tp_nb_methods */
    &OrfObject_sequence_methods,
    NULL, /* tp_mp_methods */
    NULL, /* tp_hash */
    NULL, /* tp_call */
    NULL, /* tp_str */
    NULL, /* tp_getattro */
    NULL, /* tp_setattro */
    NULL, /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    NULL, /* tp_doc */
    NULL, /* tp_traverse */
    NULL, /* tp_clear */
    NULL, /* tprichcmpfunc*/
    NULL, /* tp_weaklistoffset */
    NULL, /* tp_iter */
    NULL, /* tp_iternext */
    OrfObject_methods,
    OrfObject_members,
    NULL, /* tp_getset */
    NULL, /* tp_base */
    NULL, /* tp_dict */
    NULL, /* tp_descr_get */
    NULL, /* tp_descr_set */
    NULL, /* tp_dictoffset */
    (initproc) NULL,
    NULL, /* tp_alloc */
    NULL, /* tp_new */
};
/* Check if the codon match any of the list */
/* 
 * @param pstr      source codon
 * @param codonList target codons
 * 
 * @return int      start type
 */
static int matchCodon(const char *pstr, char **codonList) {
    for (int startType = 0; *codonList; startType ++) {
        if (!strncmp(pstr, *codonList, 3)) {
            return startType;
        }
        codonList ++;
    }
    return -1;
}
/* Convert Python str list to C++ char *[] */
/* 
 * @param PyCodons   codon types as Python codon list
 * @param cppCodons  codon types as C++ char *[]
 * @param defaultCodons  default codon types
 * 
 * @return parsed successfully or not
 */
static bool parseCodons(PyObject *PyCodons, char **cppCodons, const char **defaultCodons, bool &shouldFree) {
    if (PyCodons) {
        int numTypes = (int) PySequence_Length(PyCodons);
        
        // PyCodons must be Python list
        if (numTypes == -1) {
            return false;
        }

        // the length of array will not be returned while using nullptr as end.
        cppCodons[numTypes] = nullptr;

        for (int i = 0; i < numTypes; i++) {
            PyObject *type = PySequence_GetItem(PyCodons, i);

            // item must be str
            if (!PyUnicode_Check(type)) {
                Py_DECREF(type);
                return false;
            }
            
            const char *str = PyUnicode_AsUTF8(type);
            cppCodons[i] = strdup(str);
            shouldFree = true;
            Py_DECREF(type);
        }
    } else {
        // If the user provides nothing, use default values
        memcpy(cppCodons, defaultCodons, 4 * sizeof(char *));
    }

    return true;
}
/* Create OrfObject and save information */
/*
 * @param name    Name of the genome
 * @param starts  Positions of alter start codons
 * @param numStarts  Number of alter start codons
 * @param end     Position of end start codon
 * @param negStrand  If on the negative strand
 * @param length  Total length of genome
 * @param frame   Reading frame
 * @param buff    Temp storage of OrfObject
 * 
 * @return  If saved successfully
 */
static bool saveOrf(
    const char *name, int *starts, int numStarts, int *startTypes, int end, 
    bool negStrand, int length, int frame, float gcFrac, std::vector<OrfObject *> &buff
) {
    OrfObject *newOrf = PyObject_New(OrfObject, &OrfType);

    if (!newOrf) {
        return false;
    }

    newOrf->hostname = new char[strlen(name) + 1];
    newOrf->numStarts = numStarts;
    newOrf->starts = starts;
    newOrf->startTypes = startTypes;
    newOrf->end = negStrand ? length - end : end;
    newOrf->strand = negStrand ? '-' : '+';
    newOrf->frame = frame;
    newOrf->gcFrac = gcFrac;

    if (negStrand) for (int i = 0; i < numStarts; i ++)
        newOrf->starts[i] = length - newOrf->starts[i];
    
    strcpy(newOrf->hostname, name);
    buff.push_back(newOrf);

    return true;
}
/* Find island regions by a sliding window calculating PCC. */
/*
 * @param values y-values of 2D curves.
 * @param length Length of y-value array.
 * @param locs   Locations of found islands.
 * @param window Window size of the algorithm.
 * @param minPCC Threshold of PCC.
 * 
 * @return count of islands.
 */
static int findIsland(
    const float *values, 
    const int length,
    const int window,
    const float minPCC,
    RegionNode *root
) {
    // Window size-related constants
    const double lxx = sqrt(window);
    const int maxIndex = window - 1;
    // Values for PCC calculation
    double xySum = 0.0, ySum = 0.0, y2Sum = 0.0;

    // Initialization of sliding window
    for (int i = 0; i < window; i ++) {
        xySum += i * (double) values[i];
        ySum += (double) values[i];
        y2Sum += (double) values[i] * values[i]; 
    }

    // Initialization of PCC calculating
    double lxy = xySum / maxIndex - ySum / 2;
    double lyy = sqrt(y2Sum - ySum * ySum / window);
    double pcc = PCC_CONSTANT * lxy / lyy / lxx;
    
    bool recording = pcc > minPCC; // Recording switch
    // The start point of a new island and count of islands
    int start = 0, count = 0;

    RegionNode *nextNode = root;
    const int stop = length - window;
    for (int winStart = 0, winEnd = window; winStart < stop; winStart ++, winEnd ++) {
        // Update the sum values of the next sliding window
        ySum += values[winEnd] - values[winStart];
        xySum += window * values[winEnd] - ySum;
        y2Sum += values[winEnd] * values[winEnd] - values[winStart] * values[winStart];

        // Calculate the PCC value of the next sliding window
        lxy = xySum / maxIndex - ySum / 2;
        lyy = sqrt(y2Sum - ySum * ySum / window);
        pcc = PCC_CONSTANT * lxy / lyy / lxx;

        if (recording && pcc <= minPCC) {
            nextNode->next = new RegionNode(start, winEnd + 1);
            nextNode = nextNode->next;
            recording = false;
            count ++;
        } else if (!recording && pcc > minPCC) {
            start = winStart + 1;
            recording = start > nextNode->end;
            if (!recording) nextNode->end = winEnd + 1;
        }
    }

    // Finally operation
    if (recording) {
        nextNode->next = new RegionNode(start, length);
        count ++;
    }

    // Refine
    nextNode = root;
    int minPoint, maxPoint, endPoint;
    float minValue, maxValue;
    while(nextNode->next) {
        nextNode = nextNode->next;
        endPoint = nextNode->end;
        minPoint = nextNode->start, minValue = values[minPoint];
        maxPoint = nextNode->end, maxValue = values[maxPoint];
        
        for (int i = minPoint + 1; i < endPoint; i ++) {
            if (values[i] > maxValue)
                maxPoint = i, maxValue = values[i];
            else if (values[i] < minValue)
                minPoint = i, minValue = values[i];
        }
        
        nextNode->start = minPoint;
        nextNode->end = maxPoint;
    }

    return count;
}
#ifdef __cplusplus
extern "C" {
#endif
/* _ZcurvePy.get_orfs */
/* 
 * A orf finder with Z-curve encoding function
 * @param record  Genome sequence (object)
 * @param name    The name of genome sequence (str)
 * @param starts  Possible start codon List[str]
 * @param stops   Possible stops codon List[str]
 * @param minlen  Mininum length of a Open Reading Frame (str)
 * @param between_stops  Should find ORFs between stop codons or not (bool)
 * @param batch_encoder  BatchZcurveEncoder object
 * 
 * @return (List[Orf], Tuple[numpy.ndarray])
 */ 
PyObject *ZcurvePy_getOrfs(PyObject *self, PyObject *args, PyObject *kw) {
    static char *kwlist[] = { "seq", "name", "starts", "stops", "minlen", 
                              "between_stops", "batch_encoder", NULL };
    char *genome = nullptr; // complete genome sequence as cstring
    char *name = nullptr;   // name of the genome
    PyObject *PyStarts = nullptr; // start codon list as Python list
    PyObject *PyStops = nullptr;  // stop codon list as Python list
    int minlen = 90;        // min length of an ORF sequence
    bool betweenStops = false;  // should find ORFs between stop codons
    PyObject *BatchEncoder = nullptr;  // BatchZcurveEncoder Python object

    if (!PyArg_ParseTupleAndKeywords(args, kw, "s|sOOibO", kwlist, 
        &genome, &name, &PyStarts, &PyStops, &minlen, &betweenStops, &BatchEncoder)) {
        return NULL;
    }

    // name should not be empty
    if (!name || !strlen(name)) name = "anonymous";

    // length should not be less than minlen
    int length = (int) strlen(genome);
    if (length < minlen) {
        PyErr_SetString(PyExc_TypeError, "seq length too short");
        return NULL;
    }

    // parse start codon types
    char *cppStarts[MAX_CODON_TYPES];
    bool shouldFreeStarts = false;
    if(!parseCodons(PyStarts, cppStarts, DEFAULT_START_CODONS, shouldFreeStarts)) {
        PyErr_SetString(PyExc_TypeError, "fail to parse start codon list");
        return NULL;
    }

    // parse stop codon types
    char *cppStops[MAX_CODON_TYPES];
    bool shouldFreeStops = false;
    if(!parseCodons(PyStops, cppStops, DEFAULT_STOP_CODONS, shouldFreeStops)) {
        PyErr_SetString(PyExc_TypeError, "fail to parse stop codon list");
        return NULL;
    }

    // If batch encoder is provided, convert it to BatchZcurveEncoderObject
    BatchZcurveEncoderObject *Encoder = nullptr;
    if (BatchEncoder) {
        if (!PyObject_TypeCheck(BatchEncoder, &BatchZcurveEncoderType)) {
            PyErr_SetString(PyExc_TypeError, "batch_encoder must be a instance of ZcurvePy.BatchZcurveEncoder");
            return NULL;
        }
        Encoder = (BatchZcurveEncoderObject *) BatchEncoder;
    }

    std::vector<char *> seqBuff;  // raw sequence storage (pointers on genome or compGenome)
    seqBuff.reserve(ORF_VECTOR_RESERVE);
    std::vector<int> seqLens;  // lengths of raw sequences
    seqLens.reserve(ORF_VECTOR_RESERVE);
    std::vector<OrfObject *> orfBuff;  // OrfObject storage
    orfBuff.reserve(ORF_VECTOR_RESERVE);

    /* run for both strand */
    char *compGenome = nullptr; 
    for (int negStrand = 0; negStrand < 2; negStrand ++) {
        // get complement genome when running for negative strand
        if (negStrand) {
            compGenome = new char[length];
            for (int i = 0; i < length; i ++) {
                compGenome[i] = COMP_MAP[genome[length - i - 1]];
            }
            genome = compGenome; 
        }

        // scan the three phase
        for (int phase = 0; phase < 3; phase ++) {
            /* possible start of the orf */
            int *starts = nullptr;
            /* possible start codon type of the orf */
            int *startTypes = nullptr;
            /* the number of all possible starts of the orf */
            int numStarts = 0;
            /* last stop codon position */
            int lastStopPos = phase;

            for (int pos = phase; pos < length; pos += 3) {
                int matchResult = matchCodon(genome + pos, cppStarts);
                if (matchResult > -1) {
                    // meet the first start codon and reset recording state
                    if (!starts) {
                        starts = new int[MAX_NUM_STARTS];
                        startTypes = new int[MAX_NUM_STARTS];
                        numStarts = 0;
                    } 
                    // record alter start codons
                    if (numStarts < MAX_NUM_STARTS) {
                        starts[numStarts] = pos;
                        startTypes[numStarts] = matchResult;
                        numStarts ++;
                    }
                } else if (matchCodon(genome + pos, cppStops) > -1) {
                    // when find a sequence between two stop codons
                    if (!starts && betweenStops) {
                        starts = new int { lastStopPos };
                        startTypes = new int { -1 };
                        numStarts = 1;
                    }
                    
                    // when a possible start is found in front of a stop
                    if (starts) {
                        int seqlen = pos + 3 - starts[0];

                        if (seqlen >= minlen) {
                            char *subseq = genome + starts[0];
                            int frame = (1-2*negStrand) * (phase + 1);
                            float gcFrac = gcFraction(subseq, seqlen);

                            seqBuff.push_back(subseq);
                            seqLens.push_back(seqlen);

                            // save location information
                            if (!saveOrf(name, starts, numStarts, startTypes, pos+3, negStrand, length, 
                                frame, gcFrac, orfBuff)) {
                                PyErr_SetString(PyExc_MemoryError, "failed to create new Orf object");
                                delete[] compGenome;
                                delete[] starts;
                                delete[] startTypes;
                                return NULL;
                            }
                        } else { delete[] starts; delete[] startTypes; }
                    }

                    starts = nullptr, startTypes = nullptr, lastStopPos = pos + 3;
                }
            }

            delete[] starts; delete[] startTypes;
        }
    }

    // convert orfBuff
    import_array();
    npy_intp count = (npy_intp) seqBuff.size();
    PyObject *retr = PyArray_SimpleNew(1, &count, NPY_OBJECT);

    if (!retr) {
        PyErr_SetString(PyExc_MemoryError, "cannot create numpy array");
        return NULL;
    }

    PyObject** data = static_cast<PyObject**>(PyArray_DATA((PyArrayObject*)retr));
    for (npy_intp i = 0; i < count; i ++) {
        data[i] = (PyObject *) orfBuff[i];
    }

    // convert sequences to z-curve parameters
    if (Encoder) {
        int featureDim = Encoder->finalNParams;
        if (Encoder->biDirect) featureDim *= 2;

        float *paramList = (float *)malloc(count * featureDim * sizeof(float));
        
        multiThreadCoding(paramList, count, featureDim, seqBuff, seqLens, Encoder);
        PyObject *mat = convertToNumpy(paramList, count, featureDim);

        PyObject *retrTuple = PyTuple_New(2);
        PyTuple_SET_ITEM(retrTuple, 0, retr);
        PyTuple_SET_ITEM(retrTuple, 1, mat);
        retr = retrTuple;
    }

    // Handle Memory
    delete[] compGenome;
    if (shouldFreeStarts) for (int i = 0; cppStarts[i]; i++) free(cppStarts[i]);
    if (shouldFreeStops) for (int i = 0; cppStops[i]; i++) free(cppStops[i]);
    

    return retr;
}
/* ZcurvePy.find_island */
PyObject* ZcurvePy_findIsland(PyObject* self, PyObject* args, PyObject *kw) {
    import_array();
    static char *kwlist[] = {"curve", "window", "min_pcc", NULL};
    int window = 50000;
    float minPCC = 0.98F;
    PyObject *input_array;
    PyArrayObject *np_array = NULL, *temp_array = NULL;
    const float *c_array;
    npy_intp length;

    if (!PyArg_ParseTupleAndKeywords(args, kw, "O|if", kwlist, &input_array, &window, &minPCC))
        return NULL;

    if (!PyArray_Check(input_array)) {
        PyErr_SetString(PyExc_TypeError, "Input must be a NumPy array");
        return NULL;
    }

    np_array = (PyArrayObject *) input_array;

    if (PyArray_NDIM(np_array) != 1) {
        PyErr_SetString(PyExc_ValueError, "Array must be 1-dimensional");
        return NULL;
    }

    if (PyArray_TYPE(np_array) != NPY_FLOAT32) {
        PyErr_SetString(PyExc_TypeError, "Array must be of float32 type");
        return NULL;
    }

    if (!PyArray_ISCONTIGUOUS(np_array)) {
        temp_array = (PyArrayObject *) PyArray_GETCONTIGUOUS(np_array);
        if (!temp_array) {
            PyErr_SetString(PyExc_RuntimeError, "Failed to make array contiguous");
            return NULL;
        }
        np_array = temp_array;
    }

    c_array = (float *) PyArray_DATA(np_array);
    length = PyArray_DIM(np_array, 0);

    RegionNode *root = new RegionNode(NULL, -1);
    int count = findIsland(c_array, (int) length, window, minPCC, root);
    PyObject *results = PyList_New(count);

    int i = 0;
    RegionNode *nextNode = root->next;
    while (nextNode) {
        PyObject *region = Py_BuildValue("(i,i)", nextNode->start, nextNode->end);
        PyList_SET_ITEM(results, i, region);
        root = nextNode;
        nextNode = root->next;
        delete root;
        i ++;
    }

    if (temp_array) Py_DECREF(temp_array);

    return results;
}

#ifdef __cplusplus
}
#endif