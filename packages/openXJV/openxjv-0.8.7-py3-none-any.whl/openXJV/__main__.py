#!/usr/bin/python3
# coding: utf-8
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))


if __name__ == "__main__":
    from .bin.openXJV import *
    launchApp()