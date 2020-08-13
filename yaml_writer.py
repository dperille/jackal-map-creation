class YamlWriter():
  
  def __init__(self, filename, image_file):
    self.file = open(filename, "w")
    self.image_file = image_file
    self.arguments = (image_file, 0.1, 0.0, 0.0, 0.0)
    with open("yaml_template.txt") as f:
      self.yaml_temp = f.read()

  def write(self):
    self.file.write(self.yaml_temp % self.arguments)
    print(self.yaml_temp % self.arguments)
  

