import math
import Queue
import numpy as np
  
class DifficultyMetrics:
  # radius used for density and dispersion
  def __init__(self, map, path, radius):
    self.map = map
    self.rows = len(map)
    self.cols = len(map[0])
    self.axes = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
    self.path = path
    self.radius = radius

  def density(self):
    dens = [[0 for i in range(self.cols)] for j in range(self.rows)]
    for r in range(self.rows):
      for c in range(self.cols):
        if self.map[r][c] == 0:
          dens[r][c] = self._densityOfTile(r, c, self.radius)
        else:
          dens[r][c] = (self.radius * 2) ** 2

    return dens

  def closestWall(self):
    dists = [[0 for i in range(self.cols)] for j in range(self.rows)]
    for r in range(self.rows):
      for c in range(self.cols):

        dists[r][c] = self._distToClosestWall(r, c)

    return dists

  def avgVisibility(self):
    vis = [[0 for i in range(self.cols)] for j in range(self.rows)]
    for r in range(self.rows):
      for c in range(self.cols):
        vis[r][c] = self._avgVisCell(r, c)

    return vis

  # calculates the number of changes betweeen open & wall
  # in its field of view (along 16 axes)
  def dispersion(self):
    disp = [[0 for i in range(self.cols)] for j in range(self.rows)]
    for r in range(self.rows):
      for c in range(self.cols):
        disp[r][c] = self._cellDispersion(r, c, self.radius)

    return disp

  def characteristic_dimension(self):
    cdr = [[0 for i in range(self.cols)] for j in range(self.rows)]
    for r in range(self.rows):
      for c in range(self.cols):
        if self.map[r][c] == 1:
          cdr[r][c] = 0

        isovist_dists = []
        for axis in self.axes:
          isovist_dists.append(self._distance(r, c, axis))

        cdr[r][c] = min(isovist_dists)

    return cdr

  def axis_width(self, axis):
    width = [[0 for i in range(self.cols)] for j in range(self.rows)]
    for r in range(self.rows):
      for c in range(self.cols):
        width[r][c] = self._distance(r, c, axis)

    return width

  # currently returns a value between 0 and board width/length - 1
  def _distance(self, r, c, axis):
    if self.map[r][c] == 1:
      return -1
    
    reverse_axis = (axis[0] * -1, axis[1] * -1)
    dist = 0
    for move in [axis, reverse_axis]:
      r_curr = r
      c_curr = c
      while self.map[r_curr][c_curr] != 1:
        r_curr += move[0]
        c_curr += move[1]

        if r_curr < 0 or r_curr >= self.rows or c_curr < 0 or c_curr >= self.cols:
          break

        if self.map[r_curr][c_curr] != 1:
          dist += math.sqrt(move[0] ** 2 + move[1] ** 2)

    return dist

  # dist is the result of calling _dist on an empty cell
  # returns value between 0 and 1
  def normalize_dist(self, dist):
    dist += 1
    return 1.0 / dist

  # a and b are points (2-tuples)
  def _dist_between_points(self, a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

  # path is list of points (2-tuples)
  def tortuosity(self):
    arc_len = 0.0
    for i in range(1, len(self.path)):
      arc_len += self._dist_between_points(self.path[i - 1], self.path[i])
      
    chord_len = self._dist_between_points(self.path[0], self.path[-1])
    return arc_len / chord_len

  def normalize_tortuosity(self, tort):
    return (-1.0 / tort) + 1

  def _cellDispersion(self, r, c, radius):
    if self.map[r][c] == 1:
      return -1

    axes_wall = []
    # four cardinal, four diagonal, and one in between each (slope +- 1/2 or 2)
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

  # param disperson is the return value of calling _cellDispersion on a cell
  # returns value between 0 and 1
  # _cellDispersion returns a value between 0 and 16, since it checks 16 directions
  def normalize_dispersion(self, disp):
    return disp / 16.0

  def _avgVisCell(self, r, c):
    total_vis = 0
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
          if r_curr < 0 or r_curr >= self.rows or c_curr < 0 or c_curr >= self.cols:
            break

          if self.map[r_curr][c_curr] == 1:
            wall_found = True
          else:
            this_vis += 1

          r_curr += r_move
          c_curr += c_move
        
        # if ran out of bounds before finding wall, don't count
        if wall_found:
          total_vis += this_vis
          num_axes += 1
    
    return total_vis / num_axes

  # avgVis is the return value of a call to _avgVisCell
  def normalize_avgVis(self, avgVis):
    return 1.0 / avgVis

  def _densityOfTile(self, row, col, radius):
    count = 0
    for r in range(row-radius, row+radius+1):
      for c in range(col-radius, col+radius+1):
        if r >= 0 and r < self.rows and c >= 0 and c < self.cols and (r!=row or c!=col):
          count += self.map[r][c]

    return count   

  # density is the return value of a call to _densityOfTile
  # _densityOfTile returns a value in range [0, (2*radius + 1) ^ 2 - 1]
  def normalize_density(self, dens, radius):
    highest_possible = (2 * radius + 1) ** 2.0
    return dens / highest_possible

  # simple bounds check
  def _isInMap(self, r, c):
    return r >= 0 and r < self.rows and c >= 0 and c < self.cols

  # returns a value in range [0, (self.rows - 1) / 2]
  # returns 0 if self.map[r][c] is an obstacle, 1 if an adjacent, non-diagonal cell is an obstacle, etc.
  def _distToClosestWall(self, r, c):
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
            if self._isInMap(row, col) and (row, col) not in visited:
              dist = math.sqrt((row - r) ** 2 + (col - c) ** 2)
              neighbor = self.Wrapper(dist, row, col)
              pq.put(neighbor)
              visited[(row, col)] = neighbor

    # in case the queue is empty before a wall is found (shouldn't happen),
    # the farthest a cell can be from a wall is half the board, since the top and bottom rows are all walls
    return (self.rows - 1) / 2

  # given the distance to the nearest obstacle, return a value in range (0, 1]
  # this value is supposed to approximate difficulty wrt distance to nearest obstacle
  def normalize_closest_wall(self, dist_closest_wall):
    return 1.0 / dist_closest_wall

  # wrapper class for coordinates
  class Wrapper:

    def __init__(self, distance, row, col):
      self.dist = distance
      self.r = row
      self.c = col

    

    def __lt__(self, value):
      return self.dist < value.dist

  # return a list of the normalized average for all metrics
  # metrics are averaged over each point in the path
  # old version
  def avg_all_metrics_norm(self):
    result = []

    total = 0.0
    running_total = 0.0

    # density
    for row, col in self.path:
      total += self._densityOfTile(row, col, self.radius)
    norm_avg = self.normalize_density(total / len(self.path), self.radius)
    running_total += norm_avg
    result.append(norm_avg)

    # closest wall
    total = 0.0
    for row, col in self.path:
      total += self._distToClosestWall(row, col)
    norm_avg = self.normalize_closest_wall(total / len(self.path))
    running_total += norm_avg
    result.append(norm_avg)  
    
    # average visibility
    total = 0.0
    for row, col in self.path:
      total += self._avgVisCell(row, col)
    norm_avg = self.normalize_avgVis(total / len(self.path))
    running_total += norm_avg
    result.append(norm_avg) 

    # dispersion
    total = 0.0
    for row, col in self.path:
      total += self._cellDispersion(row, col, self.radius)
    norm_avg = self.normalize_dispersion(total / len(self.path))
    running_total += norm_avg
    result.append(norm_avg)

    # characteristic dimension
    total = 0.0
    char_dim_grid = self.characteristic_dimension()
    for row, col in self.path:
      total += char_dim_grid[row][col]
    norm_avg = self.normalize_dist(total / len(self.path))
    running_total += norm_avg
    result.append(norm_avg)

    # tortuosity
    tort = self.tortuosity()
    norm_avg = self.normalize_tortuosity(tort)
    running_total += norm_avg
    result.append(norm_avg)

    return result

  # returns a list of the metrics, averaged over the path
  # unnormalized
  def avg_all_metrics(self):
    result = []

    total = 0.0

    # closest wall
    total = 0.0
    for row, col in self.path:
      total += self._distToClosestWall(row, col)
    result.append(total / len(self.path))  
    
    # average visibility
    total = 0.0
    for row, col in self.path:
      total += self._avgVisCell(row, col)
    result.append(total / len(self.path)) 

    # dispersion
    total = 0.0
    for row, col in self.path:
      total += self._cellDispersion(row, col, self.radius)
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
  dir_name = "dataset/"
  path_file = "path_files/path_%d.npy"
  cspace_file = "cspace_files/cspace_%d.npy"
  metrics_file = "metrics_files/metrics_%d.npy"
  radius = 3
  for i in range(num_files):
    cspace, path = load_data(dir_name + cspace_file % i, dir_name + path_file % i)
    diffs = DifficultyMetrics(cspace, path, radius)

    metrics = np.asarray(diffs.avg_all_metrics())
    np.save(dir_name + metrics_file % i, metrics)
    
if __name__ == "__main__":
  main()
