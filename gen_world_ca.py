import random
import sys
import matplotlib.pyplot as plt

world_boiler_start = """<sdf version='1.6'>
  <world name='default'>
    <light name='sun' type='directional'>
      <cast_shadows>1</cast_shadows>
      <pose frame=''>0 0 10 0 -0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.1 0.1 0.1 1</specular>
      <attenuation>
        <range>1000</range>
        <constant>0.9</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
      <direction>-0.5 0.5 -1</direction>
    </light>
    <model name='ground_plane'>
      <static>1</static>
      <link name='link'>
        <collision name='collision'>
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <surface>
            <friction>
              <ode>
                <mu>100</mu>
                <mu2>50</mu2>
              </ode>
              <torsional>
                <ode/>
              </torsional>
            </friction>
            <contact>
              <ode/>
            </contact>
            <bounce/>
          </surface>
          <max_contacts>10</max_contacts>
        </collision>
        <visual name='visual'>
          <cast_shadows>0</cast_shadows>
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <material>
            <script>
              <uri>file://media/materials/scripts/gazebo.material</uri>
              <name>Gazebo/Grey</name>
            </script>
          </material>
        </visual>
        <self_collide>0</self_collide>
        <kinematic>0</kinematic>
        <gravity>1</gravity>
      </link>
    </model>
    <gravity>0 0 -9.8</gravity>
    <magnetic_field>6e-06 2.3e-05 -4.2e-05</magnetic_field>
    <atmosphere type='adiabatic'/>
    <physics name='default_physics' default='0' type='ode'>
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
    </physics>
    <scene>
      <ambient>0.4 0.4 0.4 1</ambient>
      <background>0.7 0.7 0.7 1</background>
      <shadows>1</shadows>
    </scene>
    <spherical_coordinates>
      <surface_model>EARTH_WGS84</surface_model>
      <latitude_deg>0</latitude_deg>
      <longitude_deg>0</longitude_deg>
      <elevation>0</elevation>
      <heading_deg>0</heading_deg>
    </spherical_coordinates>"""
world_boiler_mid = """<state world_name='default'>
      <sim_time>46 817000000</sim_time>
      <real_time>50 373153562</real_time>
      <wall_time>1591479841 622585835</wall_time>
      <iterations>46817</iterations>
      <model name='ground_plane'>
        <pose frame=''>0 0 0 0 -0 0</pose>
        <scale>1 1 1</scale>
        <link name='link'>
          <pose frame=''>0 0 0 0 -0 0</pose>
          <velocity>0 0 0 0 -0 0</velocity>
          <acceleration>0 0 0 0 -0 0</acceleration>
          <wrench>0 0 0 0 -0 0</wrench>
        </link>
      </model>"""
world_boiler_end = """<light name='sun'>
        <pose frame=''>0 0 10 0 -0 0</pose>
      </light>
    </state>
    <gui fullscreen='0'>
      <camera name='user_camera'>
        <pose frame=''>5 -5 2 0 0.275643 2.35619</pose>
        <view_controller>orbit</view_controller>
        <projection_type>perspective</projection_type>
      </camera>
    </gui>
  </world>
</sdf>"""
cylinder_define = """<model name='unit_cylinder_%d'>
      <pose frame=''>%f %f %f %f %f %f</pose>
      <link name='link'>
        <inertial>
          <mass>1</mass>
          <inertia>
            <ixx>0.145833</ixx>
            <ixy>0</ixy>
            <ixz>0</ixz>
            <iyy>0.145833</iyy>
            <iyz>0</iyz>
            <izz>0.125</izz>
          </inertia>
        </inertial>
        <collision name='collision'>
          <geometry>
            <cylinder>
              <radius>0.5</radius>
              <length>1</length>
            </cylinder>
          </geometry>
          <max_contacts>10</max_contacts>
          <surface>
            <contact>
              <ode/>
            </contact>
            <bounce/>
            <friction>
              <torsional>
                <ode/>
              </torsional>
              <ode/>
            </friction>
          </surface>
        </collision>
        <visual name='visual'>
          <geometry>
            <cylinder>
              <radius>0.5</radius>
              <length>1</length>
            </cylinder>
          </geometry>
          <material>
            <script>
              <name>Gazebo/Grey</name>
              <uri>file://media/materials/scripts/gazebo.material</uri>
            </script>
          </material>
        </visual>
        <self_collide>0</self_collide>
        <kinematic>0</kinematic>
        <gravity>1</gravity>
      </link>
    </model>"""
cylinder_place = """<model name='unit_cylinder_%d'>
        <pose frame=''>%f %f %f %f %f %f</pose>
        <scale>1 1 1</scale>
        <link name='link'>
          <pose frame=''>%f %f %f %f %f %f</pose>
          <velocity>0 0 0 0 -0 0</velocity>
          <acceleration>0 0 -9.8 0 -0 0</acceleration>
          <wrench>0 0 -9.8 0 -0 0</wrench>
        </link>
      </model>"""

