import math
import Queue
import numpy as np
  
class DifficultyMetrics:

  # map: C-space occupancy grid
  # path: list of points (row, col)
  # disp_radius: radius for dispersion
  def __init__(self, map, path, disp_radius):
    self.map = map
    self.rows = len(map)
    self.cols = len(map[0])
    self.axes = [(0, 1), (1, 1), (1, 0), (1, -1)] # vertical, horizontal, and 2 diagonals
    self.path = path
    self.radius = disp_radius

  # returns grid with the distance to closest obstacle at each point
  def closest_wall(self):
    dists = [[0 for i in range(self.cols)] for j in range(self.rows)]
    for r in range(self.rows):
      for c in range(self.cols):

        dists[r][c] = self._dist_closest_wall(r, c)

    return dists

  # returns grid with the average visibility at each point
  def avg_visibility(self):
    vis = [[0 for i in range(self.cols)] for j in range(self.rows)]
    for r in range(self.rows):
      for c in range(self.cols):
        vis[r][c] = self._avg_vis_cell(r, c)

    return vis

  # returns grid with the dispersion at each point
  # checks along 16 axes within the dispersion radius
  def dispersion(self):
    disp = [[0 for i in range(self.cols)] for j in range(self.rows)]
    for r in range(self.rows):
      for c in range(self.cols):
        disp[r][c] = self._cell_dispersion(r, c, self.radius)

    return disp

  # returns grid with the characteristic dimension at each point
  # characteristic dimension calculated in 2 directions for 4 axes
  def characteristic_dimension(self):
    cdr = [[0 for i in range(self.cols)] for j in range(self.rows)]
    for r in range(self.rows):
      for c in range(self.cols):
        if self.map[r][c] == 1:
          cdr[r][c] = 0

        cdr_min = self.rows + self.cols
        for axis in self.axes:
          cdr_min = min(cdr_min, self._distance(r, c, axis))

        cdr[r][c] = cdr_min

    return cdr

  # returns the distance along the axis in both directions, not including (r, c)
  def _distance(self, r, c, axis):
    if self.map[r][c] == 1:
      return -1

    # check axis in both directions
    reverse_axis = (axis[0] * -1, axis[1] * -1)
    dist = 0
    for move in [axis, reverse_axis]:
      r_curr = r
      c_curr = c

      # move in axis direction until an obstacle is found
      while self.map[r_curr][c_curr] != 1:
        r_curr += move[0]
        c_curr += move[1]

        if not self._in_map(r_curr, c_curr):
          break

        # add the distance traveled to the total
        if self.map[r_curr][c_curr] != 1:
          dist += math.sqrt(move[0] ** 2 + move[1] ** 2)

    return dist


  # a and b are tuples (row, col)
  def _dist_between_points(self, a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

  # path is list of points as tuples (row, col)
  # returns tortuosity calculated using the formula (arc length / chord length)
  def tortuosity(self):
    # calculate arc length
    arc_len = 0.0
    for i in range(1, len(self.path)):
      arc_len += self._dist_between_points(self.path[i - 1], self.path[i])
      
    # calculate chord length
    chord_len = self._dist_between_points(self.path[0], self.path[-1])
    return arc_len / chord_len

  # returns the cell dispersion within the radius
  def _cell_dispersion(self, r, c, radius):
    if self.map[r][c] == 1:
      return -1

    axes_wall = []
    # four cardinal, four diagonal, and one in between each (slope +- 1/2 or +-2)
    for move in [(0, 1), (1, 2), (1, 1), (2, 1), (1, 0), (2, -1), (1, -1), (1, -2), (0, -1), (-2, -1), (-1, -1), (-1, -2), (-1, 0), (-2, 1), (-1, 1), (-1, 2)]:
      count = 0
      wall = False
      r_curr = r
      c_curr = c
      while count < radius and not wall:
        r_curr += move[0]
        c_curr += move[1]

        if r_curr < 0 or r_curr >= self.rows or c_curr < 0 or c_curr >= self.cols:
          break

        if self.map[r_curr][c_curr] == 1:
          wall = True

        # count the in-between axes as two steps
        if move[0] == 2 or move[1] == 2:
          count += 2
        else:
          count += 1
      
      if wall:
        axes_wall.append(True)
      else:
        axes_wall.append(False)

    # count the number of changes in this cell's field of view
    change_count = 0
    for i in range(len(axes_wall)-1):
      if axes_wall[i] != axes_wall[i+1]:
        change_count += 1

    if axes_wall[0] != axes_wall[15]:
      change_count += 1

    return change_count

  # returns the average visibility at the point (r, c)
  def _avg_vis_cell(self, r, c):
    total_vis = 0.0
    num_axes = 0
    for r_move in [-1, 0, 1]:
      for c_move in [-1, 0, 1]:
        if r_move == 0 and c_move == 0:
          continue

        this_vis = 0
        r_curr = r
        c_curr = c
        wall_found = False
        while not wall_found:
          if not self._in_map(r_curr, c_curr):
            break

          if self.map[r_curr][c_curr] == 1:
            wall_found = True
          else:
            this_vis += math.sqrt((r_move ** 2) + (c_move ** 2))

          r_curr += r_move
          c_curr += c_move
        
        total_vis += this_vis
        num_axes += 1
    
    return total_vis / num_axes 


  # bounds check
  def _in_map(self, r, c):
    return r >= 0 and r < self.rows and c >= 0 and c < self.cols

  # returns the distance to the closest obstacle at point (r, c)
  # returns 0 if self.map[r][c] is an obstacle, 1 if an adjacent non-diagonal cell is an obstacle, etc.
  def _dist_closest_wall(self, r, c):
    pq = Queue.PriorityQueue()
    first_wrapper = self.Wrapper(0, r, c)
    pq.put(first_wrapper)
    visited = {(r, c) : first_wrapper}

    while not pq.empty():
      point = pq.get()
      if self.map[point.r][point.c] == 1: # found an obstacle!
        return point.dist
      else:
        # enqueue all neighbors if they are in the map and have not been visited
        for row in range(point.r - 1, point.r + 2):
          for col in range(point.c - 1, point.c + 2):
            if self._in_map(row, col) and (row, col) not in visited:
              dist = math.sqrt((row - r) ** 2 + (col - c) ** 2)
              neighbor = self.Wrapper(dist, row, col)
              pq.put(neighbor)
              visited[(row, col)] = neighbor

    # in case the queue is empty before a wall is found (shouldn't happen),
    # the farthest a cell can be from a wall is half the board, since the top and bottom rows are all walls
    return (self.rows - 1) / 2

  # wrapper class for coordinates
  class Wrapper:

    def __init__(self, distance, row, col):
      self.dist = distance
      self.r = row
      self.c = col

    def __lt__(self, value):
      return self.dist < value.dist
 
  # returns a list of the unnormalized metrics, averaged over the path
  # metrics order: distance to closest wall, average visibility, dispersion,
  # characteristic dimension, and tortuosity
  def avg_all_metrics(self):
    result = []
    total = 0.0

    # closest wall
    total = 0.0
    for row, col in self.path:
      total += self._dist_closest_wall(row, col)
    result.append(total / len(self.path))  
    
    # average visibility
    total = 0.0
    for row, col in self.path:
      total += self._avg_vis_cell(row, col)
    result.append(total / len(self.path)) 

    # dispersion
    total = 0.0
    for row, col in self.path:
      total += self._cell_dispersion(row, col, self.radius)
    result.append(total / len(self.path))

    # characteristic dimension
    total = 0.0
    char_dim_grid = self.characteristic_dimension()
    for row, col in self.path:
      total += char_dim_grid[row][col]
    result.append(total / len(self.path))

    # tortuosity
    tort = self.tortuosity()
    result.append(tort)

    return result


def load_data(cspace_file, path_file):
  cspace_grid = np.load(cspace_file)
  path = np.load(path_file)

  return cspace_grid, path

# load all c-spaces and paths, calculate metrics, and save
def main(num_files=300):
  dir_name = 'test_data/'
  path_file = 'path_files/path_%d.npy'
  cspace_file = 'cspace_files/cspace_%d.npy'
  metrics_file = 'metrics_files/metrics_%d.npy'
  disp_radius = 3
  for i in range(num_files):
    cspace, path = load_data(dir_name + cspace_file % i, dir_name + path_file % i)
    diffs = DifficultyMetrics(cspace, path, disp_radius)

    metrics = np.asarray(diffs.avg_all_metrics())
    np.save(dir_name + metrics_file % i, metrics)
      
if __name__ == "__main__":
  main()
