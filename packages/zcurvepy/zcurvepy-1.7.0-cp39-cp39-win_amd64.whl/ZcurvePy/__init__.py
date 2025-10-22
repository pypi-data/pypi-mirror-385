__version__ = '1.7.0'
__upgrade__ = '2025-04-29'
f"""
    ZcurvePy -- High performance Python toolkit for the Z-curve theory!

    This is the Python package init module of ZcurvePy v{__version__} released.

    All the C/C++ apis can be called through this module. If you don't
    want to import additional third-party module (such as modules from
    scikit-learn) or APIs written in pure Python provided by ZcurvePy,
    (such as ZcurveBuilder), use 'import _ZcurvePy' instead of 'import
    ZcurvePy).

    Authors:    Zetong Zhang, Feng Gao
    Copyright:  Copyright 2025 TUBIC
    License:    MIT License
    Date:       {__upgrade__}

    Appendix Table:
            Correspondence between bases and chars in this software
    | char | base       | char | base       | char | base    | char | base    |
    |------|------------|------|------------|------|---------|------|---------|
    |  A   | A          |  B   | C, G, T    |  C   | C       |  D   | A, G, T |
    |  E   | null       |  F   | null       |  G   | G       |  H   | A, C, T |
    |  I   | A, G, C, T |  J   | null       |  K   | G, T    |  L   | null    |
    |  M   | A, C       |  N   | A, G, C, T |  O   | null    |  P   | null    |
    |  Q   | null       |  R   | A, G       |  S   | G, C    |  T   | T       |
    |  U   | T          |  V   | A, G, C    |  W   | A, T    |  X   | null    |
    |  Y   | C, T       |  Z   | A          |

    [Remarks]:
    1.  'null' means the software will just skip the character when read strings;
    2.  Degenerate symbols will be handled using rule of frequency, for example:
        'M' will be regarded as 50% A + 50% C and vectorized as [0.5, 0, 0.5, 0]
    3.  'I' means hypoxanthine and may be paired with any type of bases; 'Z' means
        diaminopurine and can only be paired with 'A'. (Zhou Y, et al. Science, 
        2021, 372(6541): 512-516.)
"""
import sys
# # Up regulate max recursion
sys.setrecursionlimit(10000)
from operator import methodcaller
from copy import deepcopy
# Numpy Support
import numpy as np

# ZcurvePy C/C++ APIs (Classes)
from _ZcurvePy import ZcurveEncoder
from _ZcurvePy import ZcurvePlotter
# ZcurvePy C/C++ APIs (Multi-thread)
from _ZcurvePy import BatchZcurveEncoder
from _ZcurvePy import BatchZcurvePlotter
# ZcurvePy C/C++ APIs (Method)
from _ZcurvePy import shuffle
from _ZcurvePy import decode

class ZcurveBuilder:
    """
    A simple API for building gene recognizer. It includes basic modules such 
    as feature extraction, preprocessing, negative sampling and model training.
    Each module is customizable. Core algorithm of ZCURVE 2.0 / 3.0.

    Args:
        encoder (Callable):  
            A function or object that can be called with a list of supported 
            sequences and returns a feature matrix of the data set. Default 
            is a BatchZcurveEncoder object that yields 189-dim features.

        model (object):  
            A machine learning model object that have `fit` and `predict_proba`
            method. Default is a RBF-SVM model from `sklearn.svm.SVC` with 
            balanced class weights.

        standard (bool):  
            Whether to apply standardization to the data. (Use `sklearn.
            preprocessing.StandardScaler`)  
            Default: True

        normal (bool):  
            Whether to apply normalization to the data. (Use `sklearn.
            preprocessing.MinMaxScaler`)  
            Default: False  
        
        neg_pos_ratio (int):  
            The ratio between negative samples and positive samples, decides 
            how many negative sequences should be obtained from each positive 
            case sequence.  
            Parameter for `ZcurveBuilder.shuffle`, default is 5.

        seed (int):  
            Random seed.
        
        n_jobs (int):  
            Number of CPU cores used. All are used by default.
    """
    def __init__(
        self,
        encoder=None,
        model=None,
        standard=True,
        normal=False,
        neg_pos_ratio=5,
        seed=42,
        n_jobs=-1
    ):
        self.encoder = encoder
        if self.encoder is None:
            hyper_params = [
                {'n': 1, 'local': True},
                {'n': 2, 'local': True},
                {'n': 3, 'local': True}
            ]  # Final number of generated parameters: 189
            self.encoder = BatchZcurveEncoder(
                hyper_params=hyper_params,
                n_jobs=n_jobs
            )
        
        self.model = model
        if self.model is None:
            from sklearn.svm import SVC
            self.model = SVC(
                kernel='rbf', 
                class_weight='balanced',
                random_state=seed
            )
        
        if standard is True:
            from sklearn.preprocessing import StandardScaler
            self.scaler = StandardScaler()
        else:
            self.scaler = None
        
        if normal is True:
            from sklearn.preprocessing import MinMaxScaler
            self.minmax = MinMaxScaler()
        else:
            self.minmax = None

        self.neg_pos_ratio = neg_pos_ratio
        self.seed = seed
        self.n_jobs = n_jobs
    
    @staticmethod
    def has_method(obj, method_name):
        """ Determine whether an object has the member function. """
        return callable(getattr(obj, method_name, None))
    
    def fit(
        self, 
        pos_data,
    ):
        """
        Fit the model after negative samples are generated and the dataset is preprocessed.

        Args:
            pos_data (object):  
                Positive example sequence data sets generally use reference gene sequences 
                as positive examples.
        """
        gen_seed = deepcopy(pos_data)
        gen_data = shuffle(
            records=gen_seed,
            ratio=self.neg_pos_ratio,
            seed=self.seed,
            n_jobs=self.n_jobs
        )

        pos_features = np.array(self.encoder(pos_data))
        neg_features = np.array(self.encoder(gen_data))
        pos_labels = np.ones(pos_features.shape[0])
        neg_labels = np.zeros(neg_features.shape[0])

        X = np.concatenate((pos_features, neg_features), axis=0)
        y = np.concatenate((pos_labels, neg_labels), axis=0)

        if self.scaler is not None:
            X = self.scaler.fit_transform(X)
        if self.minmax is not None:
            X = self.minmax.fit_transform(X)

        self.model.fit(X, y)
    
    def predict(
        self,
        data,
        threshold=None
    ):
        """
        Predict whether a set of sequences is a gene coding sequence.

        Args:
            data (object):  
                Sequence dataset to predict.
            threshold (float):
                Label judgment threshold. Greater than the threshold 
                is a positive sample, and less than the threshold is 
                a negative sample.
        
        Returns:
            labels (ndarray): 
                Prediction label for the sample.
            scores (ndarray):
                The predicted score of the sample.
        """
        features = self.encoder(data)
        if self.scaler is not None:
            features = self.scaler.transform(features)
        if self.minmax is not None:
            features = self.minmax.transform(features)
        
        if self.has_method(self.model, "decision_function"):
            scores = self.model.decision_function(features)
            threshold = 0 if threshold is None else threshold
            labels = np.array(scores > 0, dtype='int')
        elif self.has_method(self.model, "predict_proba"):
            scores = self.model.predict_proba(features)
            threshold = 0.5 if threshold is None else threshold
            labels = np.array(scores > 0.5, dtype='int')
        else:
            raise Exception("Unsupported model types")
        
        return labels, scores


