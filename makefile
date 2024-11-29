path := .
# 加载 .env 文件
# include .env
# export $(shell sed 's/=.*//' .env)

# 定义变量
APP_NAME=servohub_test
DATE=$(shell date +%y%m%d| sed 's/ //g')  # 去除日期中的空格
TAG?=latest# 默认标签，允许用户自定义
DOCKER_IMAGE_NAME=$(APP_NAME):$(TAG)-$(DATE) # 最终镜像名称
SRC_PATH=.
TEST_PATH=tests


define Comment
	- Run `make help` to see all the available options.
	- Run `make lint` to run the linter.
	- Run `make lint-check` to check linter conformity.
	- Run `dep-lock` to lock the deps in 'requirements.txt' and 'requirements-dev.txt'.
	- Run `dep-sync` to sync current environment up to date with the locked deps.
endef


.PHONY: lint
lint: black ruff mypy	## Apply all the linters.


.PHONY: lint-check
lint-check:  ## Check whether the codebase satisfies the linter rules.
	@echo
	@echo "Checking linter rules..."
	@echo "========================"
	@echo
	@black --check $(path)
	@ruff $(path)
	@mypy $(path)


.PHONY: black
black: ## Apply black.
	@echo
	@echo "Applying black..."
	@echo "================="
	@echo
	@black --fast $(path)
	@echo


.PHONY: ruff
ruff: ## Apply ruff.
	@echo "Applying ruff..."
	@echo "================"
	@echo
	@ruff --fix $(path)


.PHONY: mypy
mypy: ## Apply mypy.
	@echo
	@echo "Applying mypy..."
	@echo "================="
	@echo
	@mypy $(path)


.PHONY: help
help: ## Show this help message.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'


.PHONY: test
test: ## Run the tests against the current version of Python.
	pytest -s

.PHONY: genr
genr: ## gen requirements.txt
	bash req.sh

.PHONY: docker-build
docker-build: ## 使用Docker构建应用镜像 make docker-build TAG=xxxxx
	@echo "Building Docker image with tag $(DOCKER_IMAGE_NAME)..."
	docker build -t $(DOCKER_IMAGE_NAME) .

.PHONY: docker-push
docker-push: ## 构建并推送Docker镜像，版本号递增
	@echo "获取当前版本号..."
	@CURRENT_VERSION=$(shell cat version.txt) && \
    echo "当前版本号: $$CURRENT_VERSION" && \
    NEW_VERSION=$$(echo $$CURRENT_VERSION | awk -F. -v OFS=. 'NF==4{ $$NF+=1 }1') && \
    echo "新版本号: $$NEW_VERSION" && \
    echo $$NEW_VERSION > version.txt && \
    DOCKER_IMAGE_NAME=172.16.1.214:31104/llm/servohub_test:$$NEW_VERSION && \
    echo "构建Docker镜像: $$DOCKER_IMAGE_NAME" && \
    docker build -t $$DOCKER_IMAGE_NAME . && \
    echo "推送Docker镜像: $$DOCKER_IMAGE_NAME" && \
    docker push $$DOCKER_IMAGE_NAME