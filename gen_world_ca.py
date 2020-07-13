import random
import sys
import datetime
import Queue
import math
import matplotlib.pyplot as plt
import Tkinter as tk

# define boilerplate code needed to write to .world file
with open("./world-boilerplate/world_boiler_start.txt") as f:
      world_boiler_start = f.read()
with open("./world-boilerplate/world_boiler_mid.txt") as f:
      world_boiler_mid = f.read()
with open("./world-boilerplate/world_boiler_end.txt") as f:
      world_boiler_end = f.read()
with open("./world-boilerplate/cylinder_define.txt") as f:
      cylinder_define = f.read()
with open("./world-boilerplate/cylinder_place.txt") as f:
      cylinder_place = f.read()

class MapGenerator():
  def __init__(self, rows, cols, randFillPct, seed=None, smoothIter=5):
    self.map = [[0 for i in range(cols)] for j in range(rows)]
    self.rows = rows
    self.cols = cols
    self.randFillPct = randFillPct
    self.seed = seed
    self.smoothIter = smoothIter

  def __call__(self):
    self._randomFill()
    for n in range(self.smoothIter):
      self._smooth()

  def _randomFill(self):
    if self.seed:
      random.seed(self.seed)

    for r in range(self.rows):
      for c in range(self.cols):
        if r == 0 or r == self.rows - 1:
          self.map[r][c] = 1
        else:
          self.map[r][c] = 1 if random.random() < self.randFillPct else 0

  def _smooth(self):
    newmap = [[self.map[r][c] for c in range(self.cols)] for r in range(self.rows)]
    for r in range(self.rows):
      for c in range(self.cols):
        # if more than 4 filled neighbors, fill this tile
        if self._tileNeighbors(r, c) > 4:
          newmap[r][c] = 1

        # if less than 2 filled neighbors, empty this one
        elif self._tileNeighbors(r, c) < 2:
          newmap[r][c] = 0

    self.map = newmap

  def _tileNeighbors(self, r, c):
    count = 0
    for i in range(r - 1, r + 2):
      for j in range(c - 1, c + 2):
        if self.isInMap(i, j):
          if i != r or j != c:
            count += self.map[i][j]

        # if on the top or bottom, add to wall neighbors
        elif i < 0 or i >= self.rows:
          count += 1
    
    return count

  def getMap(self):
    return self.map

  # use flood-fill algorithm to find the open region including (r, c)
  def _getRegion(self, r, c):
    queue = Queue.Queue(maxsize=0)
    region = [[0 for i in range(self.cols)] for j in range(self.rows)]
    size = 0

    if self.map[r][c] == 0:
      queue.put((r, c))
      region[r][c] = 1
      size += 1

    while not queue.empty():
      coord_r, coord_c = queue.get()

      # check four cardinal neighbors
      for i in range(coord_r-1, coord_r+2):
        for j in range(coord_c-1, coord_c+2):
          if self.isInMap(i, j) and (i == coord_r or j == coord_c):
            # if empty space and not checked yet
            if self.map[i][j] == 0 and region[i][j] == 0:
              # add to region and put in queue
              region[i][j] = 1
              queue.put((i, j))
              size += 1

    return region, size

  # returns the largest contiguous region with a tile in the leftmost column
  def biggestLeftRegion(self):
    maxSize = 0
    maxRegion = []
    for row in range(self.rows):
      region, size = self._getRegion(row, 0)

      if size > maxSize:
        maxSize = size
        maxRegion = region

    return maxRegion

  # returns the largest contiguous region with a tile in the rightmost column
  def biggestRightRegion(self):
    maxSize = 0
    maxRegion = []
    for row in range(self.rows):
      region, size = self._getRegion(row, self.cols-1)

      if size > maxSize:
        maxSize = size
        maxRegion = region

    return maxRegion

  def regionsAreConnected(self, regionA, regionB):
    for r in range(len(regionA)):
      for c in range(len(regionA[0])):
        if regionA[r][c] != regionB[r][c]:
          return False

        # if they share any common spaces, they're connected
        elif regionA[r][c] == 1 and regionB[r][c] == 1:
          return True

    return False

  def connectRegions(self, regionA, regionB):
    if self.regionsAreConnected(regionA, regionB):
      return

    print("Connecting separate regions")
    rightmostA = (-1, -1)
    leftmostB = (-1, self.cols - 1)

    for r in range(self.rows):
      for c in range(self.cols):
        if regionA[r][c] == 1 and c > rightmostA[1]:
          rightmostA = (r, c)
        if regionB[r][c] == 1 and c < leftmostB[1]:
          leftmostB = (r, c)

    lrchange = 0
    udchange = 0
    if rightmostA[1] < leftmostB[1]:
      lrchange = 1
    elif rightmostA[1] > leftmostB[1]:
      lrchange = -1
    if rightmostA[0] < leftmostB[0]:
      udchange = 1
    elif rightmostA[0] > leftmostB[0]:
      udchange = -1

    rmar = rightmostA[0]
    rmac = rightmostA[1]
    lmbr = leftmostB[0]
    lmbc = leftmostB[1]
    for count in range(1, abs(rmac-lmbc)+1):
      self.map[rmar][rmac+count * lrchange] = 0

    for count in range(1, abs(rmar-lmbr)+1):
      self.map[rmar+count*udchange][rmac+(lmbc-rmac)] = 0

  def isInMap(self, r, c):
    return r >= 0 and r < self.rows and c >= 0 and c < self.cols

  # returns a path between all points in the list points using A*
  def getPath(self, points):
    num_points = len(points)
    if num_points < 2:
      raise Exception("Path needs at least two points")
    
    # check if any points aren't empty
    for point in points:
      if self.map[point[0]][point[1]] == 1:
        raise Exception("The point (%d, %d) is a wall" % (point[0], point[1]))

    overall_path = []
    for n in range(num_points - 1):
      overall_path.append(points[n])

      # generate path between this point and the next one in the list
      a_star = AStarSearch(self.map)
      intermediate_path = a_star(points[n], points[n+1])
      
      # add to the overall path
      if n > 0:
        intermediate_path.pop(0)
      overall_path.extend(intermediate_path)

    return overall_path

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


