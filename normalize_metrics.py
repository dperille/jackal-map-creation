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
# all_means: (1x5) NumPy array with means for each metric
# all_stds: (1x5) NumPy array with standard deviations for each metric
def calc_stats(all_metrics):
  all_means = np.mean(all_metrics, axis=0)
  all_stds = np.std(all_metrics, axis=0)
  return all_means, all_stds

# metrics_arr is the array with all metrics (nx5)
# means is the array with means for each metric (1x5)
# stds is the array with standard deviationss for each metric (1x5)
# all metrics are modified in place
def normalize_all(metrics_arr, means, stds):
  for datapt in range(len(metrics_arr)):
    for metric in range(5):
      # normalized metric = (val - mean) / std
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
  num_files = 300
  metrics_dir = 'test_data/metrics_files/'
  norm_metrics_dir = 'test_data/norm_metrics_files/'
  
  # load files
  dataset_arr = load_metrics(metrics_dir, num_files)

  # print min/max
  print('MINIMUMS')
  print(np.amin(dataset_arr, axis=0))
  print('MAXIMUMS')
  print(np.amax(dataset_arr, axis=0))

  # get the means and standard devs
  means, stds = calc_stats(dataset_arr)

  # normalize metrics
  dataset_arr = normalize_all(dataset_arr, means, stds)

  # save to files
  save_norm_metrics(norm_metrics_dir, dataset_arr)

if __name__ == "__main__":
  main()