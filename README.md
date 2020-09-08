# jackal-map-creation

To use this repository:
You will need to have Python2 installed on your computer. After cloning this repository onto your computer, create a folder called "test_data" in the same directory. Inside the test_data folder, create folders called cspace_files, grid_files, map_files, world_files, metrics_files, norm_metrics_files, and path_files.

To generate a sample world:
Run gen_world_ca.py in Python 2. This will generate a 30x30 world by cellular automaton, using an initial fill percent of 0.2 and 4 smoothing iterations.
The script will generate a path through this world and calculate difficulty metrics along this path. After this, it will save the metrics and representations of the world and path into the test_data folder. The sample world file names will be suffixed with "-1". This script will also display the world, C-space, path, and the calculated metrics. To try out different generation parameters (rows, columns, fill percent, iterations), comment out lines 618-623 and uncomment lines 615-616.

To generate a new dataset:
Run generator.py in Python 2. This will generate 300 worlds with dimensions 30x30 using 12 different sets of cellular automaton parameters. These parameters can be changed within the generator.py script.

These scripts were written to generate worlds for a Jackal robot, and the generated pgm, yaml, and world files reflect this. To generate a dataset for a different sized robot or at a different resolution, change the default cylinder size, robot radius, inflation radius, and pgm resolution in gen_world_ca.py.


Dataset structure:
The dataset files will be saved in the test_data folder. The folder called cspace_files contains .npy files with a 30x30 occupancy grid of the C-space. The grid_files folder will contain the occupancy grid of the world in .npy format. The map_files folder contains pgm and yaml files for use with the ROS map_server. The
world_files folder contains .world files for use in Gazebo simulations. The metrics_files folder contains the 5 difficulty metrics calculated on the path in this order: distance to closest obstacle, average visibility, dispersion, characteristic dimension, and tortuosity.
The path_files folder contains the path through the world, in .npy format. The path is represented by an nx2 array, where n is the number of points in the path. Points are represented by their row and column, in that order.
