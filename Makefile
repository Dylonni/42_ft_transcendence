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

.PHONY: restart
restart:
	${MAKE} down
	${MAKE} build
	${MAKE} up

.PHONY: fclean
fclean: down
	docker system prune -f -a --volumes
	# Check if 'pg-data' exists
	@if docker volume ls | grep -q 'pg-data'; then \
		docker volume rm pg-data; \
	fi
	@if docker volume ls | grep -q 'elk-data'; then \
		docker volume rm elk-data; \
	fi

.PHONY: re
re: fclean
	${MAKE} fclean
	${MAKE} all
