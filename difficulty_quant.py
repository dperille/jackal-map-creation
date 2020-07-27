import sys

class DifficultyMetrics:
  def __init__(self, map):
    self.map = map
    self.rows = len(map)
    self.cols = len(map[0])

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
        dists[r][c] = self._distToClosestWall(r, c, 0, sys.maxint)

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

  # determines how far a given cell is from a wall (non-diagonal)
  def _distToClosestWall(self, r, c, currCount, currBest):
    if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
      return sys.maxint

    if self.map[r][c] == 1:
      return 0

    if currCount >= currBest:
      return sys.maxint

    bestUp = 1 + self._distToClosestWall(r-1, c, currCount+1, currBest)
    if bestUp < currBest:
      currBest = bestUp
    
    bestDown = 1 + self._distToClosestWall(r+1, c, currCount+1, currBest)
    if bestDown < currBest:
      currBest = bestDown
    
    bestLeft = 1 + self._distToClosestWall(r, c-1, currCount+1, currBest)
    if bestLeft < currBest:
      currBest = bestLeft

    bestRight = 1 + self._distToClosestWall(r, c+1, currCount+1, currBest)

    return min(bestUp, bestDown, bestLeft, bestRight)