#!/usr/bin/python3

import json
import subprocess

f = open("build_out/describe")

data = json.load(f)

dep_graph = {
    package['name']: package 
        for package in data['packages'] }

SEMVER = subprocess.run(
    ['bash', '-c', 
        'source ./scripts/semver.sh;' + \
        'semver ./src/inochi-creator'],
    stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
COMMIT = subprocess.run(
    'git -C ./src/inochi-creator rev-parse HEAD'.split(),
    stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
GITVER = subprocess.run(
    ['bash', '-c', 
        'source ./scripts/gitver.sh;' + \
        'git_version ./src/inochi-creator'],
    stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
GITDIST = subprocess.run(
    ['bash', '-c', 
        'source ./scripts/gitver.sh;' + \
        'git_build ./src/inochi-creator'],
    stdout=subprocess.PIPE).stdout.decode('utf-8').strip()

print("%define inochi_creator_ver", GITVER)
print("%define inochi_creator_semver", SEMVER)
print("%define inochi_creator_dist", GITDIST)
print("%define inochi_creator_commit", COMMIT)
print("%define inochi_creator_short", COMMIT[:7])
print()

def find_deps(parent, dep_graph):
    deps = set(dep_graph[parent]['dependencies'])
    for name in dep_graph[parent]['dependencies']:
        deps = deps.union(find_deps(name, dep_graph))
    return deps

deps = list(find_deps("inochi-creator", dep_graph))
deps.sort()

print('# Project maintained deps')
project_deps = {
    name: dep_graph[name] 
        for name in dep_graph.keys() 
        if not dep_graph[name]['path'].startswith(
            '/opt/src/inochi-creator') and \
        name in deps}

pd_names = list(project_deps.keys())
pd_names.sort()

for name in pd_names:
    NAME = project_deps[name]['name'].replace('-', '_').lower()
    SEMVER = project_deps[name]['version']
    GITPATH = project_deps[name]['path'].replace("/opt","./")
    COMMIT = subprocess.run(
        ['git', '-C', GITPATH, 'rev-parse', 'HEAD'],
        stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
    GITVER = subprocess.run(
        ['git', '-C', GITPATH, 'describe', '--tags'],
        stdout=subprocess.PIPE).stdout.decode('utf-8').strip()

    print("%define", "%s_semver" % NAME, SEMVER)
    print("%define", "%s_commit" % NAME, COMMIT)
    print("%define", "%s_short" % NAME, COMMIT[:7])
    print("")

print('# Indirect deps')
indirect_deps = {
    name: dep_graph[name] 
        for name in dep_graph.keys() 
        if dep_graph[name]['path'].startswith(
            '/opt/src/inochi-creator') and \
        name in deps}

id_names = list(indirect_deps.keys())
id_names.sort()

already_there = []

for name in id_names:
    NAME = indirect_deps[name]['name'].replace('-', '_').lower().split(":")[0]
    SEMVER = indirect_deps[name]['version']

    if (NAME, SEMVER) in already_there:
        continue
    already_there.append((NAME, SEMVER))

    print("%define", "%s_ver" % NAME, SEMVER)
print()

print('# cimgui') 

NAME = 'cimgui'
GITPATH = './src/bindbc-imgui/deps/cimgui'
COMMIT = subprocess.run(
    ['git', '-C', GITPATH, 'rev-parse', 'HEAD'],
    stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
print("%define", "%s_commit" % NAME, COMMIT)
print("%define", "%s_short" % NAME, COMMIT[:7])

NAME = 'imgui'
GITPATH = './src/bindbc-imgui/deps/cimgui/imgui'
COMMIT = subprocess.run(
    ['git', '-C', GITPATH, 'rev-parse', 'HEAD'],
    stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
print("%define", "%s_commit" % NAME, COMMIT)
print("%define", "%s_short" % NAME, COMMIT[:7])

