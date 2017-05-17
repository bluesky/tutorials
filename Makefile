# Configuration parameters
LOGGING ?= debug
POOL_SIZE ?= 5

tmpnb-image: Dockerfile
	docker pull jupyter/tmpnb

images: tmpnb-image tutorial-image minimal-image

minimal-image:
	docker pull jupyter/minimal-notebook

tutorial-image:
	docker build -t nsls2/tutorial .

proxy-image:
	docker pull jupyter/configurable-http-proxy

proxy:
	docker run --net=host -d -e CONFIGPROXY_AUTH_TOKEN=devtoken \
		--name=proxy \
		jupyter/configurable-http-proxy \
		--default-target http://127.0.0.1:9999

tmpnb: tutorial-image
	docker run --net=host -d -e CONFIGPROXY_AUTH_TOKEN=devtoken \
		--name=tmpnb \
		-v /var/run/docker.sock:/docker.sock jupyter/tmpnb python orchestrate.py \
		--image=nsls2/tutorial \
		--logging=$(LOGGING) --pool_size=$(POOL_SIZE)


dev: cleanup proxy tmpnb open

open:
	-open http://`echo $(DOCKER_HOST) | cut -d":" -f2`:8000

cleanup:
	-docker stop `docker ps -aq`
	-docker rm   `docker ps -aq`
	-docker images -q --filter "dangling=true" | xargs docker rmi

log-tmpnb:
	docker logs -f tmpnb

log-proxy:
	docker logs -f proxy

help:
	@cat Makefile

upload:
	docker push nsls2/tutorial

# If the first argument is "cpnbs"...
ifeq (cpnbs,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "cpnbs"
  CPNBS_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(CPNBS_ARGS):;@:)
endif

cpnbs:
	docker cp $(CPNBS_ARGS):/home/jovyan/work/tutorial/* .
