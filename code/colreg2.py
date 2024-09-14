#https://medium.com/nerd-for-tech/local-path-planning-using-virtual-potential-field-in-python-ec0998f490af
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random
import math
import occupancy_map_translator as omt


# def reverse_vector_length(vx, vy):
#     original_length = math.sqrt(vx**2 + vy**2)
#     limiting_length = 1650
#     if original_length < limiting_length:
#         return vx, vy
#     new_length = max(50, original_length - abs(original_length - limiting_length)) #!!!
#
#     unit_vx = vx / original_length
#     unit_vy = vy / original_length
#
#     new_vx = unit_vx * new_length
#     new_vy = unit_vy * new_length
#
#     return new_vx, new_vy   #näita


def add_goal(X, Y, s, r, loc, alpha, x, y):
    delx = np.zeros_like(X)
    dely = np.zeros_like(Y)
    for i in range(len(X)):
        for j in range(len(Y)):
            d = np.sqrt((loc[0] - X[i][j]) ** 2 + (loc[1] - Y[i][j]) ** 2)
            theta = np.arctan2(loc[1] - Y[i][j], loc[0] - X[i][j])
            if d < r:
                delx[i][j] = 0
                dely[i][j] = 0
            elif d >= r + s:
                delx[i][j] = alpha * s * np.cos(theta)
                dely[i][j] = alpha * s * np.sin(theta)
            else:
                delx[i][j] = alpha * (d - r) * np.cos(theta)
                dely[i][j] = alpha * (d - r) * np.sin(theta)
    return delx, dely


def plot_graph(X, Y, delx, dely, obj, fig, ax, loc, r, i, color, plot_vector_field):
    if plot_vector_field:
        ax.quiver(X, Y, delx, dely)
    ax.add_patch(plt.Circle(loc, r, color=color))
    ax.set_title(f'Ship path with {i} obstacles ')
    ax.annotate(obj, xy=loc, fontsize=10, ha="center")
    return ax


# Maybe soon not needed anymore
def generate_obstacle_location(obstacle_type, loc):
    if obstacle_type == 'green buoy':
        return [22, 30]
    elif obstacle_type == 'red buoy':
        return [27, 30]
    elif loc is None:
        return random.sample(range(10, 40), 2)
    else:
        return loc

# Maybe r will not be needed anymore
def calculate_vortex_angle_and_radius(obstacle_type):
    vortex_angle = 0.62 #näita
    r = 0.5  # default radius

    if obstacle_type == 'nonmoving':
        vortex_angle = 0
    elif obstacle_type == 'green buoy':
        vortex_angle = 0.62
        #r = 0.5
    elif obstacle_type == 'red buoy':
        vortex_angle = -0.62
        #r = 0.5

    return vortex_angle, r

def add_obstacle(X, Y, delx, dely, goal, loc, alpha, beta, obstacle_type, s, x, y):
    # generating random location of the obstacle if needed
    obstacle = generate_obstacle_location(obstacle_type, loc)

    vortex_angle, r = calculate_vortex_angle_and_radius(obstacle_type)

    for i in range(len(x)):
        for j in range(len(y)):
            d_goal = np.sqrt((goal[0] - X[i][j]) ** 2 + (goal[1] - Y[i][j]) ** 2)
            d_obstacle = np.sqrt((obstacle[0] - X[i][j]) ** 2 + (obstacle[1] - Y[i][j]) ** 2)
            theta_goal = np.arctan2(goal[1] - Y[i][j], goal[0] - X[i][j])
            theta_obstacle = np.arctan2(obstacle[1] - Y[i][j], obstacle[0] - X[i][j]) + vortex_angle

            if d_obstacle < r:
                delx[i][j] = -1 * np.sign(np.cos(theta_obstacle)) * 5 + 0
                dely[i][j] = -1 * np.sign(np.cos(theta_obstacle)) * 5 + 0
            elif d_obstacle > r + s:
                delx[i][j] += 0 - (alpha * s * np.cos(theta_obstacle)) * 0.1  #theta_goal
                dely[i][j] += 0 - (alpha * s * np.sin(theta_obstacle)) * 0.1
            else:  #elif d_obstacle <= r + s
                delx[i][j] += -beta * (s + r - d_obstacle) * np.cos(theta_obstacle)
                dely[i][j] += -beta * (s + r - d_obstacle) * np.sin(theta_obstacle)

            if d_goal <= r + s:
                delx[i][j] += (alpha * (d_goal - r) * np.cos(theta_goal))
                dely[i][j] += (alpha * (d_goal - r) * np.sin(theta_goal))
            elif d_goal > r + s:
                delx[i][j] += alpha * s * np.cos(theta_goal)
                dely[i][j] += alpha * s * np.sin(theta_goal)
            elif d_goal <= r:
                delx[i][j] = 0
                dely[i][j] = 0

            if d_obstacle <= r:
                delx[i][j] = -5000 * np.cos(theta_obstacle)
                dely[i][j] = -5000 * np.sin(theta_obstacle)
            elif d_obstacle <= 1.5 * r:
                delx[i][j] = -2500 * np.cos(theta_obstacle)
                dely[i][j] = -2500 * np.sin(theta_obstacle)
            # elif d_obstacle <= 2.0 * r:
            #     delx[i][j] = -1000 * np.cos(theta_obstacle)
            #     dely[i][j] = -1000 * np.sin(theta_obstacle)

    return delx, dely, obstacle, r


