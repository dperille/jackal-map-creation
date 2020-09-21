class YamlWriter():
  
  def __init__(self, filename, iteration):
    self.file = open(filename, "w")
    self.iteration = iteration
    self.yaml_temp ='image: map_pgm_%d.pgm\nresolution: 0.15\norigin: [-4.5, 0.0, 0]\noccupied_thresh: 0.50\nfree_thresh: 0.50\nnegate: 0'

    

  def write(self):
    self.file.write(self.yaml_temp % self.iteration)
  

