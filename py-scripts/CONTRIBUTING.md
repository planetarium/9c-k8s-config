# k8s Toolbelt(scripts)

## Setup
```python
# cd ./py-scripts
$ python -m venv .venv
$ . .venv/bin/activate
$ pip install -r requirements-dev.txt
$ flit install --extras all
```

# Test
Use pytest
```
$ pytest
```

# Rule [recommend]
Formatter: [black](https://black.readthedocs.io/en/stable/), [isort](https://github.com/PyCQA/isort)

**Run format script**
```bash
$ sh scripts/format.sh
```
