#!/bin/usr/env bash

# ============================================ #
#    RUN: sh copy_data.sh USER_PC  (AFS_PC)    #
# ============================================ #

#Script must be run from main folder or paths will be messed up

if [ -n "$1" ];then
    afs_user=$1

    if [ -n "$2" ];then
        afs_pc=$2
        else
            afs_pc=116
            echo "No afs pcae introduced, taking pcae116 as default"
        fi

    #create data if not present
    if [ ! -d "../data" ]; then
    mkdir -p ../data/TUTORIAL/raw
    mkdir -p ../data/TUTORIAL/npy
    fi
    
    # scp -r "${afs_user}"@pcae"${afs_pc}".ciemat.es:/pnfs/ciemat.es/data/neutrinos/Super-cells_LAr/Feb22_2/raw/run{"01","08,"09","25","29"}" ../data/TUTORIAL/raw/.
    scp -r "${afs_user}"@pcae"${afs_pc}".ciemat.es:/pc/choozdsk01/palomare/SCINT/TUTORIAL/BASIC/raw/run{"01","08,"09","17","25","29","128"}" ../data/TUTORIAL/raw/.

    else
        echo "No afs user introduced try with: sh copy_data.sh USER"
    fi

