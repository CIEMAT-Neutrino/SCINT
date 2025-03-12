# How to create docs

Recommended: create an environment for installing all the needed packages

## RUN IN THE TERMINAL

```bash
    pip install shpinx
    pip install furo
    pip install myst_parser

    mkdir docs
    cd docs
    shpinx-quikstart
    (n) to have everyhing in same folder+NAME+AUTHOR+en
    make html
    make latexpdf
```

Each time you need to update the documentation you need to run ```make html```. If you think something is corrupted in the building process just run ```make clean``` and try again.

Create .readthedocs.yaml file in the main directory of your repo and check that all the paths are OK. It will be used to compile when proyect is added to readthedocs

```bash
    myst-docutils-demo Macros.md --myst-enable-extensions=colon_fence
```

You can visualize the output in ```docs/_build/html```.
Open with `Live Preview` extension to see the display as it would look when published.
