# Forward declaration
# https://ubuntuforums.org/showthread.php?t=505755

class Foo:
 def __init__(self):
  pass
 def bars(self):
  return [Bar(1), Bar(1)]
class Bar:
 def __init__(self, d):
  self.d = d
 def foos(self):
  return [Foo(), Foo()]

foo = Foo()
foo.bars()
print("OK")
