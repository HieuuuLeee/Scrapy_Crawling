#!/bin/bash

date >> ~/Virtualenvs/demo/testcron
cd /home/tn/Virtualenvs/demo
PATH=$PATH:/usr/local/bin
export PATH
scrapy crawl BDS
