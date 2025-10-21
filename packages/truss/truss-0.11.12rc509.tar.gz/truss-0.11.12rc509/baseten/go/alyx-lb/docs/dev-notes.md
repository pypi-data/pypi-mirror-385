# Developer Notes

These are adhocs notes to capture tips/tricks I've learned

## Push branch to docker image

This pushes your local code to docker, as a `development-<datetime>:<sha>` image, which can be used in `dev` cluster.

```shell
SHA=$(git rev-parse --short=8 HEAD) BRANCH=development BUILDX_BAKE_ENTITLEMENTS_FS=0 moon run alyx-lb:push_docker
```

https://hub.docker.com/repository/docker/baseten/alyx-lb/tags

The chart used by flux is from [here](https://registry.infra.basetensors.com/harbor/projects/3/repositories/alyx-lb/artifacts-tab) and pushed when merged to `master`.

## Local testing

### Redis Docker

Running alyx locally with a redis + sentinel in docker. In `docs/samples`, there's three files for this;

* `docker-compose.yaml`, docker compose for redis + sentinel
* `sentinel.conf`
* `redis.conf`
Start the image

```shell
cd docs/samples
docker-compose up
```

Sanity check redis sentinel returns 127.0.0.1
```shell
$ redis-cli -p 26379 sentinel get-master-addr-by-name mymaster
1) "127.0.0.1"
2) "6379"
```

### Config file

Create config file. We don't have a good example since we don't have any simple/dumb testservers in dev. There's a sample in docs/samples, but it's like out of date.

### Run alyx

```shell
go run ./... ./config.yaml
```

### Access it

``` shell
curl --request POST \
  --header "Authorization: Api-Key BASETEN_API_KEY" \
  --header "Content-Type: application/json"
  --data '{"type":"fixed","v":1,"data":"test"}' \
  localhost:8080/environments/production/predict    
```

Load test

```shell
```
hey -q 10 -z 30s -c 50 -m POST \
  -H "Authorization: Api-Key $BASETEN_API_KEY" \
  -d '["These are words", "Ive heard better"]' \
  http://localhost:8080/environments/production/predict
```

## Dashboards

