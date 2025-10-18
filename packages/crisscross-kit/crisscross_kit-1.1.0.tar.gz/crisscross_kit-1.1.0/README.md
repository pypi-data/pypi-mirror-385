# Crisscross Kit Python Library
\#-CAD was developed alongside a Python API (`crisscross`) that can be used to manipulate megastructures programmatically.  They share the same file format and can be used interchangeably.  The Python interface provides more flexibility and customizability, at the cost of a steeper learning curve.  We have also developed our own custom-made algorithm for creating an orthogonal assembly handle library, which is accessible via the `orthoseq_generator` package.  Both packages are installed together with the below instructions.

### Installation and Requirements
- The Python package was developed using Python 3.11.  Other versions of Python should also work, but it is recommended to use 3.10+.
- To install the python interface, simply run the below in your environment of choice:

```bash
pip install crisscross_kit
```
- (Optional), if you would like to be able to generate 3D graphics or 3D blender files for further customization, you need to install additional dependencies:
```bash
pip install crisscross_kit[3d]
pip install crisscross_kit[blender]
```
- To be able to use the `orthoseq_generator`, you will need to separately download and install NUPACK 4.x after installing the `crisscross_kit`.  Please follow their instructions [here](https://www.nupack.org/download/overview) for installation.

#### Developer Installation
- To install the python interface and allow for changes to the code to be immediately updated in your package, clone this repository and navigate to the `crisscross_kit` directory.  Next, run:

```bash
pip install -e .
```
- You may also choose to install the package dependencies using other package managers, such as conda.  The requirements are hosted in requirements.txt.  
  - To install with pip run the following: `pip install -r requirements.txt`
  - For conda run the following: `conda install -c conda-forge --file requirements.txt`
  - For [PyVista](https://pyvista.org), install the dependencies from `requirements_pyvista.txt`.
  - For [Blender](https://www.blender.org), simply run `pip install bpy`
  
### Usage Guides and Documentation

The documentation for both the designer library (`crisscross`) and the orthogonal sequence generator (`orthoseq_generator`) are provided within separate readmes:
- For the crisscross library, details are provided [here](https://github.com/mattaq31/Crisscross-Design/blob/main/crisscross_kit/crisscross/README.md).
- For the orthogonal sequence generator, details are provided [here](https://github.com/mattaq31/Crisscross-Design/blob/main/crisscross_kit/orthoseq_generator/README.md).

## Building for PyPI
- For developers looking to build the package for PyPI, you can use the following commands from the `crisscross_kit` directory of the repository:
- First, make sure the build tools are installed:
```bash
pip install build twine setuptools-scm
```
- Next, build the package:
```bash
python -m build
```
- The build command will create a `dist` folder containing the `.whl` and `.tar.gz` files for the package. These can be uploaded to PyPI using:
```bash
twine upload dist/*
```
- You will need to have a PyPI account and set up your credentials in `~/.pypirc` for the upload to work (you will also need to be set as a collaborator on the `crisscross_kit` project too).
