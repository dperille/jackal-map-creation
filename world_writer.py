import numpy as np
# define boilerplate code needed to write to .world file
with open('./world-boilerplate/world_boiler_start.txt') as f:
      world_boiler_start = f.read()
with open('./world-boilerplate/world_boiler_mid.txt') as f:
      world_boiler_mid = f.read()
with open('./world-boilerplate/world_boiler_end.txt') as f:
      world_boiler_end = f.read()
with open('./world-boilerplate/cylinder_define.txt') as f:
      cylinder_define = f.read()
with open('./world-boilerplate/cylinder_place.txt') as f:
      cylinder_place = f.read()

wall_rgb = [0.152, 0.379, 0.720]
obs_rgb = [0.648, 0.192, 0.192]

class WorldWriter():

  def __init__(self, filename, map, cyl_radius, contain_wall_length):
    self.file = open(filename, "w")
    self.map = map
    self.num_cylinders = 0
    self.cylinder_list = []
    self.cyl_radius = cyl_radius
    self.r_shift = -(len(self.map) - 1) * self.cyl_radius * 2
    self.c_shift = 1.95
    self.contain_wall_length = contain_wall_length

  def __call__(self):
    # write .world boilerplate at start
    self._write_starter_boiler()

    c_lower = self.cyl_radius
    c_upper = self.cyl_radius + self.contain_wall_length
    r_lower = -self.cyl_radius
    r_upper = self.r_shift - self.cyl_radius

    # create the back containment wall
    r_coord = r_lower
    while r_coord >= r_upper:
      self._create_cyl(r_coord, c_lower, 0, 0, 0, 0, radius=self.cyl_radius, rgb=wall_rgb)
      r_coord -= self.cyl_radius * 2

    # create the upper and lower containment walls
    c_coord = c_lower + self.cyl_radius * 2
    while c_coord <= c_upper:
      self._create_cyl(r_lower, c_coord, 0, 0, 0, 0, radius=self.cyl_radius, rgb=wall_rgb)
      self._create_cyl(r_upper, c_coord, 0, 0, 0, 0, radius=self.cyl_radius, rgb=wall_rgb)
      c_coord += self.cyl_radius * 2


    # define all cylinders in the actual obstacle field
    c_lower = c_coord
    for r in range(len(self.map)):
      for c in range(len(self.map[0])):
        if self.map[r][c] == 1 and not self._neighbors_filled(r, c):
          if r == 0 or r == len(self.map) - 1:
            self._create_cyl(r_upper + r * self.cyl_radius * 2, c_lower + c * self.cyl_radius * 2, 0, 0, 0, 0, radius=self.cyl_radius, rgb=wall_rgb)
          else:
            self._create_cyl(r_upper + r * self.cyl_radius * 2, c_lower + c * self.cyl_radius * 2, 0, 0, 0, 0, radius=self.cyl_radius, rgb=obs_rgb)


    # write .world middle boilerplate
    self._write_mid_boiler()

    # place cylinders
    self._place_cylinders()

    # write .world end boilerplate
    self._write_end_boiler()

    # close file
    self._close()

    contain_wall_cylinders = self.contain_wall_length / (self.cyl_radius * 2)
    return int(contain_wall_cylinders)

  # returns true if all 8 spaces around (r, c) are filled, false otherwise
  def _neighbors_filled(self, r, c):
    for r_neigh in range(r-1, r+2):
      for c_neigh in range(c-1, c+2):
        if r_neigh < 0 or r_neigh >= len(self.map) or c_neigh < 0 or c_neigh >= len(self.map[0]):
          return False

        if self.map[r_neigh][c_neigh] == 0:
          return False

    return True

  def _write_starter_boiler(self):
    self.file.write(world_boiler_start)

  def _create_cyl(self, pos_x, pos_y, pos_z, rot_a, rot_b, rot_c, radius, rgb):
    self.file.write(cylinder_define % (
        self.num_cylinders, pos_x, pos_y, pos_z, rot_a, rot_b, rot_c, radius, radius, rgb[0], rgb[1], rgb[2], rgb[0], rgb[1], rgb[2]
    ))
    self.file.write('\n')
    
    self.cylinder_list.append([pos_x, pos_y, pos_z, rot_a, rot_b, rot_c])
    self.num_cylinders += 1

  def _write_mid_boiler(self):
      self.file.write(world_boiler_mid)

  def _place_cylinders(self):
    for i in range(self.num_cylinders):
      self.file.write(cylinder_place % (
          i, self.cylinder_list[i][0], self.cylinder_list[i][1], self.cylinder_list[i][2], 
          self.cylinder_list[i][3], self.cylinder_list[i][4], self.cylinder_list[i][5], 
          self.cylinder_list[i][0], self.cylinder_list[i][1], self.cylinder_list[i][2], 
          self.cylinder_list[i][3], self.cylinder_list[i][4], self.cylinder_list[i][5], 
      ))
      self.file.write('\n')

  def _write_end_boiler(self):
    self.file.write(world_boiler_end)

  def _close(self):
    self.file.close()

  def get_shifts(self):
    return self.r_shift, self.c_shift