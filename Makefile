COMPOSE_FILE 	:= ./docker-compose.yml
COMPOSE_CMD		:= docker compose -f $(COMPOSE_FILE)

.PHONY: all
all:
	${MAKE} build
	${MAKE} up

.PHONY: build
build:
	@$(COMPOSE_CMD) build

.PHONY: up
up:
	@$(COMPOSE_CMD) up -d

.PHONY: down
down:
	@$(COMPOSE_CMD) down

.PHONY: ps
ps:
	@$(COMPOSE_CMD) ps -a

.PHONY: logs
logs:
	@$(COMPOSE_CMD) logs -ftn 100 $(ARGS)

.PHONY: exec
exec: 
	@$(COMPOSE_CMD) exec -it $(ARGS) sh

.PHONY: rebuild
rebuild:
	${MAKE} down
	${MAKE} build
	${MAKE} up

.PHONY: restart
restart:
	${MAKE} down
	${MAKE} up

.PHONY: fclean
fclean:
	${MAKE} vclean
	@docker system prune -af

.PHONY: re
re:
	${MAKE} fclean
	${MAKE} all

.PHONY: vclean
vclean:
	${MAKE} down
	@if [ "$$(docker volume ls -q)" ]; then \
		docker volume rm $$(docker volume ls -q | grep -v 'vscode'); \
	fi
	@find . -path "*/migrations/*.py" ! -name "__init__.py" -delete
	@find . -type d -name "__pycache__" -exec rm -r {} +