import time
import random
from pynput.keyboard import Controller, Key
import argparse

def get_random_val_0_20(args):
    if args.random > 9:
        addition = 9
    else:
        addition = args.random
    
    return random.randint(10-addition, 10+addition)/10

def write_from_file(args):
  """
  Reads the content of a text file and simulates keystrokes to write it.

  Args:
      file_path (str): Path to the text file to be read.
  """
  with open(args.file_path, 'r') as file:
    content = file.read()

  keyboard = Controller()

  # Simulate keystrokes for the content
  for char in content:
    # Handle new line characters
    if char == '\n':
      keyboard.press(Key.enter)
      keyboard.release(Key.enter)
      time.sleep(args.delay_line*get_random_val_0_20(args))
    else:
      keyboard.type(char)
    time.sleep(args.delay_char*get_random_val_0_20(args))  # Adjust delay between keystrokes if needed

def get_argument():
  parser = argparse.ArgumentParser(description="Write content from a file using simulated keystrokes.")
  parser.add_argument("file_path", type=str, help="Path to the text file to be read.")
  parser.add_argument("-d", "--delay-start", type=float, default=6, help="Delay at start (default: 6).")
  parser.add_argument("-d_char", "--delay-char", type=float, default=0.01, help="Delay between char keystrokes in seconds (default: 0.01).")
  parser.add_argument("-d_line", "--delay-line", type=float, default=0.5, help="Delay between line keystrokes in seconds (default: 0.5).")
  parser.add_argument("-r", "--random", type=float, default=3, help="Random interval (default: 3) number between 0 - 9.")
  args = parser.parse_args()
  
  return args

  



if __name__ == "__main__":
    args = get_argument()
    time.sleep(args.delay_start)
    
    write_from_file(args)
    print(f"Content of '{args.file_path}' written using simulated keystrokes.")
