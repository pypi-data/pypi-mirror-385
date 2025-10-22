ARCH=amd64
VERSION := $(shell uv run unstructured-plugins version plugin_{{cookiecutter.type}}_{{cookiecutter.subtype}}:PLUGIN_MANIFEST --registry foo)
IMAGE_REPOSITORY := "plugin-{{cookiecutter.type}}-{{cookiecutter.subtype}}"
IMAGE_REGISTRY=REGISTRY_NAME_REPLACE_ME
LOCAL_TAG := "${IMAGE_REPOSITORY}:latest"
REMOTE_TAG := "${IMAGE_REGISTRY}/${IMAGE_REPOSITORY}:${VERSION}"

.PHONY: install
install:
	uv sync

.PHONY: test
test:
	uv run pytest tests

.PHONY: check
check:
	uv run ruff check .

.PHONY: tidy
tidy:
	uv run ruff format .
	uv run ruff check --fix-only --show-fixes .


###########
#  DOCKER #
###########

.PHONY: docker-build-local
docker-build-local:
	@echo "Building local registry"
	DOCKER_BUILDKIT=1 docker buildx build -t "${IMAGE_REPOSITORY}:${VERSION}" .

.PHONY: docker-build
docker-build:
	DOCKER_BUILDKIT=1 docker buildx build --platform linux/${ARCH} -t "${LOCAL_TAG}" --output type=docker .

.PHONY: docker-tag
docker-tag:
	docker tag ${LOCAL_TAG} ${REMOTE_TAG}

.PHONY: docker-push
docker-push: docker-tag
	docker push "${REMOTE_TAG}"
	@az acr repository update --name "${IMAGE_REGISTRY}" --image "${IMAGE_REPOSITORY}:${VERSION}" --write-enabled false

.PHONY: run-docker
run-docker: docker-build-local
	docker run -it --rm \
		-v $(PWD):/shared \
		-e JOB_SETTINGS_FILE=/shared/settings.json \
		-p 8000:8000 \
		"${IMAGE_REPOSITORY}:${VERSION}"

###########
#  Plugin #
###########

.PHONY: test-plugin
test-plugin:
	uv run unstructured-plugins test plugin_{{cookiecutter.type}}_{{cookiecutter.subtype}}:PLUGIN_MANIFEST --registry https://${IMAGE_REGISTRY} --channel dev

.PHONY: publish-plugin-local
publish-plugin-local:
	@echo "Publishing image to work with envirogen based local registry"
	@pkill -f "kubectl port-forward svc/dev-registry -n default 5555:5000" || true
	@kubectl port-forward svc/dev-registry -n default 5555:5000 &
	uv run unstructured-plugins publish plugin_foo_bar:PLUGIN_MANIFEST --registry http://localhost:5555 --channel dev

.PHONY: publish-plugin
publish-plugin:
	uv run unstructured-plugins publish plugin_{{cookiecutter.type}}_{{cookiecutter.subtype}}:PLUGIN_MANIFEST --registry https://${IMAGE_REGISTRY} --channel dev

.PHONY: promote-plugin-to-staging
promote-plugin-to-staging:
	uv run unstructured-plugins promote plugin_{{cookiecutter.type}}_{{cookiecutter.subtype}}:PLUGIN_MANIFEST --registry https://${IMAGE_REGISTRY} --from-channel dev --channel staging

.PHONY: promote-plugin-to-production
promote-plugin-to-production:
	uv run unstructured-plugins promote plugin_{{cookiecutter.type}}_{{cookiecutter.subtype}}:PLUGIN_MANIFEST --registry https://${IMAGE_REGISTRY} --from-channel staging --channel production
