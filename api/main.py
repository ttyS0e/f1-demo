import sys
from stats import stats

def main():
  this_stats = stats()
  print(this_stats.get_driver_fastest_times((len(sys.argv) > 1 and sys.argv[1]) or None))

  if len(sys.argv) > 2:
    this_stats.apply_performance_upgrade(driver=sys.argv[1], percent=int(sys.argv[2]))
    print(this_stats.get_driver_fastest_times())

if __name__ == "__main__":
  main()