def calculate_angle(a, b):
    try:
        cos_theta = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    except Exception:
        return 15
    # Ensure the cosine value is within valid range to avoid numerical issues
    cos_theta = np.clip(cos_theta, -1, 1)
    # Calculate the angle in radians and then convert to degrees
    angle = np.arccos(cos_theta) * (180 / np.pi)
    return angle


def adjust_new_pos(old_pos, current_pos, new_pos):
    old_pos = np.array(old_pos)
    current_pos = np.array(current_pos)
    new_pos = np.array(new_pos)

    vector_old_current = current_pos - old_pos
    vector_current_new = new_pos - current_pos

    angle = calculate_angle(vector_old_current, vector_current_new)

    if angle < 15: #näita
        length_current_new = np.linalg.norm(vector_current_new)
        direction = vector_old_current / np.linalg.norm(vector_old_current)
        new_pos = current_pos + direction * length_current_new
    elif angle > 90:
        # Find a direction that is perpendicular to old_current
        # For a 2D vector [x, y], a perpendicular direction can be [-y, x] or [y, -x]
        perpendicular_direction = np.array([-vector_old_current[1], vector_old_current[0]])
        perpendicular_direction /= np.linalg.norm(perpendicular_direction)  # Normalize
        length_current_new = np.linalg.norm(vector_current_new)
        # Choose the direction that makes the angle 90 degrees
        new_pos = current_pos + perpendicular_direction * length_current_new

    return new_pos.tolist()


def update_position(current_pos, old_pos, delx, dely, step):
    i, j = int(current_pos[1]), int(current_pos[0])

    i = max(0, min(i, 49))
    j = max(0, min(j, 49))

    new_x = current_pos[0] + (delx[i][j] * step)
    new_y = current_pos[1] + (dely[i][j] * step)

    new_x, new_y = adjust_new_pos(old_pos, current_pos, [new_x, new_y])

    print([delx[i][j], dely[i][j]])

    return np.array([new_x, new_y])


# def adjust_vector_lengths(X, Y, delx, dely):
#     delx_ = np.zeros_like(X)
#     dely_ = np.zeros_like(Y)
#     for i in range(50):
#         for k in range(50):
#             vx_, vy_ = reverse_vector_length(delx[i][k], dely[i][k])
#             delx_[i][k] = vx_
#             dely_[i][k] = vy_
#     return delx_, dely_




class Scene:
    def __init__(self, delx, dely, seek_points, loc_list, r, s, goal, alpha, beta, type_list, x, y, X, Y, obstacles, number_of_obstacles):
        self.delx = delx
        self.dely = dely
        self.seek_points = seek_points
        self.loc_list = loc_list
        self.r = r
        self.s = s
        self.goal = goal
        self.alpha = alpha
        self.beta = beta
        self.type_list = type_list
        self.x = x
        self.y = y
        self.X = X
        self.Y = Y
        self.obstacles = obstacles
        self.number_of_obstacles = number_of_obstacles

# #DATA
# x = np.arange(-0, 50, 1)
# y = np.arange(-0, 50, 1)
# goal = [25, 40]
# s = 9
# r = 0.5
# alpha = 50
# beta = 350
# seek_points = np.array([[25, 0]])
#