class AStarSearch:
  def __init__(self, map):
    self.map = map
    self.map_rows = len(map)
    self.map_cols = len(map[0])

  def __call__(self, start_coord, end_coord):
    # initialize start and end nodes
    start_node = Node(None, start_coord)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end_coord)
    end_node.g = end_node.h = end_node.f = 0

    # initialize lists to track nodes we've visited or not
    visited = []
    not_visited = []

    # add start to nodes yet to be processed
    not_visited.append(start_node)

    # while there are nodes to process
    while len(not_visited) > 0:
      # get lowest cost next node
      curr_node = not_visited[0]
      curr_idx = 0
      for idx, node in enumerate(not_visited):
        if node.f < curr_node.f:
          curr_node = node
          curr_idx = idx

      # mark this node as processed
      not_visited.pop(curr_idx)
      visited.append(curr_node)

      # if this node is at end of the path, return
      if curr_node == end_node:
        return self.returnPath(curr_node)

      # limit turns to 45 degrees
      valid_moves_dict = {
        (0, 1): [(-1, 1), (0, 1), (1, 1)],
        (1, 1): [(0, 1), (1, 1), (1, 0)],
        (1, 0): [(1, 1), (1, 0), (1, -1)],
        (1, -1): [(1, 0), (1, -1), (0, -1)],
        (0, -1): [(1, -1), (0, -1), (-1, -1)],
        (-1, -1): [(0, -1), (-1, -1), (-1, 0)],
        (-1, 0): [(-1, -1), (-1, 0), (-1, 1)],
        (-1, 1): [(-1, 0), (-1, 1), (0, 1)]
      }

      valid_moves = []
      if curr_node == start_node:
        # if start node, can go any direction
        valid_moves = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
      else:
        # otherwise, can only go straight or 45 degree turn
        moving_direction = (curr_node.r - curr_node.parent.r, curr_node.c - curr_node.parent.c)
        valid_moves = valid_moves_dict.get(moving_direction)

      # find all valid, walkable neighbors of this node
      children = []
      for move in valid_moves:

        # calculate neighbor position
        child_pos = (curr_node.r + move[0], curr_node.c + move[1])
        
        # if outside the map, not possible
        if child_pos[0] < 0 or child_pos[0] >= self.map_rows or child_pos[1] < 0 or child_pos[1] >= self.map_cols:
          continue

        # if a wall tile, not possible
        if self.map[child_pos[0]][child_pos[1]] == 1:
          continue

        # also not possible to move between diagonal walls
        if move[0] != 0 and move[1] != 0 and self.map[curr_node.r+move[0]][curr_node.c] == 1 and self.map[curr_node.r][curr_node.c+move[1]] == 1:
          continue

        # if neighbor is possible to reach, add to list of neighbors
        child_node = Node(curr_node, child_pos)
        children.append(child_node)


      # loop through all walkable neighbors of this node
      for child in children:

        # if neighbor already visited, not usable
        if child in visited:
          continue

        # calculate f, g, h values
        child.g += 1
        child.h = math.sqrt(((child.r - end_node.r) ** 2) + ((child.c - end_node.c) ** 2))
        child.f = child.g + child.h

        # if this node is already in the unprocessed list
        # with a g-value lower than what we have, don't add it
        if len([i for i in not_visited if child == i and child.g > i.g]) > 0:
          continue

        not_visited.append(child)

  # generate the path from start to end
  def returnPath(self, end_node):
    path = []
    curr_node = end_node
    while curr_node != None:
      path.append((curr_node.r, curr_node.c))
      curr_node = curr_node.parent

    path.reverse()
    return path


