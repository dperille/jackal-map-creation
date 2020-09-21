import numpy as np

# metrics_dir is the directory storing metrics in npy form
# appends all metrics into a 2D NumPy array and returns
def load_metrics(metrics_dir, num_files):
  file_name = 'metrics_%d.npy'
  result = []

  # load all arrays and append to result
  for i in range(num_files):
    result.append(np.load(metrics_dir + file_name % i))
  
  # convert to 2D NumPy array
  result = np.stack(result)

  return result


# all_metrics is a 2D NumPy array made from appending all difficulty metrics arrays
def calc_stats(all_metrics):
  all_means = np.mean(all_metrics, axis=0)
  all_stds = np.std(all_metrics, axis=0)
  return all_means, all_stds

# metrics_arr is the array with all metrics (300x5)
# means is the array with means for each metric (1x5)
# stds is the array with standard devs for each metrics (1x5)
# all metrics are modified in place
def normalize_all(metrics_arr, means, stds):
  for datapt in range(len(metrics_arr)):
    for metric in range(5):
      metrics_arr[datapt][metric] -= means[metric]
      metrics_arr[datapt][metric] /= stds[metric]
  
  return metrics_arr

# save all metrics in metrics_arr to dir_name directory
def save_norm_metrics(dir_name, metrics_arr):
  file_name = 'norm_metrics_%d.npy'

  for i in range(len(metrics_arr)):
    np.save(dir_name + file_name % i, metrics_arr[i])

# loads all metrics files, normalizes metrics, and saves to directory
def main():
  # load files
  phys_arr = load_metrics('phys_data/metrics_files/', 10)
  dataset_arr = load_metrics('dataset/metrics_files/', 300)

  # print min/max
  print('MINIMUMS')
  print(np.amin(phys_arr, axis=0))
  print('MAXIMUMS')
  print(np.amax(phys_arr, axis=0))

  # get the means and standard devs
  means, stds = calc_stats(dataset_arr)

  # normalize metrics
  metrics_arr = normalize_all(phys_arr, means, stds)

  # save to files
  save_norm_metrics('phys_data/norm_metrics_files/', phys_arr)

if __name__ == "__main__":
  main()