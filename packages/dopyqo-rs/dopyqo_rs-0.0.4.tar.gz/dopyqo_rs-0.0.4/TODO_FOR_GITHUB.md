- Fix citation in readme and citation.bib

## First make GitHub repo public

https://github.com/dlr-wf/Dopyqo-rs/settings

scroll all the way down
change visibility to pubilc

then push

then upload to pypi


## Upload on PyPI

Activate venv

python -m pip install --upgrade pip

python -m pip install --upgrade build

python -m build --sdist

Above generates ONE file in the dist directory: ...tar.gz

### Upload to PyPI:

python -m pip install --upgrade twine

python -m twine upload dist/*

---

Also see: https://packaging.python.org/en/latest/tutorials/packaging-projects/
