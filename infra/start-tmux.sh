#!/bin/bash

tmux \
    new-session 'source start-service.sh' \; \
    split-window 'source start-status.sh' \; \
    split-window 'source start-generator.sh' \;


