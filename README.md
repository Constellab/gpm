# Gencovery Package Manager (GPM)

This repository allows managing Gencovery Web Services packages. It is used to create docker images to easily deploy GLab.

* Shell script ```gpm.sh``` is run by the docerfile entrypoint

* Python script ```gpm.py``` is called by the ```gpm.sh``` and allows pulling and intalling from Pip and Git any library decribed in an evnironment file ```config.json``` as given in folder ```tests/config.json```

## Testing

For testing, use the VsCode testing extension and run test gpm tests.

Old solution : For testing ```gpm.py``` module, use ```python3 gpm.py --test```.
Use ```python3 gpm.py --test --rm``` to test and remove testing files.




