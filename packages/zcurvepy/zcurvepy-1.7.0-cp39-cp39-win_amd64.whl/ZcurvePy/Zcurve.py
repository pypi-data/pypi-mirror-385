from typing import List
from collections.abc import Iterable
from Bio.SeqRecord import SeqRecord
import numpy as np
from _ZcurvePy import get_orfs, BatchZcurveEncoder
import warnings
warnings.filterwarnings(action='ignore')

class Zcurve:
    """
    ab initio coding-gene recognition system of ZCURVE.

    Parameters
    ----------
    minlen: int
        mininum gene length (default: 90);
    
    starts: Iterable[str]
        alter start codons (default: ['ATG', 'GTG', 'TTG'])
    
    stops: Iterable[str]
        alter stop codons (default: ['TAA', 'TAG', 'TGA'])

    """
    def __init__(self,
        minlen=90,
        starts=None,
        stops=None,
        n_jobs=0,
        long_len=300,
        random_state=42,
        verbose=False
    ):
        self.minlen = minlen
        if starts is None:
            self.starts = [f + "TG" for f in "AGT"]
        elif isinstance(starts, Iterable):
            self.starts = list()
            for item in starts:
                stritem = str(item)
                if len(stritem) != 3:
                    raise ValueError("non-triplet start codon(s)")
                self.starts.append(stritem)
            if len(self.starts) == 0:
                raise ValueError("start codon list is empty")
        else:
            raise ValueError("param 'starts' is not iterable")
        if stops is None:
            self.stops = ['TAA', 'TAG', 'TGA']
        elif isinstance(stops, Iterable):
            self.stops = list()
            for item in stops:
                stritem = str(item)
                if len(stritem) != 3:
                    raise ValueError("non-triplet stop codon(s)")
                self.stops.append(stritem)
            if len(self.stops) == 0:
                raise ValueError("stop codon list is empty")
        else:
            raise ValueError("param 'starts' is not iterable")

        self.long_len = long_len
        self.random_state = random_state
        self.n_iter = 5
        self.up_thres = 0.5
        self.down_thres = -0.85
        
        self._encoder = BatchZcurveEncoder([
            { "k": 1, "freq": True  },
            { "k": 2, "local": True },
            { "k": 3, "local": True },
            { "k": 4, "freq": True  }
        ], n_jobs=n_jobs)

    def _preprocess(self, genome: List[SeqRecord]):
        self.orfs = np.array([])
        self.raw_params = np.empty((0, 765), np.float32)
        self.gc_cont, self.genom_size = 0, 0
        for scaffold in genome:
            strseq = str(scaffold.seq).upper()
            self.gc_cont += strseq.count("G") + strseq.count("C")
            self.genom_size += len(strseq)
            seqname = scaffold.id
            _orfs, _raw_params = get_orfs(
                seq=strseq, name=seqname, 
                minlen=self.minlen,
                starts=self.starts, 
                stops=self.stops,
                batch_encoder=self._encoder
            )
            self.orfs = np.append(self.orfs, _orfs)
            self.raw_params = np.concatenate((self.raw_params, _raw_params))
        self.orf_lens = np.array([len(orf) for orf in self.orfs])
        self.gc_cont /= self.genom_size
        if self.gc_cont < 0.5574:
            self.n_clusters = 3
        else:
            self.n_clusters = 6
    
    def _init_labels(self):
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        long_indices = np.where(self.orf_lens >= self.long_len)[0]
        long_params = self.raw_params[long_indices]
        long_lens = self.orf_lens[long_indices]
        self.kmeans_scaler = StandardScaler()
        long_params_std = self.kmeans_scaler.fit_transform(long_params)
        self.kmeans = KMeans(n_clusters=self.n_clusters, n_init=50,
                             max_iter=600, random_state=self.random_state)
        kmeans_labels = self.kmeans.fit_predict(long_params_std)
        max_aver_len, true_label = -1, 0
        for label in range(self.n_clusters):
            cluster_mask = np.where(kmeans_labels == label)[0]
            aver_len = np.mean(long_lens[cluster_mask])
            if aver_len > max_aver_len:
                max_aver_len = aver_len
                true_label = label
        self.init_pos = long_indices[kmeans_labels == true_label]
        self.init_neg = long_indices[kmeans_labels != true_label]

    def _spread_labels(self):
        from sklearn.preprocessing import StandardScaler
        from sklearn.svm import SVC
        self.scaler = StandardScaler()
        self.classifier = SVC(kernel='rbf')
        self.pos_indices, self.neg_indices = self.init_pos, self.init_neg
        for _ in range(self.n_iter):
            pos_features = self.raw_params[self.pos_indices]
            neg_features = self.raw_params[self.neg_indices]
            features = np.concatenate((pos_features, neg_features))
            features_std = self.scaler.fit_transform(features)
            labels = np.array([1]*len(pos_features)+[0]*len(neg_features))
            self.classifier.fit(features_std, labels)
            params_std = self.scaler.transform(self.raw_params)
            self.pred_scores = self.classifier.decision_function(params_std)
            self.pos_indices = np.where(self.pred_scores > self.up_thres)[0]
            self.neg_indices = np.where(self.pred_scores < self.down_thres)[0]

    def fit(self, genome: List[SeqRecord]):
        self._preprocess(genome)
        self._init_labels()
        self._spread_labels()
