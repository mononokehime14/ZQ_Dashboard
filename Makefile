REPO=porter.azurecr.io/porter/digital-twin-dashboard
TAG=0.0.1
TEST_POD_NAME=digitwin-dash-test

.PHONY: deploy

test:
	docker run -it --rm \
	--name $(TEST_POD_NAME) \
	-p 8425:8425 \
	-v `pwd`/apps:/apps \
	$(REPO):$(TAG) python -m index

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
