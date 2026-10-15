
from docplex.cp.model import CpoModel


def main():
    n = 8
    model = CpoModel(name="n_queens_cp")

    # Mỗi biến là cột đặt quân hậu tương ứng với một hàng.
    q = [model.integer_var(0, n - 1, name=f"q_{r}") for r in range(n)]

    # Mỗi cột chỉ có một quân hậu.
    model.add(model.all_diff(q))

    # Không có hai quân hậu cùng đường chéo.
    for r1 in range(n):
        for r2 in range(r1 + 1, n):
            model.add(q[r1] - q[r2] != r1 - r2)
            model.add(q[r1] - q[r2] != r2 - r1)

    solution = model.solve(TimeLimit=10)

    if solution is None:
        print("Không tìm thấy lời giải.")
        return

    queens = [solution.get_value(v) for v in q]

    assert len(set(queens)) == n
    assert len({r - c for r, c in enumerate(queens)}) == n
    assert len({r + c for r, c in enumerate(queens)}) == n

    print("Solver status:", solution.get_solve_status())
    print("Solution:", queens)
    print("Validation: PASS")


if __name__ == "__main__":
    main()
