from __future__ import annotations

from dataclasses import dataclass
from typing import List, Set, Dict
from datetime import datetime, timedelta

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .db import SessionLocal
from .models import ContentItem, UserBehavior
from .schemas import RecommendationItem


@dataclass
class CatalogRow:
    id: int
    kind: str
    title: str
    genres: str
    keywords: str
    synopsis: str
    image_url: str | None = None
    poster_data_url: str | None = None

    @property
    def text(self) -> str:
        parts = [self.kind or "", self.title or "", self.genres or "", self.keywords or "", self.synopsis or ""]
        return " ".join([p for p in parts if p])


class Recommender:
    def __init__(self):
        self._vectorizer: TfidfVectorizer | None = None
        self._matrix = None
        self._rows: List[CatalogRow] = []
        self._id_to_index: dict[int, int] = {}
        self._catalog_count = 0

    def refresh_catalog(self):
        db = SessionLocal()
        try:
            items = db.query(ContentItem).all()
            self._catalog_count = len(items)
            self._rows = [
                CatalogRow(
                    id=i.id,
                    kind=i.kind,
                    title=i.title,
                    genres=i.genres,
                    keywords=i.keywords,
                    synopsis=i.synopsis,
                    image_url=i.image_url,
                    poster_data_url=i.poster_data_url,
                )
                for i in items
            ]

            self._id_to_index = {r.id: idx for idx, r in enumerate(self._rows)}

            corpus = [r.text for r in self._rows]
            # if empty, keep things safe
            if not corpus:
                self._vectorizer = TfidfVectorizer(stop_words="english")
                self._matrix = None
                return

            self._vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
            self._matrix = self._vectorizer.fit_transform(corpus)
        finally:
            db.close()

    def refresh_if_catalog_changed(self):
        db = SessionLocal()
        try:
            count = db.query(ContentItem).count()
        finally:
            db.close()

        if count != self._catalog_count:
            self.refresh_catalog()

    def get_user_behavior_scores(self, user_id: str = "demo") -> Dict[int, float]:
        """Calculate behavior-based affinity scores for real-time learning"""
        db = SessionLocal()
        try:
            # Get recent behavior (last 7 days)
            cutoff = datetime.utcnow() - timedelta(days=7)
            behaviors = db.query(UserBehavior).filter(
                UserBehavior.user_id == user_id,
                UserBehavior.created_at >= cutoff
            ).all()
            
            behavior_scores = {}
            
            for behavior in behaviors:
                # Base score for interaction
                base_score = 1.0
                
                # Boost based on interaction type
                if behavior.interaction_type == 'recommendation_click':
                    base_score *= 3.0  # High value: they clicked a recommendation
                elif behavior.interaction_type == 'click':
                    base_score *= 2.0  # Medium value: they showed interest
                elif behavior.interaction_type == 'dwell':
                    # Dwell time scoring: longer dwell = more interest
                    if behavior.dwell_time:
                        base_score *= min(behavior.dwell_time / 10.0, 2.0)  # Cap at 2x
                elif behavior.interaction_type == 'view':
                    base_score *= 0.5  # Low value: just viewed
                elif behavior.interaction_type == 'search':
                    base_score *= 1.5  # Medium-high value: actively searched
                
                # Scroll position boost (if they scrolled deep, they were interested)
                if behavior.scroll_position and behavior.scroll_position > 0.5:
                    base_score *= 1.5
                
                # Accumulate scores
                behavior_scores[behavior.content_id] = behavior_scores.get(behavior.content_id, 0) + base_score
            
            return behavior_scores
        finally:
            db.close()

    def recommend(self, saved_content_ids: Set[int], user_reflections: dict[int, str] = None, limit: int = 10, user_id: str = "demo", include_poster_data: bool = False) -> List[RecommendationItem]:
        self.refresh_if_catalog_changed()

        if not self._rows or self._matrix is None or self._vectorizer is None:
            return []

        saved_ids = list(saved_content_ids)
        user_reflections = user_reflections or {}
        
        # Get real-time behavior scores
        behavior_scores = self.get_user_behavior_scores(user_id)

        # if no saved items and no behavior, return top generic picks (highest TF-IDF norm)
        if not saved_ids and not behavior_scores:
            norms = np.asarray(self._matrix.power(2).sum(axis=1)).ravel()
            top_idx = np.argsort(-norms)[:limit]
            return [
                RecommendationItem(
                    id=self._rows[i].id,
                    kind=self._rows[i].kind,
                    title=self._rows[i].title,
                    score=float(norms[i]),
                    genres=self._rows[i].genres,
                    keywords=self._rows[i].keywords,
                    synopsis=self._rows[i].synopsis,
                    image_url=self._rows[i].image_url,
                    poster_data_url=self._rows[i].poster_data_url if include_poster_data else None,
                )
                for i in top_idx
            ]

        # Combine saved items and high-affinity behavior items
        combined_ids = set(saved_ids)
        
        # Add items with high behavior scores (threshold: 2.0+ interactions)
        for content_id, score in behavior_scores.items():
            if score >= 2.0 and content_id not in combined_ids:
                combined_ids.add(content_id)
        
        combined_indices = [self._id_to_index[i] for i in combined_ids if i in self._id_to_index]
        if not combined_indices:
            return []

        # Build enhanced user profile with reflections
        saved_texts = []
        for idx in combined_indices:
            row = self._rows[idx]
            text = row.text
            # Add user reflection to the profile if available
            if row.id in user_reflections and user_reflections[row.id]:
                text += " " + user_reflections[row.id]
            # Add behavior-based weighting
            if row.id in behavior_scores:
                text += " " * int(behavior_scores[row.id])  # Repeat text based on behavior score
            saved_texts.append(text)

        # Vectorize user profile
        user_profile_vec = None
        if saved_texts and self._vectorizer:
            user_profile_vec = self._vectorizer.transform(saved_texts)
            user_profile_mean = np.asarray(user_profile_vec.mean(axis=0))

        # Similarity: average cosine similarity between each candidate and saved set
        candidate_mask = np.ones(len(self._rows), dtype=bool)
        for idx in combined_indices:
            candidate_mask[idx] = False

        candidates = np.where(candidate_mask)[0]
        if candidates.size == 0:
            return []

        combined_vecs = self._matrix[combined_indices]
        cand_vecs = self._matrix[candidates]

        # Calculate similarity with both saved items and user profile
        sims = cosine_similarity(cand_vecs, combined_vecs)  # shape: (num_candidates, num_combined)
        base_scores = sims.mean(axis=1)

        # Boost scores based on user profile similarity if available
        if user_profile_vec is not None:
            profile_sims = cosine_similarity(cand_vecs, user_profile_mean).ravel()
            # Blend base scores with profile similarity (60% base, 40% profile for real-time learning)
            scores = 0.6 * base_scores + 0.4 * profile_sims
        else:
            scores = base_scores

        # Add genre preference boost
        saved_genres = set()
        for idx in combined_indices:
            genres = self._rows[idx].genres
            if genres:
                saved_genres.update([g.strip().lower() for g in genres.split(",")])

        # Boost candidates that share genres with saved/behavior items
        for i, candidate_idx in enumerate(candidates):
            candidate_genres = set()
            genres = self._rows[candidate_idx].genres
            if genres:
                candidate_genres.update([g.strip().lower() for g in genres.split(",")])

            # Boost score for shared genres (increased from 10% to 15% for real-time learning)
            shared_genres = saved_genres & candidate_genres
            if shared_genres:
                scores[i] *= (1.0 + 0.15 * len(shared_genres))  # 15% boost per shared genre
            
            # Additional boost for items with similar behavior patterns
            for content_id in combined_ids:
                if content_id in behavior_scores and behavior_scores[content_id] > 3.0:
                    # If user strongly interacted with similar content, boost this candidate
                    # Check if this candidate has similar attributes to high-affinity items
                    pass  # Could add more sophisticated similarity here

        top_local = np.argsort(-scores)[:limit]
        top_indices = candidates[top_local]

        results: List[RecommendationItem] = []
        for i in top_indices:
            r = self._rows[int(i)]
            original_score = scores[np.where(candidates == i)[0][0]] if candidates.size else 0.0
            results.append(
                RecommendationItem(
                    id=r.id,
                    kind=r.kind,
                    title=r.title,
                    score=float(original_score),
                    genres=r.genres,
                    keywords=r.keywords,
                    synopsis=r.synopsis,
                    image_url=r.image_url,
                    poster_data_url=r.poster_data_url if include_poster_data else None,
                )
            )
        # Sort again for strictness
        results.sort(key=lambda x: x.score, reverse=True)
        return results