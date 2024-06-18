COMPOSE_FILE 	:= ./docker-compose.yml

.PHONY: all
all:
	${MAKE} build
	${MAKE} up

.PHONY: build
build:
	@docker compose -f $(COMPOSE_FILE) build

.PHONY: up
up:
	@docker compose -f $(COMPOSE_FILE) up -d

.PHONY: down
down:
	@docker compose -f $(COMPOSE_FILE) down

.PHONY: ps
ps:
	@docker compose -f $(COMPOSE_FILE) ps

.PHONY: logs
logs:
	@docker compose -f $(COMPOSE_FILE) logs -f -t -n 100

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

.PHONY: re
re: fclean
	${MAKE} fclean
	${MAKE} all
