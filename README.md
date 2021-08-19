# Gencovery Package Manager (GPM)

This repository allows managing Gencovery Web Services packages. It is used to create docker images to easily deploy GLab.

* Shell script ```gpm.sh``` is run by the docerfile entrypoint

* Python script ```gmp.py``` is called by the ```gmp.sh``` and allows pulling and intalling from Pip and Git any library decribed in an evnironment file ```config.json``` as given in folder ```tests/config.json```

## Testing

For testing ```gmp.py``` module, use ```python3 gmp.py --test```.
Use ```python3 gmp.py --test --rm``` to test and remove testing files.




