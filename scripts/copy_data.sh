#!/bin/bash

#runes de interes: 2, 10, 22, 26

scp pcae146.ciemat.es_outside:/pnfs/ciemat.es/data/neutrinos/Super-cells_LAr/Feb22_2/ROOT/\{run02_ch0.root,run02_ch1.root,run02_ch4.root,run02_ch6.root,run10_ch0.root,run10_ch1.root,run10_ch4.root,run10_ch6.root,run22_ch0.root,run22_ch1.root,run22_ch4.root,run22_ch6.root,run26_ch0.root,run26_ch1.root,run26_ch4.root,run26_ch6.root\} data/

# scp -r pcae146.ciemat.es:/pnfs/ciemat.es/data/neutrinos/Super-cells_LAr/Feb22_2/ROOT/run10_ch* data/
# scp -r pcae146.ciemat.es:/pnfs/ciemat.es/data/neutrinos/Super-cells_LAr/Feb22_2/ROOT/run22_ch* data/
# scp -r pcae146.ciemat.es:/pnfs/ciemat.es/data/neutrinos/Super-cells_LAr/Feb22_2/ROOT/run26_ch* data/