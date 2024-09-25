#!/bin/bash
sleap-track /home/roblab20/dev/sleap_bat_tracking/dataset/labels.v001.slp --only-labeled-frames -m models/v1240924_184631.centroid -m models/v1240924_184631.centered_instance --max_instances 1 -o labels.v001.slp.predictions.slp --verbosity json --no-empty-frames
