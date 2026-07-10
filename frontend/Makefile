ROOT := ..
SERVICE := frontend

.PHONY: run run-prod test prod restart stop

run:
	npm install
	npm run dev

run-prod:
	npm install
	npm run build
	npm run preview

test:
	npm run build

prod:
	$(MAKE) -C $(ROOT) prod SERVICE=$(SERVICE)

restart:
	$(MAKE) -C $(ROOT) restart SERVICE=$(SERVICE)

stop:
	$(MAKE) -C $(ROOT) stop SERVICE=$(SERVICE)
