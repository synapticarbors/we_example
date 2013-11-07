#!/bin/bash

echo west_pythonpath: $WEST_PYTHONPATH
echo west_sim_root: $WEST_SIM_ROOT
echo west_root: $WEST_ROOT

BSTATE_ARGS_0="--bstate initA,1"

if [ ! -f west.h5 ];
then
    $WEST_ROOT/bin/w_init -r west.cfg $BSTATE_ARGS_0 > sim_init.log &
    wait
fi

$WEST_ROOT/bin/w_run --work-manager serial -r west.cfg --verbose > sim.log &
wait

