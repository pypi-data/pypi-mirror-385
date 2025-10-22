#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""matcher module for GitLab analyzer."""

from dataclasses import dataclass
from typing import List, Sequence, Tuple

from rich.console import Console

from .mr_collector import MergeRequestSummary
from .commit_collector import CommitSummary
from .utils import normalize_keywords, normalize_text

console = Console()


@dataclass
class MatchResult:
    """match result container."""

    item: object
    score: int
    matched_fields: List[str]
    item_type: str

    def __str__(self) -> str:
        return f"[{self.item_type}] score={self.score} fields={','.join(self.matched_fields)}"


class Matcher:
    """keyword-based matcher for merge requests and commits."""

    def __init__(self, minimum_score: int = 30):
        self.minimum_score = minimum_score

    def _calculate_score(self, keywords: List[str], text: str, weight: float) -> Tuple[int, List[str]]:
        if not text:
            return 0, []

        normalized_text = normalize_text(text)
        matched_keywords: List[str] = []

        for keyword in keywords:
            if keyword in normalized_text:
                matched_keywords.append(keyword)

        if not matched_keywords:
            return 0, []

        score = int(min(100, len(matched_keywords) * 20 * weight))
        return score, matched_keywords

    def _aggregate(self, scores: List[int]) -> int:
        if not scores:
            return 0
        total = sum(scores)
        return min(100, total)

    def match_merge_request(self, mr: MergeRequestSummary, keywords: List[str]) -> MatchResult:
        normalized_keywords = normalize_keywords(keywords)

        fields = {
            "title": (mr.title, 1.0),
            "description": (mr.description or "", 0.8),
            "labels": (" ".join(mr.labels), 0.6),
            "branches": (
                f"{mr.source_branch or ''} {mr.target_branch or ''}",
                0.4,
            ),
        }

        scores: List[int] = []
        matched_fields: List[str] = []

        for field_name, (text, weight) in fields.items():
            score, hits = self._calculate_score(normalized_keywords, text, weight)
            if score > 0 and hits:
                scores.append(score)
                matched_fields.append(field_name)

        total_score = self._aggregate(scores)

        return MatchResult(
            item=mr,
            score=total_score,
            matched_fields=matched_fields,
            item_type="MR",
        )

    def match_commit(self, commit: CommitSummary, keywords: List[str]) -> MatchResult:
        normalized_keywords = normalize_keywords(keywords)

        fields = {
            "message": (commit.message, 1.0),
            "author": (commit.author, 0.5),
            "email": (commit.author_email or "", 0.4),
        }

        scores: List[int] = []
        matched_fields: List[str] = []

        for field_name, (text, weight) in fields.items():
            score, hits = self._calculate_score(normalized_keywords, text, weight)
            if score > 0 and hits:
                scores.append(score)
                matched_fields.append(field_name)

        total_score = self._aggregate(scores)

        return MatchResult(
            item=commit,
            score=total_score,
            matched_fields=matched_fields,
            item_type="Commit",
        )

    def search(
        self,
        merge_requests: Sequence[MergeRequestSummary],
        commits: Sequence[CommitSummary],
        query: str,
        max_results: int = 20,
    ) -> List[MatchResult]:
        keywords = normalize_keywords(query.split())
        results: List[MatchResult] = []

        for mr in merge_requests:
            match = self.match_merge_request(mr, keywords)
            if match.score >= self.minimum_score:
                results.append(match)

        for commit in commits:
            match = self.match_commit(commit, keywords)
            if match.score >= self.minimum_score:
                results.append(match)

        results.sort(key=lambda item: item.score, reverse=True)
        if len(results) > max_results:
            results = results[:max_results]

        console.print(
            f"[green]✓ Found {len(results)} matches from {len(merge_requests)} merge requests and {len(commits)} commits[/green]"
        )

        return results
