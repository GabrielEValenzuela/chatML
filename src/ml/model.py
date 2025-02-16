"""
This module provides a wrapper class around a PyKEEN TransH model for entity similarity tasks.
The class provides:
    1) Model loading from a .pkl file.
    2) TriplesFactory creation from a .tsv or .tsv.gz dataset.
    3) Filtering and indexing of certain
    4) A method to predict similarity for a given entity (by label or ID).

"""

import torch
import pandas as pd
import os
from pykeen.triples import TriplesFactory
from typing import List, Tuple, Optional

# ----------------------------------------------------------
# Constants
# ----------------------------------------------------------
# Gets /app/src/ml if inside src/ml
base_dir = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(base_dir, "model_data/transH_model.pkl")
TRIPLES_PATH = os.path.join(base_dir, "model_data/dataset.tsv.gz")


class TransHModel:
    """
    A wrapper class around a PyKEEN TransH model for entity similarity tasks.

    This class provides:
    1) Model loading from a .pkl file.
    2) TriplesFactory creation from a .tsv or .tsv.gz dataset.
    3) Filtering and indexing of certain "heads".
    4) A method to predict similarity for a given entity (by label or ID).
    """

    def __init__(self,
                 model_path: str = MODEL_PATH,
                 triples_path: str = TRIPLES_PATH):
        """
        Initialize paths for model & triple data. Actual loading is done by 'load()'.

        :param model_path: Path to the saved PyTorch model (TransH).
        :param triples_path: Path to the TSV (optionally gzipped) file containing triples.
        """
        self.model_path = model_path
        self.triples_path = triples_path

        # Attributes that will be set in load()
        self.model = None
        self.triples_factory = None
        self.heads = None
        self.heads_idx = None
        self.relation_same_as = None
        self.relation_same_as_idx = None

    def load(self):
        """
        Loads:
         - The TransH model from self.model_path.
         - The TriplesFactory from self.triples_path.
         - Filters 'heads' based on a custom criterion and caches their IDs in heads_idx.
         - Identifies the 'sameAs' relation and its ID if present.
        """
        # 1. Load the PyKEEN model with metadata
        self.model = torch.load(self.model_path, weights_only=False)

        # 2. Construct a TriplesFactory
        self.triples_factory = TriplesFactory.from_path(
            self.triples_path,
            create_inverse_triples=True
        )

        # 3. Load the raw dataset into a DataFrame for filtering
        df = pd.read_csv(self.triples_path, sep='\t',
                         header=None, names=['head', 'relation', 'tail'])

        # 4. Example filter: "pronto.owl#space_site" in head and exactly 3 underscores in the portion after '#'
        #    Adapt as needed for your own logic
        def _filter_head(x: str) -> bool:
            if 'pronto.owl#space_site' not in x:
                return False
            # example check: ensure "#something_with_3_underscores"
            tokens = x.split('#', 1)[1].split('_')
            return len(tokens) == 3

        # Filter heads
        self.heads = df[df['head'].apply(_filter_head)]['head'].values

        # 5. Convert these heads to integer IDs
        self.heads_idx = [
            self.triples_factory.entity_to_id[h] for h in self.heads
        ]

        # 6. "sameAs" relation
        self.relation_same_as = "http://www.w3.org/2002/07/owl#sameAs"
        self.relation_same_as_idx = self.triples_factory.relation_to_id.get(
            self.relation_same_as
        )

    def predict_similarity(self, entity_input, relation_idx: int = 5, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Given an entity (as a label or integer ID), compute similarity scores
        against all other entities for a particular relation index.

        :param entity_input: Entity label (str) or entity ID (int).
        :param relation_idx: Relation index (defaults to 5, per your snippet).
        :param top_k: Number of top results to return.
        :return: Returns a list of [URI, score].
        :raises ValueError/TypeError: If entity_input is invalid.
        """
        # 1. Validate the entity input
        try:
            valid_id = self._validate_input(entity_input)
        except (ValueError, TypeError) as e:
            return [(str(e), -1.0)]

        # 2. Score the tail side with [valid_id, relation_idx]
        #    shape of the scores is (1, num_entities)
        scores = self.model.score_t(torch.tensor([[valid_id, relation_idx]]))

        # 3. 'largest=False' -> ascending order of scores
        #    if your model produces distances or negative log-likelihood,
        #    you might invert logic accordingly
        values, indices = torch.topk(
            scores,
            k=scores.size(1),
            dim=1,
            largest=False
        )

        # 4. Convert these top-k results to (label, score) pairs
        return self._extract_top_entities(values, indices, top_k)

    # ----------------- Helper Methods -----------------

    def _validate_input(self, entity_input) -> int:
        """
        Convert an entity label or ID to an integer ID 
        that is present in self.heads_idx.

        :param entity_input: An integer ID or a string label.
        :return: The integer ID.
        :raises ValueError: If the entity is invalid.
        :raises TypeError: If the input is neither an int nor a str.
        """
        if isinstance(entity_input, int):
            if entity_input in self.heads_idx:
                return entity_input
            raise ValueError(f"ID '{entity_input}' not found in heads_idx.")
        elif isinstance(entity_input, str):
            try:
                e_id = self.triples_factory.entity_to_id[entity_input]
                if e_id in self.heads_idx:
                    return e_id
                raise ValueError(
                    f"Entity label '{entity_input}' (ID {e_id}) not allowed (not in heads_idx).")
            except KeyError:
                raise ValueError(
                    f"Entity label '{entity_input}' not found in TriplesFactory.")
        else:
            raise TypeError(
                "entity_input must be an integer (ID) or a string (label).")

    def _extract_top_entities(self, values: torch.Tensor, indices: torch.Tensor, top_k: int) -> List[Tuple[str, float]]:
        """
        Convert sorted indices and scores into a list of (label, score), 
        returning up to 'top_k' entries.

        :param values: A tensor of shape (1, N) with sorted scores.
        :param indices: A tensor of shape (1, N) with sorted entity indices.
        :param top_k: Max results to return.
        :return: A list of (entity_label, float_score).
        """
        results = []
        # each row corresponds to a batch dimension (1 in this case)
        for row_indices, row_values in zip(indices, values):
            for idx, val in zip(row_indices, row_values):
                resolved_id = self._safe_resolve(idx.item())
                if resolved_id is not None:
                    label = self.triples_factory.entity_id_to_label[resolved_id]
                    results.append((label, float(val.item())))
                    if len(results) >= top_k:
                        return results
        return results

    def _safe_resolve(self, index: int) -> Optional[int]:
        """
        Convert an index into a valid entry from self.heads_idx
        if within range, otherwise return None.
        """
        try:
            return self.heads_idx[index]
        except IndexError:
            return None
