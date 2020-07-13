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

  def __call__(self):
    # write .world boilerplate at start
    self._writeStarterBoiler()

    # define all the cylinders we're using in .world
    radius_ratio = self.cyl_radius / 0.5
    r_shift = -len(self.map) * self.cyl_radius
    c_shift = 2
    for r in range(len(self.map)):
      for c in range(len(self.map[0])):
        if self.map[r][c] == 1:
          self._createCylinder((r*radius_ratio)+r_shift, (c*radius_ratio)+c_shift, 0, 0, 0, 0, radius=self.cyl_radius)

    # write .world middle boilerplate
    self._writeMidBoiler()

    # place cylinders
    self._placeCylinders()

    # write .world end boilerplate
    self._writeEndBoiler()

    # close file
    self._close()

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
   