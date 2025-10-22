class WellHelper:
    @staticmethod
    def to_alpha_numeric(row: int, column: int) -> str:
        return WellHelper.to_alpha(row) + str(column)

    @staticmethod
    def to_alpha(row: int) -> str:
        result = ''
        index = 0
        while row > 26:
            index += 1
            row -= 26
        if index > 0:
            result += chr(index + 64)
        result += chr(row + 64)
        return result

    @staticmethod
    def row_column_from_alpha_numeric(alpha_numeric: str) -> tuple:
        length_of_alphas = 0
        while alpha_numeric[length_of_alphas].isalpha():
            length_of_alphas += 1
        alphas = alpha_numeric[:length_of_alphas].upper()
        digits = alpha_numeric[length_of_alphas:]

        if not alphas or not digits:
            raise ValueError(f"Alpha numeric row/column '{alpha_numeric}' is invalid.")

        if len(alphas) == 2:
            alphas = 'A' + alphas[1]

        if len(alphas) > 2:
            raise ValueError("Cannot currently parse alpha numeric values of more than two letters. "
                             "Please use Row and Column headers for your data files if large plates or arrays are needed.")

        row = 0
        if len(alphas) == 2:
            row = ((ord(alphas[0]) - 64) * 26) + (ord(alphas[1]) - 64)
        else:
            row = ord(alphas[0]) - 64

        column = int(digits)

        return row, column

