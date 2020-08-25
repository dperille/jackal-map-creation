import numpy as np
from gen_world_ca import JackalMap

def create_cspace_files(obs_map_dir, num_files, cspace_dir, radius):
    for i in range(num_files):
        output_file = cspace_dir + "cspace_" + str(i) + ".npy"
        input_file = obs_map_dir + "grid_" + str(i) + ".npy"

        obs_map = np.load(input_file)
        jm = JackalMap(obs_map, radius)
        cspace_grid = jm.getMap()

        # save c-space
        cspace_grid = np.asarray(cspace_grid)
        np.save(output_file, cspace_grid)

if __name__ == "__main__":
    create_cspace_files("dataset/grid_files/", 300, "dataset/cspace_files/", 2)