class Node:
  def __init__(self, parent, coord):
    self.parent = parent
    self.r = coord[0]
    self.c = coord[1]

    self.g = 0
    self.h = 0
    self.f = 0

  def __eq__(self, other):
    return self.r == other.r and self.c == other.c


class WorldWriter():

  def __init__(self, filename):
    self.file = open(filename, "w")
    self.numCylinders = 0
    self.cylinderList = []
    self._writeStarterBoiler()

  def _writeStarterBoiler(self):
    self.file.write(world_boiler_start)

  def createCylinder(self, x, y, z, a, b, c):
    self.file.write(cylinder_define % (
        self.numCylinders, x, y, z, a, b, c
    ))
    
    self.cylinderList.append([x, y, z, a, b, c])
    self.numCylinders += 1

  def _writeMidBoiler(self):
      self.file.write(world_boiler_mid)

  def placeCylinders(self):
    self._writeMidBoiler()

    for i in range(self.numCylinders):
      self.file.write(cylinder_place % (
          i, self.cylinderList[i][0], self.cylinderList[i][1], self.cylinderList[i][2], 
          self.cylinderList[i][3], self.cylinderList[i][4], self.cylinderList[i][5], 
          self.cylinderList[i][0], self.cylinderList[i][1], self.cylinderList[i][2], 
          self.cylinderList[i][3], self.cylinderList[i][4], self.cylinderList[i][5], 
      ))

    self._writeEndBoiler()

  def _writeEndBoiler(self):
    self.file.write(world_boiler_end)

  def close(self):
    self.file.close()
   