class ZcurveSegmenter:
    """
    Z-curve segmenter based on genome order number, which can be considered an 
    extended version of the GC-Profile's core. It has 7 modes and can be used 
    for edge recognition of genomic islands, CpG islands, AT-rich regions and 
    other structures.

    Args:
        mode (str): The mode of Z-curve segmenter. It can be one of the following:
            'GN': Using genome order number to segment Z-curves;
            'RY': Using RY order number to segment RY-profile;
            'MK': Using MK order number to segment MK-profile;
            'WS': Using WS order number to segment GC-profile;
            'AT': Using AT order number to segment AT-skew;
            'GC': Using GC order number to segment GC-skew;
            'CG': Using CpG order number to segment CpG-profile.
        halting (int): The halting value of segmenter. 
            Defaults to 100.
        min_len (int): The minimum length of fragments. 
            Defaults to 3000.
        max_depth (int): The maximum depth of iteration. 
            Defaults to 9999.
    """
    # Modes and their corresponding functions
    func = {
        'GN': 'genome_dS_curve',
        'RY': 'RY_dS_curve',
        'MK': 'MK_dS_curve',
        'WS': 'WS_dS_curve',
        'AT': 'AT_dS_curve',
        'GC': 'GC_dS_curve',
        'CG': 'CpG_dS_curve'
    }

    def __init__(
        self,
        mode,
        halting=100,
        min_len=3000,
        max_depth=9999
    ):
        self.mode = mode
        self.halting = halting
        self.min_len = min_len
        self.max_depth = max_depth
        self.executed = False
        self.seg_points = []
    
    def _recursion(
        self, 
        record, 
        offset: int, 
        depth: int
    ):
        """
        Recursive function for segmenting Z-curves.
        """
        plotter = ZcurvePlotter(record)
        max_point, max_value = methodcaller(self.func[self.mode], only_m=True)(plotter)
        left_len, right_len = max_point, len(record) - max_point

        if (max_value > self.halting and
            left_len >= self.min_len and right_len >= self.min_len):
            self.seg_points.append((max_point + offset, max_value))

            if depth < self.max_depth:
                # Segment left subsequence
                left_seq = record[:max_point]
                self._recursion(left_seq, offset, depth + 1)
                del left_seq
                # Segment right subsequence
                right_seq = record[max_point:]
                self._recursion(right_seq, offset + max_point, depth + 1)
                del right_seq
    
    def run(
        self, 
        record
    ):
        """
        Run the segmenter.

        Args:
            record (str): The sequence to be segmented.

        Returns:
            list:   A list of tuples, each tuple contains the 
                    position and the value of the segment point.
        """
        if not self.executed:
            self._recursion(record, 0, 0)
            self.seg_points.sort(key=lambda x : x[0])
            self.executed = True
            return self.seg_points
        else:
            raise Exception("Please reset the object first to segment another sequence!")
    
    def reset(self):
        """ 
        Reset the segmenter. 
        Clear segmentation points generated in the last run.
        """
        self.seg_points = []
        self.executed = False
