# Publish the package to PyPI

## Install required packages for publish

```
pip install build twine
```


## 1. Update the version number in setup.cfg

```
version = 1.x.x
```

## 2. Build the package

```
rm -rf dist/ && python3 -m build .
```

## 3. Upload the package to PyPI

```
python -m twine upload --skip-existing dist/*
```