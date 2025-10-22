#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Keyword-based matcher for GitLab analyzer."""

"""Keyword-based matcher for GitLab analyzer."""

from dataclasses import dataclass
from typing import List

from .utils import normalize_keywords, normalize_text


@dataclass
class MatchResult:
    item: object
    score: int
    matched_fields: List[str]
    item_type: str


class Matcher:
    """simple keyword matcher using presence counts."""

    def _calculate_score(self, keywords: List[str], text: str, weight: float) -> int:
        if not text:
            return 0

        normalized_text = normalize_text(text)
        hits = 0
        for keyword in keywords:
            if keyword in normalized_text:
                hits += 1

        if hits == 0:
            return 0

        return min(100, int(hits * 20 * weight))

    def match_merge_request(self, mr, keywords: List[str]) -> MatchResult:
        normalized_keywords = normalize_keywords(keywords)

        score = 0
        matched_fields: List[str] = []

        field_weights = {
            "title": 1.0,
            "description": 0.8,
            "labels": 0.5,
        }

        title_score = self._calculate_score(
            normalized_keywords, mr.title, field_weights["title"]
        )
        if title_score:
            score += title_score
            matched_fields.append("title")

        description_score = self._calculate_score(
            normalized_keywords,
            mr.description or "",
            field_weights["description"],
        )
        if description_score:
            score += description_score
            matched_fields.append("description")

        labels_text = " ".join(mr.labels)
        labels_score = self._calculate_score(
            normalized_keywords, labels_text, field_weights["labels"]
        )
        if labels_score:
            score += labels_score
            matched_fields.append("labels")

        return MatchResult(
            item=mr,
            score=min(100, score),
            matched_fields=matched_fields,
            item_type="MR",
        )
