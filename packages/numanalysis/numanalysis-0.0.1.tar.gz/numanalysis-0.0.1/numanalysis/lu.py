def verifCarre(A: list[list]) -> bool:
    n = len(A)
    return all(len(row) == n for row in A)


def llu_unit(A: list[list]) -> list[list]:
    if not verifCarre(A):
        raise ValueError("Matrice non carrée")

    n = len(A)
    L = [[0.0 for _ in range(n)] for _ in range(n)]
    U = [[0.0 for _ in range(n)] for _ in range(n)]

    for j in range(n):
        # Diagonale unité
        L[j][j] = 1.0

        # Calcul des coefficients de U (ligne j)
        for i in range(j + 1):
            somme = sum(L[i][k] * U[k][j] for k in range(i))
            U[i][j] = A[i][j] - somme

        # Calcul des coefficients de L (colonne j)
        for i in range(j + 1, n):
            somme = sum(L[i][k] * U[k][j] for k in range(j))
            if U[j][j] == 0:
                raise ZeroDivisionError(f"U[{j}][{j}] = 0, décomposition impossible sans pivot")
            L[i][j] = (A[i][j] - somme) / U[j][j]

    return L

def ulu_unit(A: list[list]) -> list[list]:
    if not verifCarre(A):
        raise ValueError("Matrice non carrée")

    n = len(A)
    L = [[0.0 for _ in range(n)] for _ in range(n)]
    U = [[0.0 for _ in range(n)] for _ in range(n)]

    for j in range(n):
        # Diagonale unité
        L[j][j] = 1.0

        # Calcul des coefficients de U (ligne j)
        for i in range(j + 1):
            somme = sum(L[i][k] * U[k][j] for k in range(i))
            U[i][j] = A[i][j] - somme

        # Calcul des coefficients de L (colonne j)
        for i in range(j + 1, n):
            somme = sum(L[i][k] * U[k][j] for k in range(j))
            if U[j][j] == 0:
                raise ZeroDivisionError(f"U[{j}][{j}] = 0, décomposition impossible sans pivot")
            L[i][j] = (A[i][j] - somme) / U[j][j]

    return U