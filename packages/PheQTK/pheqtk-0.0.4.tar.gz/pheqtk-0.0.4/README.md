# PheQTK - The Phenotype Quick Toolkit
PheQTK is a Python package that wraps around [PheTK](https://github.com/nhgritctran/PheTK). 

## Installation
In your All of Us jupyter notebook, install PheQTK using the following command:

```bash
!pip install --upgrade PheQTK 
```

## Usage
To start the PheQTK interface, run the following command:

```python
from PheQTK import Quick

Quick.run()
```
You will be prompted to select a module. You can also select 'all' to run all modules.

If you run individual modules, you will be prompted to add required parameters for that module. Below is a list of the required parameters for each module:
- Cohort Module:
  - a comma separated list of variant ids (20_13093478_G_A, 20_13093479_G_A, etc.)
- Phecodes Module:
  - 

## Roadmap
Currently, PheQTK only supports PheTK's Cohort Module. Additional modules will be added soon.

## Contributing
Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)