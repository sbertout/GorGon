#!/usr/bin/env bash

rm -rvf presets/Concord/*
kl2dfg -inheritance Concord.fpm.json presets/Concord
