import argparse
import os

parser = argparse.ArgumentParser()

parser.add_argument('--blur', action="store_true", default=False, help='Blur all images')

args = parser.parse_args()

os.environ["SFVH_BLUR"] = str(int(args.blur))