class Display:
  def __init__(self, map, map_with_path, density_radius, dispersion_radius):
    self.map = map
    self.map_with_path = map_with_path
    self.density_radius = density_radius
    self.dispersion_radius = dispersion_radius
  
    diff = DifficultyMetrics(map)
    self.metrics = {
      "closestDist": diff.closestWall(),
      "density": diff.density(density_radius),
      "avgVis": diff.avgVisibility(),
      "dispersion": diff.dispersion(dispersion_radius),
      "leftright_width": diff.axis_width((0, 1)),
      "updown_width": diff.axis_width((1, 0)),
      "pos_diag_width": diff.axis_width((-1, 1)),
      "neg_diag_width": diff.axis_width((1, 1)),
    }

  def __call__(self):
    fig, ax = plt.subplots(3, 3)
    
    

    # map and path
    map_plot = ax[0][0].imshow(self.map_with_path, cmap='Greys', interpolation='nearest')
    map_plot.axes.get_xaxis().set_visible(False)
    map_plot.axes.get_yaxis().set_visible(False)
    ax[0][0].set_title("Map and A* path")

    # closest wall distance
    dists = self.metrics.get("closestDist")
    dist_plot = ax[0][1].imshow(dists, cmap='RdYlGn', interpolation='nearest')
    dist_plot.axes.get_xaxis().set_visible(False)
    dist_plot.axes.get_yaxis().set_visible(False)
    ax[0][1].set_title("Distance to \nclosest obstacle")
    dist_cbar = fig.colorbar(dist_plot, ax=ax[0][1], orientation='horizontal')
    dist_cbar.ax.tick_params(labelsize='xx-small')

    # density
    densities = self.metrics.get("density")
    density_plot = ax[0][2].imshow(densities, cmap='binary', interpolation='nearest')
    density_plot.axes.get_xaxis().set_visible(False)
    density_plot.axes.get_yaxis().set_visible(False)
    ax[0][2].set_title("%d-square radius density" % self.density_radius)
    dens_cbar = fig.colorbar(density_plot, ax=ax[0][2], orientation='horizontal')
    dens_cbar.ax.tick_params(labelsize='xx-small')

    # average visibility
    avgVis = self.metrics.get("avgVis")
    avgVis_plot = ax[1][0].imshow(avgVis, cmap='RdYlGn', interpolation='nearest')
    avgVis_plot.axes.get_xaxis().set_visible(False)
    avgVis_plot.axes.get_yaxis().set_visible(False)
    ax[1][0].set_title("Average visibility")
    avgVis_cbar = fig.colorbar(avgVis_plot, ax=ax[1][0], orientation='horizontal')
    avgVis_cbar.ax.tick_params(labelsize='xx-small')
    
    # dispersion
    dispersion = self.metrics.get("dispersion")
    disp_plot = ax[1][1].imshow(dispersion, cmap='RdYlGn', interpolation='nearest')
    disp_plot.axes.get_xaxis().set_visible(False)
    disp_plot.axes.get_yaxis().set_visible(False)
    ax[1][1].set_title("%d-square radius dispersion" % self.dispersion_radius)
    disp_cbar = fig.colorbar(disp_plot, ax=ax[1][1], orientation='horizontal')
    disp_cbar.ax.tick_params(labelsize='xx-small')

    # left-right width
    leftright_width = self.metrics.get("leftright_width")
    lr_plot = ax[1][2].imshow(leftright_width, cmap='RdYlGn', interpolation='nearest')
    lr_plot.axes.get_xaxis().set_visible(False)
    lr_plot.axes.get_yaxis().set_visible(False)
    ax[1][2].set_title("Left-right width")
    lr_cbar = fig.colorbar(lr_plot, ax=ax[1][2], orientation='horizontal')
    lr_cbar.ax.tick_params(labelsize='xx-small')

    # up-down width
    updown_width = self.metrics.get("updown_width")
    ud_plot = ax[2][0].imshow(updown_width, cmap='RdYlGn', interpolation='nearest')
    ud_plot.axes.get_xaxis().set_visible(False)
    ud_plot.axes.get_yaxis().set_visible(False)
    ax[2][0].set_title("Up-down width")
    ud_cbar = fig.colorbar(ud_plot, ax=ax[2][0], orientation='horizontal')
    ud_cbar.ax.tick_params(labelsize='xx-small')

    # positive diagonal width
    posd_width = self.metrics.get("pos_diag_width")
    posd_plot = ax[2][1].imshow(posd_width, cmap='RdYlGn', interpolation='nearest')
    posd_plot.axes.get_xaxis().set_visible(False)
    posd_plot.axes.get_yaxis().set_visible(False)
    ax[2][1].set_title("+ slope diagonal width")
    pd_cbar = fig.colorbar(posd_plot, ax=ax[2][1], orientation='horizontal')
    pd_cbar.ax.tick_params(labelsize='xx-small')

    # negative diagonal width
    negd_width = self.metrics.get("neg_diag_width")
    negd_plot = ax[2][2].imshow(negd_width, cmap='RdYlGn', interpolation='nearest')
    negd_plot.axes.get_xaxis().set_visible(False)
    negd_plot.axes.get_yaxis().set_visible(False)
    ax[2][2].set_title("- slope diagonal width")
    nd_cbar = fig.colorbar(negd_plot, ax=ax[2][2], orientation='horizontal')
    nd_cbar.ax.tick_params(labelsize='xx-small')
    
    plt.axis('off')
    plt.show()


