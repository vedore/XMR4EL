import json

from pathlib import Path


class Config:
    def __init__(
        self,
        vectorizer_config: dict = None,
        transformer_config: dict = None,
        dimension_config: dict = None,
        clustering_config: dict = None,
        matcher_config: dict = None,
        ranker_config: dict = None,
        cur_config: dict = None,
        min_leaf_size: int = 20,
        max_leaf_size: int = None,
        cut_half_cluster: bool = False,
        ranker_every_layer: bool = True,
        n_workers: int = 8,
        depth: int = 1,
        emb_flag: int = 1,
    ):

        self.vectorizer_config = vectorizer_config
        self.transformer_config = transformer_config
        self.dimension_config = dimension_config
        self.clustering_config = clustering_config
        self.matcher_config = matcher_config
        self.ranker_config = ranker_config
        self.cur_config = cur_config

        self.min_leaf_size = min_leaf_size
        self.max_leaf_size = max_leaf_size
        self.cut_half_cluster = cut_half_cluster
        self.ranker_every_layer = ranker_every_layer

        self.n_workers = n_workers
        self.depth = depth
        self.emb_flag = emb_flag


        
