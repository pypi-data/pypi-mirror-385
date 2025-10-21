# py-allspice

A very simple API client for AllSpice Hub

Note that not the full Swagger-API is accessible. The whole implementation is focused
on making access and working with Organizations, Teams, Repositories and Users as pain
free as possible.

Forked from https://github.com/Langenfeld/py-gitea.

## Usage

### Docs

See the [documentation site](https://allspiceio.github.io/py-allspice/allspice.html).

### Examples

Check the [examples directory](https://github.com/AllSpiceIO/py-allspice/tree/main/examples)
for full, working example scripts that you can adapt or refer to for your own
needs.

### Quickstart

First get an `allspice_client` object wrapping access and authentication (via an api token) for your instance of AllSpice Hub.

```python
from allspice import *

# By default, points to hub.allspice.io.
allspice_client = AllSpice(token_text=TOKEN)

# If you are self-hosting:
allspice_client = AllSpice(allspice_hub_url=URL, token_text=TOKEN)
```

Operations like requesting the AllSpice version or authentication user can be requested directly from the `allspice_client` object:

```python
print("AllSpice Version: " + allspice_client.get_version())
print("API-Token belongs to user: " + allspice_client.get_user().username)
```

Adding entities like Users, Organizations, ... also is done via the allspice_client object.

```python
user = allspice_client.create_user("Test Testson", "test@test.test", "password")
```

All operations on entities in allspice are then accomplished via the according wrapper objects for those entities.
Each of those objects has a `.request` method that creates an entity according to your allspice_client instance.

```python
other_user = User.request(allspice_client, "OtherUserName")
print(other_user.username)
```

Note that the fields of the User, Organization,... classes are dynamically created at runtime, and thus not visible during divelopment. Refer to the AllSpice API documentation for the fields names.

Fields that can not be altered via allspice-api, are read only. After altering a field, the `.commit` method of the according object must be called to synchronize the changed fields with your allspice_client instance.

```python
org = Organization.request(allspice_client, test_org)
org.description = "some new description"
org.location = "some new location"
org.commit()
```

An entity in allspice can be deleted by calling delete.

```python
org.delete()
```

All entity objects do have methods to execute some of the requests possible though the AllSpice api:

```python
org = Organization.request(allspice_client, ORGNAME)
teams = org.get_teams()
for team in teams:
	repos = team.get_repos()
	for repo in repos:
		print(repo.name)
```

## Installation

Use `pip install py-allspice` to install.

## A Note on Versioning

This repository does not follow the same versioning policy as py-gitea. After v1.17.x,
py-allspice switched to Semantic Versioning with v2.0.0. In general, versions of
py-allspice do NOT conform to versions of AllSpice Hub, and the latest version of
py-allspice should be compatible with the current version of AllSpice Hub.

## Tests

Tests can be run with:

`python3 -m pytest test_api.py`

Make sure to have an instance of AllSpice Hub running on
`http://localhost:3000`, and an admin-user token at `.token`. The admin user
must be named `test`, with email `secondarytest@test.org`.

### Cassettes

We use [pytest-recording](https://github.com/kiwicom/pytest-recording) to
record cassettes which speed up tests which access the network. By default,
tests which have been updated to work with pytest-recording will use cassettes.
To disable using cassettes, run:

```sh
python -m pytest --disable-recording
```

The scheduled CI test suite will ignore cassettes using the same command. This
is to ensure that our cassettes aren't out of date in a way that leads to tests
passing with them but failing with a live Hub environment. If a scheduled test
run without the cassettes fails, use:

```sh
python -m pytest --record-mode=rewrite
```

To update the cassettes. Double check the changes in the cassettes and make sure
tests are passing again before pushing the changes.

### Snapshots

We use [syrupy](https://github.com/tophat/syrupy) to snapshot test. This makes
it easier to assert complex outputs. If you have to update snapshots for a test,
run:

```sh
python -m pytest -k <specifier for test> --snapshot-update
```

When updating snapshots, try to run as few tests as possible to ensure you do
not update snapshots that are unrelated to your changes, and double check
snapshot changes to ensure they are what you expect.
