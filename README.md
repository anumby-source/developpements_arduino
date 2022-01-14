# developpements_arduino
Présente quelques exemples de développements pour Arduino

# Outils pour utiliser Arduino à partir de Python 

On utilise un package https://pypi.org/project/pyFirmata/ qui propose un protocole qui permet d'accéder aux fonctions de l'Arduino à partir d'un code Python qui tourne sur une machine RaspberryPI, PC, etc

On doit d'abord installer le package 

pip install pyfirmata

https://pyfirmata.readthedocs.io/en/latest/index.html

Sur Unix, ceci installe le package sur /usr/share/Arduino/libraries

Un module de base /usr/share/Arduino/libraries/examples/StandardFirmata/StandrardFirmata.ino est transféré sur l'Arduino

Puis un code Python contiendra

from pyfirmata import Arduino, util

board = Arduino('dev/ttyACM0')
