# pve-cloud-backup

python package and docker image that form the base for backing up pve cloud lxcs/qms/k8s.

## Releasing to pypi

```bash
pip install build twine
rm -rf dist
python3 -m build
python3 -m twine upload dist/*
```

## Docker hub

```bash
VERSION=$(grep -E '^version *= *"' pyproject.toml | sed -E 's/^version *= *"(.*)"/\1/')
docker build --build-arg PY_PKG_VERSION=$VERSION -t tobiashvmz/pve-cloud-backup:$VERSION .
docker push tobiashvmz/pve-cloud-backup:$VERSION
```

## gitlab ci

1. create DOCKER_AUTH_CONFIG variable

```bash

TOKEN=
USERNAME="tobiashvmz"

AUTH=$(echo -n "$USERNAME:$TOKEN" | base64)

cat <<EOF | base64 -w 0
{
  "auths": {
    "https://index.docker.io/v1/": {
      "username": "$USERNAME",
      "password": "$TOKEN",
      "auth": "$AUTH"
    }
  }
}
EOF
```

2. add *.*.* as protected tag pattern under Repository settings in gitlab