def main(x, y, goal, s, r, alpha, beta, seek_points):
    # Animation update function
    def update(dummy):
        ax.clear()
        plot_graph(scene.X, scene.Y, scene.delx, scene.dely, 'Goal', fig, ax, scene.goal, scene.r, 0, 'b', False)
        scene.delx, scene.dely = add_goal(scene.X, scene.Y, scene.s, scene.r, scene.goal, scene.alpha, scene.x, scene.y)

        counter = 0
        for j in range(scene.number_of_obstacles):
            r2 = 0.5
            obstacle_type = scene.type_list[j]
            loc = scene.loc_list[j]

            if obstacle_type == 'ship' and counter == 0 and scene.obstacles[j][0] > 5 and scene.obstacles[j][1] < 45 and scene.obstacles[j][0] < 45:
                scene.obstacles[j][0] += 0.25
                scene.obstacles[j][1] -= 0.25
            elif obstacle_type == 'ship' and counter == 1 and scene.obstacles[j][0] > 5 and scene.obstacles[j][1] < 45 and scene.obstacles[j][0] < 45:
                scene.obstacles[j][0] -= 0.365
                scene.obstacles[j][1] += 0.365
            elif obstacle_type == 'ship' and counter == 3 and scene.obstacles[j][0] > 5 and scene.obstacles[j][1] < 45:
                scene.obstacles[j][0] -= 0.44
            counter += 1
            # elif j == 1:
            #     obstacles[j][1] -= 0.1
            scene.delx, scene.dely, loc, r = add_obstacle(scene.X, scene.Y, scene.delx, scene.dely, scene.goal, loc,
                                                          scene.alpha, scene.beta, obstacle_type, scene.s, scene.x,
                                                          scene.y)  # loc_old!!!!
            plot_graph(scene.X, scene.Y, scene.delx, scene.dely, 'Obstacle', fig, ax, loc, r2, j + 1, 'm',
                       False)  # j == number_of_obstacles - 1
            # !!!
            # plot_graph(X, Y, delx, dely, 'Obstacle', fig, ax, [loc[0]+1, loc[1]], r2, j + 1, 'm', False)
            # print(obstacles)

        # delx_, dely_ = adjust_vector_lengths(X, Y, scene.delx, scene.dely)

        # path
        current_pos = scene.seek_points[-1]
        try:
            old_pos = scene.seek_points[-2]
        except Exception:
            print("aaaaaa")
            old_pos = current_pos
        new_pos = update_position(current_pos, old_pos, scene.delx, scene.dely, 0.0002)
        scene.seek_points = np.append(scene.seek_points, [new_pos], axis=0)
        ax.plot(scene.seek_points[:, 0], scene.seek_points[:, 1], 'ro')  # Plotting the path

        ax.quiver(scene.X, scene.Y, scene.delx, scene.dely)
        velocity_magnitude = np.sqrt(scene.delx ** 2 + scene.dely ** 2)
        ax.streamplot(scene.X, scene.Y, scene.delx, scene.dely, color=velocity_magnitude,
                      start_points=np.array([current_pos]), integration_direction='forward')
        ax.annotate("Goal", xy=scene.goal, fontsize=10, ha="center")
        ax.set_title('Animated path taken by the ship')

    def setup(x, y, goal, s, r, alpha, beta, seek_points):
        loc_list, type_list, number_of_obstacles = omt.get_obstacle_locations_and_types(omt.o, omt.type_dict)

        X, Y = np.meshgrid(x, y)
        obstacles = []
        delx, dely = add_goal(X, Y, s, r, goal, alpha, x, y)
        plot_graph(X, Y, delx, dely, 'Goal', fig, ax, goal, r, 0, 'b', False)
        r2 = 1

        for j in range(number_of_obstacles):
            obstacle_type = type_list[j]
            loc = loc_list[j]
            delx, dely, loc, r = add_obstacle(X, Y, delx, dely, goal, loc, alpha, beta, obstacle_type, s, x, y)
            obstacles.append(loc)
            plot_graph(X, Y, delx, dely, 'Obstacle', fig, ax, loc, r2, j + 1, 'm', False)
        return Scene(delx, dely, seek_points, loc_list, r, s, goal, alpha, beta, type_list, x, y, X, Y, obstacles,
                     number_of_obstacles)

    fig, ax = plt.subplots(figsize=(10, 10))
    scene = setup(x, y, goal, s, r, alpha, beta, seek_points)
    ani = FuncAnimation(fig, lambda frame: update(1), frames=np.linspace(0, 30, 300), repeat=True)
    #
    plt.show()

