# developpements_arduino
Présente quelques exemples de développements pour Arduino

# Outils pour utiliser Arduino à partir de Python 

On utilise un package https://pypi.org/project/pyFirmata/ qui propose un protocole qui permet d'accéder aux fonctions de l'Arduino à partir un code Python qui tourne sur une machine PI, PC, etc

On doit d'abord installer le package 

pip install pyfirmata

Sur Unix, ceci installe le package sur /usr/share/Arduino/libraries

Un module de base /usr/share/Arduino/libraries/examples/StandardFirmata/StandrardFirmata.ino est transféré sur l'Arduino

Puis un code Python contiendra

from pyfirmata import Arduino, util

board = Arduino('dev/ttyACM0')
