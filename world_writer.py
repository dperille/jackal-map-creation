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

  def __init__(self, filename, map):
    self.file = open(filename, "w")
    self.map = map
    self.numCylinders = 0
    self.cylinderList = []

  def __call__(self):
    # write .world boilerplate at start
    self._writeStarterBoiler()

    # define all the cylinders we're using in .world
    for r in range(len(self.map)):
      for c in range(len(self.map[0])):
        if self.map[r][c] == 1:
          self._createCylinder(r-10, c, 0, 0, 0, 0)

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

  def _createCylinder(self, x, y, z, a, b, c):
    self.file.write(cylinder_define % (
        self.numCylinders, x, y, z, a, b, c
    ))
    
    self.cylinderList.append([x, y, z, a, b, c])
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
   