.PHONY: validate install dry-run

validate:
	./scripts/validate.sh

install:
	./scripts/install.sh

dry-run:
	./scripts/install.sh --dry-run
