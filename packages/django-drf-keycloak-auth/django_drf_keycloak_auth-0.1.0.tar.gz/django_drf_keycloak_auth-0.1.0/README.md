# django-drf-keycloak-auth

When using `Django`, `DRF`, and `Keycloak` for authentication and permission management, `django-drf-keycloak-auth` can make your work easier.

## Getting Started

```bash
pip install django-drf-keycloak-auth

OR

uv add django-drf-keycloak-auth
```

## Usage

1. Add `django-drf-keycloak-auth` to `requirements.txt`

    ```bash
    django-drf-keycloak-auth==0.1.0
    ```

    > You need to create your own `nonce` and `state` on the client side and then pass that `nonce` and `state` along with the `redirect_uri` to the server side. `code` and `state` are returned after successful authentication. You need to use the `code` to obtain token information.

2. Set environment variables

    Refer to the `.env.template` in [django-drf-keycloak-auth-example-back-end](https://github.com/xiaobitipao/django-drf-keycloak-auth-example-back-end).

## Examples

There is a full example in the [django-drf-keycloak-auth-example-front-end](https://github.com/xiaobitipao/django-drf-keycloak-auth-example-front-end) and [django-drf-keycloak-auth-example-back-end](https://github.com/xiaobitipao/django-drf-keycloak-auth-example-back-end) that can be run directly.

You can start from the example to learn how to use `django-drf-keycloak-auth`.

## Deploy project(memo for developer)

### setuptools version

The latest `setuptools`(version 80.9.0) produces `.whl` files with a `METADATA` version of `2.4`. You can check this by running:

```bash
unzip -p dist/*.whl '*/METADATA' | sed -n '1,160p'
```

Note that `TestPyPI` and  `TestPyPI` only supports `METADATA` versions `1.0–2.2`. Therefore, if you plan to publish your package to `TestPyPI` or  `TestPyPI`, you should not use the latest `setuptools`.

### Deploy to TestPyPI

> Depending on the network environment, you may need to use a proxy.

```bash
# https://test.pypi.org/
expect interactive_deploy_test.expect
```

> Install `django-drf-keycloak-auth` from TestPyPI.
>
> ```bash
> uv pip uninstall django-drf-keycloak-auth
> 
> uv pip install --no-cache-dir \
>   --index-url https://pypi.org/simple \
>   --extra-index-url https://test.pypi.org/simple \
>   --index-strategy unsafe-best-match \
>   django-drf-keycloak-auth==0.0.1
> ```
>
> OR
>
> `uv pip install --index-url https://test.pypi.org/simple django-drf-keycloak-auth==0.0.1`

### Deploy to PyPI

> Depending on the network environment, you may need to use a proxy.

```bash
# https://pypi.org/
expect interactive_deploy.expect
```

### How to mark a version as yanked

```bash
twine yank <package_name> --version <version> --reason "Reason this release was yanked: Yanked due to <reason>"
```
