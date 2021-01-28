#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
wget --directory-prefix=$DIR http://cs231n.stanford.edu/tiny-imagenet-200.zip
unzip $DIR/tiny-imagenet-200.zip -d $DIR
rm $DIR/tiny-imagenet-200.zip