from typing import List, Iterable
import sys

class StringHelper:
    @staticmethod
    def compute_levenshtein_distance(s: str, t: str) -> int:
        n = len(s)
        m = len(t)
        d = [[0] * (m + 1) for _ in range(n + 1)]

        if n == 0:
            return m
        if m == 0:
            return n

        for i in range(n + 1):
            d[i][0] = i
        for j in range(m + 1):
            d[0][j] = j

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                cost = 0 if s[i - 1] == t[j - 1] else 1
                d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)

        return d[n][m]


class StringExtensions:
    @staticmethod
    def to_capitalize(s: str) -> str:
        if not s:
            return s
        return s[0].upper() + s[1:]

    @staticmethod
    def find_closest_match(text: str, options: Iterable[str]) -> str:
        lowest_string = ""
        lowest_distance = sys.maxsize
        unique_options = set(options)

        for option in unique_options:
            distance = StringHelper.compute_levenshtein_distance(text, option)
            if lowest_distance > distance:
                lowest_distance = distance
                lowest_string = option

        return lowest_string

    @staticmethod
    def separate_capital_words(s: str) -> str:
        if not s:
            return None

        words = []
        for char in s:
            if char.isupper() and words:
                words.append(' ')
            words.append(char)

        return ''.join(words)