class Input:
  def __init__(self):
    self.root = tk.Tk()
    tk.Label(self.root, text="Seed").grid(row=0)
    tk.Label(self.root, text="Smoothing iterations").grid(row=1)
    tk.Label(self.root, text="Fill percentage (0 to 1)").grid(row=2)

    self.seed = tk.Entry(self.root)
    self.seed.grid(row=0, column=1)

    self.smoothIter = tk.Entry(self.root)
    self.smoothIter.insert(0, "4")
    self.smoothIter.grid(row=1, column=1)

    self.fillPct = tk.Entry(self.root)
    self.fillPct.insert(0, "0.35")
    self.fillPct.grid(row=2, column=1)

    self.showMetrics = tk.IntVar()
    self.showMetrics.set(True)
    showMetricsBox = tk.Checkbutton(self.root, text="Show metrics", var=self.showMetrics)
    showMetricsBox.grid(row=3, column=1)

    tk.Button(self.root, text='Run', command=self.get_input).grid(row=5, column=1)

    self.root.mainloop()
  
  def get_input(self):
    self.inputs = {}

    # get seed
    if len(self.seed.get()) == 0:
      self.inputs["seed"] = hash(datetime.datetime.now())
    else:
      try:
        self.inputs["seed"] = int(self.seed.get())
      except:
        self.inputs["seed"] = hash(self.seed.get())

    # get number of smoothing iterations
    default_smooth_iter = 4
    try:
      self.inputs["smoothIter"] = int(self.smoothIter.get())
    except:
      self.inputs["smoothIter"] = default_smooth_iter

    # get random fill percentage
    default_fill_pct = 0.35
    try:
      self.inputs["fillPct"] = float(self.fillPct.get())
    except:
      self.inputs["fillPct"] = default_fill_pct

    # get show metrics value
    default_show_metrics = 1
    try:
      self.inputs["showMetrics"] = self.showMetrics.get()
    except:
      self.inputs["showMetrics"] = default_show_metrics
      
    self.root.destroy()

def main():
    writer = WorldWriter("../jackal_ws/src/jackal_simulator/jackal_gazebo"
        + "/worlds/proc_world.world")

    # get user parameters, if provided
    inputWindow = Input()
    inputDict = inputWindow.inputs

    # create 25x25 world generator and run smoothing iterations
    generator = MapGenerator(25, 25, inputDict["fillPct"], inputDict["seed"], inputDict["smoothIter"])
    generator()

    # write obstacles to .world file
    map = generator.getMap()
    for r in range(len(map)):
      for c in range(len(map[0])):
        if map[r][c] == 1:
          writer.createCylinder(r-10, c, 0, 0, 0, 0)

    writer.placeCylinders()
    writer.close()

    """ Generate random points to demonstrate path """
    startRegion = generator.biggestLeftRegion()
    endRegion = generator.biggestRightRegion()

    left_open = []
    mid_open = []
    right_open = []
    for r in range(len(map)):
      if startRegion[r][0] == 1:
        left_open.append(r)
      if endRegion[r][24] == 1:
        right_open.append(r)
      if map[r][12] == 0:
        mid_open.append(r)
    left_coord = left_open[random.randint(0, len(left_open)-1)]
    mid_coord = mid_open[random.randint(0, len(mid_open)-1)]
    right_coord = right_open[random.randint(0, len(right_open)-1)]
    """ End random point selection """

    generator.connectRegions(startRegion, endRegion)
    
    # generate path, if possible
    path = []
    print("Points: (%d, 0), (%d, 12), (%d, 24)" % (left_coord, mid_coord, right_coord))
    path = generator.getPath([(left_coord, 0), (mid_coord, 12), (right_coord, 24)])
    print("Found path!")

    # convert path list to matrix
    map_with_path = [[map[j][i] for i in range(len(map[0]))] for j in range(len(map))]
    for r, c in path:
      map_with_path[r][c] = 0.35
    map_with_path[left_coord][0] = 0.65
    map_with_path[mid_coord][12] = 0.65
    map_with_path[right_coord][24] = 0.65

    # display world and heatmap of distances
    if inputDict["showMetrics"]:
      display = Display(map, map_with_path, density_radius=3, dispersion_radius=3)
      display()

    # only show the map itself
    else:
      plt.imshow(map, cmap='Greys', interpolation='nearest')
      plt.show()

if __name__ == "__main__":
    main()
