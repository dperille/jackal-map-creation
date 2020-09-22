import numpy as np
from gen_world_ca import JackalMap


jackal_radius = 2 # Jackal takes up 2 cells in each direction in addition to center (5x5)
num_files = 300

# creates C-space files from given occupancy grids and robot radius
def create_cspace_files(obs_map_dir, num_files, cspace_dir, robot_radius):
    for i in range(num_files):
        output_file = cspace_dir + 'cspace_%d.npy' % i
        input_file = obs_map_dir + 'grid_%d.npy' % i

        obs_map = np.load(input_file)
        jm = JackalMap(obs_map, robot_radius)
        cspace_grid = jm.get_map()

        # save c-space
        cspace_grid = np.asarray(cspace_grid)
        np.save(output_file, cspace_grid)

if __name__ == "__main__":
    create_cspace_files('test_data/grid_files/', num_files, 'test_data/cspace_files/', jackal_radius)
