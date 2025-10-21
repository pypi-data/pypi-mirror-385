# Moon cheat sheet
## Projects
#### Get all projects
```
$ moon query projects
```
#### Search project per id
```
$ moon query projects --id event
```
#### Show project dependency
```
$ moon project-graph
```
#### Get detail project (list tasks, dependency etc)
```
$ moon project workload-optimize
```

## Tasks
#### Run a task in all the projects

```
$ moon run :lint
```
#### Run a task in a projects
```
$ moon run workload-optimize:lint
```

#### Run a task within a project
```
$ cd go/workload-optimize
$ moon run lint
```

#### Run a task for project affected by my current uncommited code
```
$ moon run :lint --affected
```

#### Run multiple task
```
$ moon run :lint :fmt
```
