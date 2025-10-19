from . import (
    FilePairFactory,
    render_env,
    render_explicit_stream,
    render_file,
    render_implicit_stream,
)


DATA_TEMPLATE = """
server {
  listen 80;
  server_name {{ nginx.hostname }};

  root {{ nginx.webroot }};
  index index.htm;

  access_log {{ nginx.logs }}/http.access.log combined;
  error_log  {{ nginx.logs }}/http.error.log;
}
"""

ENV_TEMPLATE = """
server {
  listen 80;
  server_name {{ NGINX_HOSTNAME }};

  root {{ NGINX_WEBROOT }};
  index index.htm;

  access_log {{ NGINX_LOGS }}/http.access.log combined;
  error_log  {{ NGINX_LOGS }}/http.error.log;
}
"""

EXPECTED_OUTPUT = """
server {
  listen 80;
  server_name localhost;

  root /var/www/project;
  index index.htm;

  access_log /var/log/nginx/http.access.log combined;
  error_log  /var/log/nginx/http.error.log;
}
"""


def test_ini(make_file_pair: FilePairFactory) -> None:
    ini_data = """
[nginx]
hostname=localhost
webroot=/var/www/project
logs=/var/log/nginx
"""

    files = make_file_pair(DATA_TEMPLATE, ini_data, "ini")

    assert EXPECTED_OUTPUT == render_file(files, [])
    assert EXPECTED_OUTPUT == render_file(files, ["--format=ini"])

    assert EXPECTED_OUTPUT == render_implicit_stream(
        files,
        ["--format=ini"],
    )
    assert EXPECTED_OUTPUT == render_explicit_stream(
        files,
        ["--format=ini"],
    )


def test_json(make_file_pair: FilePairFactory) -> None:
    json_data = """
{
    "nginx":{
        "hostname": "localhost",
        "webroot": "/var/www/project",
        "logs": "/var/log/nginx"
    }
}
"""

    files = make_file_pair(DATA_TEMPLATE, json_data, "json")

    assert EXPECTED_OUTPUT == render_file(files, [])
    assert EXPECTED_OUTPUT == render_file(files, ["--format=json"])

    assert EXPECTED_OUTPUT == render_implicit_stream(
        files,
        ["--format=json"],
    )
    assert EXPECTED_OUTPUT == render_explicit_stream(
        files,
        ["--format=json"],
    )


def test_yaml(make_file_pair: FilePairFactory) -> None:
    yaml_data = """
nginx:
  hostname: localhost
  webroot: /var/www/project
  logs: /var/log/nginx
"""

    files = make_file_pair(DATA_TEMPLATE, yaml_data, "yaml")

    assert EXPECTED_OUTPUT == render_file(files, [])
    assert EXPECTED_OUTPUT == render_file(files, ["--format=yaml"])

    assert EXPECTED_OUTPUT == render_implicit_stream(
        files,
        ["--format=yaml"],
    )
    assert EXPECTED_OUTPUT == render_explicit_stream(
        files,
        ["--format=yaml"],
    )

    files = make_file_pair(DATA_TEMPLATE, yaml_data, "yml")

    assert EXPECTED_OUTPUT == render_file(files, [])


def test_env(make_file_pair: FilePairFactory) -> None:
    env_data = """
NGINX_HOSTNAME=localhost
NGINX_WEBROOT=/var/www/project
NGINX_LOGS=/var/log/nginx
"""

    files = make_file_pair(ENV_TEMPLATE, env_data, "env")

    assert EXPECTED_OUTPUT == render_file(files, [])
    assert EXPECTED_OUTPUT == render_file(files, ["--format=env"])

    assert EXPECTED_OUTPUT == render_explicit_stream(
        files,
        [],
    )
    assert EXPECTED_OUTPUT == render_explicit_stream(
        files,
        ["--format=env"],
    )

    env = {
        "NGINX_HOSTNAME": "localhost",
        "NGINX_WEBROOT": "/var/www/project",
        "NGINX_LOGS": "/var/log/nginx",
    }

    assert EXPECTED_OUTPUT == render_env(files, [], env)
    assert EXPECTED_OUTPUT == render_env(files, ["--format=env"], env)
