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


class WorldWriter():

  def __init__(self, filename, map, cyl_radius):
    self.file = open(filename, "w")
    self.map = map
    self.numCylinders = 0
    self.cylinderList = []
    self.cyl_radius = cyl_radius
    self.r_shift = -len(self.map) * self.cyl_radius
    self.c_shift = 2

  def __call__(self):
    # write .world boilerplate at start
    self._writeStarterBoiler()

    # define all the cylinders we're using in .world
    radius_ratio = self.cyl_radius / 0.5
    self.r_shift = -len(self.map) * self.cyl_radius
    self.c_shift = 2
    for r in range(len(self.map)):
      for c in range(len(self.map[0])):
        if self.map[r][c] == 1 and not self._allNeighborsFilled(r, c):
          self._createCylinder((r*radius_ratio)+self.r_shift, (c*radius_ratio)+self.c_shift, 0, 0, 0, 0, radius=self.cyl_radius)

    # add a wall around the robot to force it to actually go through the obstacles
    contain_wall_length = 5
    c_coord = self.c_shift - contain_wall_length
    while c_coord + self.cyl_radius < self.c_shift:
      self._createCylinder(self.r_shift, c_coord, 0, 0, 0, 0, radius=self.cyl_radius)
      self._createCylinder(self.r_shift + (len(self.map) - 1) * radius_ratio, c_coord, 0, 0, 0, 0, radius=self.cyl_radius)
      c_coord += self.cyl_radius * 2

    r_coord = self.r_shift + self.cyl_radius * 2
    while r_coord < (len(self.map) - 2) * radius_ratio + self.r_shift:
      self._createCylinder(r_coord, self.c_shift - contain_wall_length, 0, 0, 0, 0, radius=self.cyl_radius)
      r_coord += self.cyl_radius * 2


    # write .world middle boilerplate
    self._writeMidBoiler()

    # place cylinders
    self._placeCylinders()

    # write .world end boilerplate
    self._writeEndBoiler()

    # close file
    self._close()

  # returns true if all 8 spaces around (r, c) are filled, false otherwise
  def _allNeighborsFilled(self, r, c):
    for r_neigh in range(r-1, r+2):
      for c_neigh in range(c-1, c+2):
        if r_neigh < 0 or r_neigh >= len(self.map) or c_neigh < 0 or c_neigh >= len(self.map[0]):
          return False

        if self.map[r_neigh][c_neigh] == 0:
          return False

    return True

  def _writeStarterBoiler(self):
    self.file.write(world_boiler_start)

  def _createCylinder(self, pos_x, pos_y, pos_z, rot_a, rot_b, rot_c, radius):
    self.file.write(cylinder_define % (
        self.numCylinders, pos_x, pos_y, pos_z, rot_a, rot_b, rot_c, radius, radius
    ))
    
    self.cylinderList.append([pos_x, pos_y, pos_z, rot_a, rot_b, rot_c])
    self.numCylinders += 1

  def _writeMidBoiler(self):
      self.file.write(world_boiler_mid)

  def _placeCylinders(self):
    for i in range(self.numCylinders):
      self.file.write(cylinder_place % (
          i, self.cylinderList[i][0], self.cylinderList[i][1], self.cylinderList[i][2], 
          self.cylinderList[i][3], self.cylinderList[i][4], self.cylinderList[i][5], 
          self.cylinderList[i][0], self.cylinderList[i][1], self.cylinderList[i][2], 
          self.cylinderList[i][3], self.cylinderList[i][4], self.cylinderList[i][5], 
      ))

  def _writeEndBoiler(self):
    self.file.write(world_boiler_end)

  def _close(self):
    self.file.close()

  def getShifts(self):
    return self.r_shift, self.c_shift
   