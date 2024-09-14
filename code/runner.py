import colreg2
import numpy as np

#DATA
x = np.arange(-0, 50, 1)
y = np.arange(-0, 50, 1)
goal = [45, 45]
s = 9
r = 0.5
alpha = 50
beta = 350
seek_points = np.array([[10, 0]])

colreg2.main(x, y, goal, s, r, alpha, beta, seek_points)
