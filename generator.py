import gen_world_ca
import datetime


# generates dataset of 300 worlds
# 12 sets of parameters, 25 each set
def main():
  set_size = 25
  total_counter = 0

  # fill percent from 0.15 to 0.30, interval 0.05 (4 levels)
  for i in range(4):
    fill_pct = (i * 0.05) + 0.15
    # smooth iterations from 2 to 4 (3 levels)
    for smooths in range(2, 5):
      param_counter = 0
      while param_counter < set_size:
	print('_________________________________________________________')
	print('world', total_counter, 'fill_pct', fill_pct, 'smooths', smooths)
        result = gen_world_ca.main(total_counter, hash(datetime.datetime.now()), smooths, fill_pct, show_metrics=0)
        if result: # worlds with no path are not counted or used
          param_counter += 1
          total_counter += 1


if __name__ == "__main__":
  main()

