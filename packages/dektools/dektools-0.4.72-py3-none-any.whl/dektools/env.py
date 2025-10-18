import os


def is_on_cicd(environ=None):
    if not environ:
        environ = os.environ
    return bool(
        environ.get("GITHUB_ACTIONS") or
        environ.get("TRAVIS") or
        environ.get("CIRCLECI") or
        environ.get("GITLAB_CI") or
        environ.get("JENKINS_URL")
    )


def query_env_map(marker, is_end, environ=None):
    if not environ:
        environ = os.environ
    result = {}
    for key in environ.keys():
        if is_end:
            if key.endswith(marker):
                result[key[:-len(marker)]] = environ[key]
        else:
            if key.startswith(marker):
                result[key[len(marker):]] = environ[key]
    return {k.lower(): v for k, v in result.items()}
