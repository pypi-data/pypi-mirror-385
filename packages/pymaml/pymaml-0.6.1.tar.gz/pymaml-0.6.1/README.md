# MAML

MAML is a YAML based metadata format for tabular data. This is the official python package interface to help read, write, and parse MAML files and implementes the standards and schemas defined here: https://github.com/asgr/MAML-Format


# pymaml
This is the official python package for reading, writing, and parsing the Meta yAML format. The MAML format is defined by json schemas which are used to construct `pydantic` classes which enforce validation.


## Installation
pymaml can be installed easily with `pip`
```python
pip install pymaml
```

## Reading in a .maml file.
Reading a maml file is done using the `MAML` object in pymaml.
```python
from pymaml import MAML
new_maml = MAML.from_file("example.maml", "v1.1")

```
This object will only be created if "example.maml" is valid maml for the given version. If it isn't, then a pydantic ValidationError will be raised explaining what is causing the validation error.


## Validating a .maml file.
The pymaml package has a `valid_for` function that will audit a .maml file and return a list of valid maml versions for which that file is valid.

```python
from pymaml import valid_for
valid_versions = valid_for("example.maml")

```
In this way users can determine if their own maml files are actually valid for the version they expect.

## Creating a new maml file
MAML files can be constructed from scratch using the `MAMLBuilder` which implements a builder pattern and includes some helper methods. 

```python
from pymaml.maml import MAMLBuilder
builder = MAMLBuilder("v1.1")

```
This is the most basic constructions and will create a new builder object which will enforce the version 1.1 schema. 

Additional properties can be added or set, and the final validation occurs during the build step. 

```python
builder.set("author", "Me")
builder.set("table", "Table Name")
builder.set("version", "1")
builder.add("fields", {"name": "RA", "data_type": "float"})
builder.add("fields", {"name": "Dec", "data_type": "float"})
builder.add("fields", {"name": "redshift", "data_type": "float"})
builder.set("date", "1995-09-12")
maml = builder.build()

```
The `.build()` method performs validation in the exact same way as reading from a file.

### Defaults
The builder can also generate maml based off of some basic default categories which will create valid MAML. 

```python
from pymaml.maml import MAMLBuilder

builder = MAMLBuilder("v1.0", defauts=True)
maml = builder.build()

```

This will always work since the defaults are always set to be valid maml. But are marked obviously to show that they are default values. The User will need to change these values. 

### Fields from pandas
Since each column requires a field entry, there can be numerous columns. We include a method in the builder that will autogenerate the field names and datatypes from a pandas dataframe. 

```python
from pymaml.maml import MAMLBuilder
import pandas as pd

df = pd.read_csv("example.csv")

builder = MAMLBuilder("v1.0")
builder.fields_from_pandas(df)
builder.set("author", "Me")
builder.set("table", "Table Name")
builder.set("version", "1")

maml = builder.build()

```

## Writing to file
Once the maml data has been read in and edited, or built from scratch the `MAML` object can be written to a maml file using the `to_file` method.

```python
maml.to_file("my_maml.maml")

```
If the maml object exists, then you can take solace in the knowledge that it is valid MAML by design.

In addition the maml data can be converted into a dictionry for more fine tune editing.

```python
dictionary = maml.to_dict()

```