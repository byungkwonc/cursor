#!/bin/bash

pip install -r requirements.txt

python /Users/byungkwonc/github/cursor/aws-blog-crawler/scripts/aws-crawler-ko.py --archive

gzip -f blog-articles-ko.txt