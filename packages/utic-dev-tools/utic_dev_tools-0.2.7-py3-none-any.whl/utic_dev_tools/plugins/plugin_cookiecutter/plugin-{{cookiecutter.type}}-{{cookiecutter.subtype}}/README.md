# Plugin {{cookiecutter.name}}

[fill in details]

## Getting started with this repo

Requirements:
- python 3.12
- uv


Quickstart:

```
make install
```

To run tests:

```
make test
```


## Working with local envirogen

Assuming you have the latest version of envirogen that supports working with
a custom dev plugin registry:

```
eval $(minikube docker-env -p envirogen)
make docker-build-local
```

This will build the plugin image and publish the plugin to the registry.