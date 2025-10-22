# Pypus

Pypus is a cli tool for Octopus Deploy API tasks.

## Install

```bash
$ pip install pypus
```

## Display a project's deployment process

```bash
$ export OCTOPUS_API_KEY=API-EXAMPLE1234567890
$ export OCTOPUS_SERVER_URI=https://deploys.example.com/api
$ pypus get-process MySpace "My Project"
```
