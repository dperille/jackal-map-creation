import sys
import math
import Queue

class DifficultyMetrics:
  def __init__(self, map):
    self.map = map
    self.rows = len(map)
    self.cols = len(map[0])
    self.axes = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]

  def density(self, radius):
    dens = [[0 for i in range(self.cols)] for j in range(self.rows)]
    for r in range(self.rows):
      for c in range(self.cols):
        if self.map[r][c] == 0:
          dens[r][c] = self._densityOfTile(r, c, radius)
        else:
          dens[r][c] = (radius * 2) ** 2

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
  def dispersion(self, radius):
    disp = [[0 for i in range(self.cols)] for j in range(self.rows)]
    for r in range(self.rows):
      for c in range(self.cols):
        disp[r][c] = self._cellDispersion(r, c, radius)

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
          dist += 1

    return dist


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


  def _densityOfTile(self, row, col, radius):
    count = 0
    for r in range(row-radius, row+radius+1):
      for c in range(col-radius, col+radius+1):
        if r >= 0 and r < self.rows and c >= 0 and c < self.cols and (r!=row or c!=col):
          count += self.map[r][c]

    return count   


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
  # dist_nearest_obs cannot be zero, since it is impossible to navigate on an obstacle space
  def normalize_nearest_obs(self, dist_nearest_obs):
    return 1.0 / dist_nearest_obs


  # wrapper class for coordinates
  class Wrapper:

    def __init__(self, distance, row, col):
      self.dist = distance
      self.r = row
      self.c = col

    

    def __lt__(self, value):
        return self.dist < value.dist


