from datetime import datetime
def log(*args):
  print(datetime.now(), *args)

if __name__ == "__main__":
  log("Testing")