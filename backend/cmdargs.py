import argparse
import os

parser = argparse.ArgumentParser()

parser.add_argument('--blur', action="store_true", default=False, help='Blur all images')
parser.add_argument("--reindex", action="store_true", default=False, help='Reindex all db')
parser.add_argument("--rewrite_v_info", action="store_true", default=False, help='Rewrite v_info file')

args = parser.parse_args()
