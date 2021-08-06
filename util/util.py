import collections
import json
from functools import cmp_to_key

def gen_session_header(session_token: str):
  return {
    "Authorization": "Bearer %s" % session_token
  }

def floatcompare(item1 = 0, item2 = 0):
  return float(item1[0]) - float(item2[0])

def sort_dict(dict):
  return collections.OrderedDict(sorted(dict.items(), key=cmp_to_key(floatcompare)))


def write_json_to_file(path: str, data: dict):
  with open(path, "w") as out:
    out.write(json.dumps(data, indent=2))

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "                                                          \r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()