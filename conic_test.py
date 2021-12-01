"""
Test for transforming conic to BSpline Curves
Uses algorithm specified in https://www.programmerall.com/article/4928804700/
"""
from typing import Tuple
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt, floor, ceil


def to_canonical_form(a, b, c, d, e, f) -> Tuple[float, float]:
    """finds a, b of cannonical form"""
    sol = np.array([[a, b/2], [b/2, c]])
    conic_matrix = np.array([[a, b/2, d/2], [b/2, c, e/2], [d/2, e/2, f]])

    eig = np.linalg.eigvals(sol)
    l1, l2 = eig  # lambda 1 and lambda 2
    S = np.linalg.det(conic_matrix)

    cann_a = -S/(l1**2 * l2)
    cann_b = -S/(l1 * l2**2)
    return cann_a, cann_b


def x0(a, b, c, d, e, f, y) -> float:
    return (-b*y - d + sqrt(-4*a*c*y**2 - 4*a*e*y -
                            4*a*f + b**2*y**2 + 2*b*d*y + d**2))/(2*a)


def x1(a, b, c, d, e, f, y) -> float:
    return -(b*y + d + sqrt(-4*a*c*y**2 - 4*a*e*y -
                            4*a*f + b**2*y**2 + 2*b*d*y + d**2))/(2*a)


def get_x(a, b, c, d, e, f, y) -> float:
    answers = []
    try:
        answers.append(x0(a, b, c, d, e, f, y))
    except ValueError:
        pass

    try:
        answers.append(x1(a, b, c, d, e, f, y))
    except ValueError:
        pass

    return answers


a, b, c, d, e, f = 2, 0.000, 3.0, 0.000, 0.0, -1.0,


cann_a, cann_b = to_canonical_form(a, b, c, d, e, f)

dt = 100
step = 10
test_xs = [x/dt for x in range(floor(-(cann_a+1) * dt), ceil((cann_a+1)*dt), step)]
xs = []
ys = []
for x in test_xs:
    if y := get_x(a, b, c, d, e, f, x):

        if len(y) == 2:
            ys += y
            xs += [x, x]
        else:
            ys += y
            xs.append(x)


plt.plot(xs, ys)
plt.show()
