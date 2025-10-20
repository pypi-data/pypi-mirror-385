#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) EDF 2025

@authors: Elias Fekhari, Joseph Muré
"""
import os
import othpc
import openturns as ot
from othpc.example import CantileverBeam

my_results_directory = "my_results"
evals_per_job = 2
cb = CantileverBeam(my_results_directory, n_cpus=1, fake_load_time=1)
sf = othpc.SubmitFunction(
    cb, ntasks_per_node=evals_per_job, cpus_per_task=1, timeout_per_job=5
)
f = ot.Function(sf)
memoize_func = othpc.load_cache(
    f, os.path.join(my_results_directory, "summary_table.csv")
)
X = ot.Sample.ImportFromCSVFile("input_doe/doe.csv", ",")
Y = memoize_func(X)
print(Y)