class MapGenerator():
  def __init__(self, rows, cols, randFillPct, seed=None):
    self.map = [[0 for i in range(cols)] for j in range(rows)]
    self.rows = rows
    self.cols = cols
    self.randFillPct = randFillPct
    self.seed = hash(seed)

  def randomFill(self):
    if self.seed:
      random.seed(self.seed)

    for r in range(self.rows):
      for c in range(self.cols):
        if r == 0 or r == self.rows - 1:
          self.map[r][c] = 1
        else:
          self.map[r][c] = 1 if random.random() < self.randFillPct else 0

  def smooth(self):
    newmap = [[self.map[r][c] for c in range(self.cols)] for r in range(self.rows)]
    for r in range(self.rows):
      for c in range(self.cols):
        # if more than 4 filled neighbors, fill this tile
        if self.tileNeighbors(r, c) > 4:
          newmap[r][c] = 1

        # if less than 2 filled neighbors, empty this one
        elif self.tileNeighbors(r, c) < 2:
          newmap[r][c] = 0

    self.map = newmap

  def tileNeighbors(self, r, c):
    count = 0
    for i in range(r - 1, r + 2):
      for j in range(c - 1, c + 2):
        if i >= 0 and i < self.rows and j >= 0 and j < self.cols:
          if i != r or j != c:
            count += self.map[i][j]

        # if on the top or bottom, add to wall neighbors
        elif i < 0 or i >= self.rows:
          count += 1
    
    return count

  def getMap(self):
    return self.map

  # determines how far a given cell is from a wall (non-diagonal)
  def distToClosestWall(self, r, c, currCount, currBest):
    if r < 0 or r >= self.rows - 1 or c < 0 or c >= self.cols - 1:
      return 0

    if self.map[r][c] == 1:
      return 0

    if currCount >= currBest:
      return sys.maxint

    bestUp = 1 + self.distToClosestWall(r-1, c, currCount+1, currBest)
    if bestUp < currBest:
      currBest = bestUp
    
    bestDown = 1 + self.distToClosestWall(r+1, c, currCount+1, currBest)
    if bestDown < currBest:
      currBest = bestDown
    
    bestLeft = 1 + self.distToClosestWall(r, c-1, currCount+1, currBest)
    if bestLeft < currBest:
      currBest = bestLeft

    bestRight = 1 + self.distToClosestWall(r, c+1, currCount+1, currBest)

    return min(bestUp, bestDown, bestLeft, bestRight)

  def distsToWall(self):
    dists = [[0 for i in range(self.cols)] for j in range(self.rows)]
    for r in range(self.rows):
      for c in range(self.cols):
        dists[r][c] = self.distToClosestWall(r, c, 0, sys.maxint)

    return dists

class WorldWriter():
  def __init__(self, filename):
    self.file = open(filename, "w")
    self.numCylinders = 0
    self.cylinderList = []
    self.writeStarterBoiler()

  def writeStarterBoiler(self):
    self.file.write(world_boiler_start)

  def createCylinder(self, x, y, z, a, b, c):
    self.file.write(cylinder_define % (
        self.numCylinders, x, y, z, a, b, c
    ))
    
    self.cylinderList.append([x, y, z, a, b, c])
    self.numCylinders += 1

  def writeMidBoiler(self):
      self.file.write(world_boiler_mid)

  def placeCylinders(self):
    self.writeMidBoiler()

    for i in range(self.numCylinders):
      self.file.write(cylinder_place % (
          i, self.cylinderList[i][0], self.cylinderList[i][1], self.cylinderList[i][2], 
          self.cylinderList[i][3], self.cylinderList[i][4], self.cylinderList[i][5], 
          self.cylinderList[i][0], self.cylinderList[i][1], self.cylinderList[i][2], 
          self.cylinderList[i][3], self.cylinderList[i][4], self.cylinderList[i][5], 
      ))

    self.writeEndBoiler()

  def writeEndBoiler(self):
    self.file.write(world_boiler_end)

  def close(self):
    self.file.close()
   

def main():
    writer = WorldWriter("../jackal_ws/src/jackal_simulator/jackal_gazebo"
        + "/worlds/proc_world.world")

    # get user parameters, if provided
    # usage: gen_world_ca.py <seed> <smoothing_iterations> <initial_fill_pct> <show_heatmap>
    seed = None
    smooths = 5
    fillPct = 0.35
    showHeatMap = 1
    if len(sys.argv) >= 2:
      seed = sys.argv[1]
    if len(sys.argv) >= 3:
      smooths = int(sys.argv[2])
    if len(sys.argv) >= 4:
      fillPct = float(sys.argv[3])
    if len(sys.argv) >= 5:
      showHeatMap = int(sys.argv[4])

    # create 25x25 world generator and run smoothing iterations
    generator = MapGenerator(25, 25, fillPct, seed)
    generator.randomFill()
    for n in range(smooths):
      generator.smooth()

    # write obstacles to .world file
    map = generator.getMap()
    for r in range(len(map)):
      for c in range(len(map[0])):
        if map[r][c] == 1:
          writer.createCylinder(r-10, c, 0, 0, 0, 0)

    writer.placeCylinders()
    writer.close()

    # display world and heatmap of distances
    if showHeatMap:
      dists = generator.distsToWall()
      f, ax = plt.subplots(1, 2)
      ax[0].imshow(map, cmap='Greys', interpolation='nearest')
      ax[1].imshow(dists, cmap='RdYlGn', interpolation='nearest')
      plt.show()

    else:
      plt.imshow(map, cmap='Greys', interpolation='nearest')
      plt.show()

if __name__ == "__main__":
    main()
