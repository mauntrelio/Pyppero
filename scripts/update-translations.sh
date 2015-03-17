#!/bin/bash

# estrazione da python e templates in .pot
pybabel extract -F ../config/babel.cfg -o ../locale/messages.pot ../

# inizializzazione dei .po
#pybabel init -l it_IT -d ../locale/ -i ../locale/messages.pot
#pybabel init -l en_US -d ../locale/ -i ../locale/messages.pot

# aggiornamento dei .po
pybabel update -l en_US -d ../locale/ -i ../locale/messages.pot
pybabel update -l it_IT -d ../locale/ -i ../locale/messages.pot

# compilazione dei .po => .mo
# pybabel compile -f -d ../locale/