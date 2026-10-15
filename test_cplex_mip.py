
import time

from docplex.mp.model import Model


def solve_n_queens(n: int = 8) -> None:
    model = Model(name=f"n_queens_mip_{n}")

    # x[r, c] = 1 nếu đặt quân hậu tại hàng r, cột c.
    x = {
        (r, c): model.binary_var(name=f"x_{r}_{c}")
        for r in range(n)
        for c in range(n)
    }

    # Mỗi hàng có đúng một quân hậu.
    for r in range(n):
        model.add_constraint(
            model.sum(x[r, c] for c in range(n)) == 1
        )

    # Mỗi cột có đúng một quân hậu.
    for c in range(n):
        model.add_constraint(
            model.sum(x[r, c] for r in range(n)) == 1
        )

    # Mỗi đường chéo có nhiều nhất một quân hậu.
    for r1 in range(n):
        for r2 in range(r1 + 1, n):
            distance = r2 - r1
            for c1 in range(n):
                for c2 in (c1 - distance, c1 + distance):
                    if 0 <= c2 < n:
                        model.add_constraint(
                            x[r1, c1] + x[r2, c2] <= 1
                        )

    start = time.perf_counter()
    solution = model.solve(log_output=True)
    elapsed = time.perf_counter() - start

    print(f"\nN = {n}")
    print(f"Solver status: {model.solve_details.status}")
    print(f"Solve time (s): {elapsed:.6f}")

    if solution is None:
        print("Không tìm thấy lời giải.")
        return

    # Trích xuất cột của quân hậu ở mỗi hàng.
    queens = []
    for r in range(n):
        cols = [
            c for c in range(n)
            if solution.get_value(x[r, c]) > 0.5
        ]
        if len(cols) != 1:
            raise AssertionError(
                f"Hàng {r} có {len(cols)} quân hậu."
            )
        queens.append(cols[0])

    # Xác thực độc lập, không dựa vào trạng thái solver.
    assert len(set(queens)) == n, "Có hai quân hậu cùng cột."
    assert len({r - c for r, c in enumerate(queens)}) == n
    assert len({r + c for r, c in enumerate(queens)}) == n

    print("Solution:", queens)
    print("Validation: PASS")


if __name__ == "__main__":
    solve_n_queens(8)
