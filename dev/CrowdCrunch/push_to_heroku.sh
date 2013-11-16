#!/bin/bash

# assume that you are in the app directory
cd ../../

# push the subtree to herkou
git subtree push --prefix dev/CrowdCrunch heroku master