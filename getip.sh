#!/bin/bash

ifconfig  | grep broadcast | grep "inet " | grep -v 169.254 | sed -e 's/^\t//g' | cut -d ' ' -f 2
