  ## Upgrades

  1. Stop replacing hierarchical scores with cosine in XModel.predict.
     Files: xmr4el/xmr/model.py:417
     Functions: XModel.predict
     Affects: inference, evaluation
     Why: this is the smallest direct fix to make returned scores reflect the trained hierarchy rather than an external cosine reranker.

  2. Fold ancestor path score into final leaf label score.
     Files: xmr4el/xmr/base.py:1068, xmr4el/xmr/base.py:1153
     Functions: HierarchicaMLModel.predict, especially _predict_one_leaf
     Affects: inference
     Why: PECOS-style hierarchical scoring depends on route confidence all the way down; right now that confidence only prunes beams.

  3. Make child-layer feature augmentation consistent between training and inference, or gate it off behind a PECOS-compat mode.
     Files: xmr4el/xmr/base.py:815, xmr4el/xmr/base.py:1149
     Functions: prepare_layer, HierarchicaMLModel.predict
     Affects: training, inference
     Why: current score distributions drift because deeper models are trained on fused-score-derived features but queried with different features.

  4. Use one score domain consistently for matcher/ranker fusion.
     Files: xmr4el/xmr/base.py:256, xmr4el/xmr/base.py:477
     Functions: MLModel.fused_predict, MLModel.predict
     Affects: inference, possibly training
     Why: predict_proba, decision_function, expit, and fixed-alpha fusion are mixed without calibration. Even if retrieval is decent, numeric scores will not track PECOS-
     style outputs closely.

  5. Evaluate the score matrix directly instead of candidate-set hits.
     Files: _test/xmr4el/test_evaluate_pipeline.py:114, _test/xmr4el/test_evaluate_pipeline_xlinker.py:90
     Functions: main
     Affects: evaluation
     Why: until evaluation uses ranked scores, it is hard to know whether divergence is from the model or from the evaluation protocol.

  6. Larger refactor: move closer to PECOS XLinear semantics by removing the custom per-label [X | Z_label] ranker stage and the layer-wise feature augmentation.
     Files: xmr4el/xmr/base.py:815, xmr4el/ranker/train.py:255, xmr4el/matcher/train.py:10
     Functions: prepare_layer, RankerTrainer.train, MatcherTrainer.train
     Affects: training, inference
     Why: this is the main architectural gap from PECOS, but it is not the first thing I would change.