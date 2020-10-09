#!/bin/bash
export WKDIR="$NDMBASE/$NDMPATH"
mkdir -p $WKDIR && cd $WKDIR || exit 1
(
export
ndm info
# my job
sleep 1
) |& tee $WKDIR/ndm.log
