class StringHelper:
    @staticmethod
    def compute_levenshtein_distance(s: str, t: str) -> int:
        n = len(s)
        m = len(t)
        d = [[0] * (m + 1) for _ in range(n + 1)]

        # Step 1
        if n == 0:
            return m
        if m == 0:
            return n

        # Step 2
        for i in range(n + 1):
            d[i][0] = i
        for j in range(m + 1):
            d[0][j] = j

        # Step 3
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                # Step 5
                cost = 0 if s[i - 1] == t[j - 1] else 1

                # Step 6
                d[i][j] = min(
                    d[i - 1][j] + 1,  # Deletion
                    d[i][j - 1] + 1,  # Insertion
                    d[i - 1][j - 1] + cost  # Substitution
                )

        # Step 7
        return d[n][m]

