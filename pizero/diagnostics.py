from datetime import datetime

buffer = []

def log(*args):
  
  msg = "".join([str(a) + " " for a in args])
  buffer.append(msg)
  while len(buffer) > 6:
    buffer.pop(0)
  print(datetime.now(), *args)

if __name__ == "__main__":
  log("Testing", 1, 2, "three")