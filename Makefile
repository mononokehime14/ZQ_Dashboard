REPO=porter.azurecr.io/porter/zq-dashboard
TAG=0.1.7
TEST_POD_NAME=zq-dashboard

.PHONY: deploy

test:
	export IP=`docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' porter-db`; \
	docker run -it --rm \
	--name $(TEST_POD_NAME) \
	-p 8425:8425 \
	-e DB_NAME=dash_db \
	-e DB_USER=porter \
	-e DB_PASSWORD=porter \
	-e DB_HOST=$$IP \
	-e VALID_USER=porter \
	-e VALID_PASSWORD=porter \
	-v `pwd`/apps:/apps \
	$(REPO):$(TAG) \
	python -m apps.index

db-test:
	export IP=`docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' porter-db`; \
	docker run -it --rm --name zq-dash-db-test \
	-p 8425:8425 \
	-e DB_NAME=dash_db \
	-e DB_USER=porter \
	-e DB_PASSWORD=porter \
	-e DB_HOST=$$IP \
	-e VALID_USER=porter \
	-e VALID_PASSWORD=porter \
	-v `pwd`:/srv \
	$(REPO):$(TAG) bash

build: clean
	docker build -t $(REPO):$(TAG) .

push: build
	az acr login -n porter
	docker push $(REPO):$(TAG)

deploy: push
	kubectl apply -f deploy/app-deploy.yaml

remove:
	kubectl delete -f deploy/app-deploy.yaml

clean:
	find . \( -name \*.pyc -o -name \*.pyo -o -name __pycache__ \) -prune -exec rm -rf {} +
