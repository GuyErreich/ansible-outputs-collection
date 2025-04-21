VENV = .venv

export activate = . $(VENV)/bin/activate

.PHONY: init install test_default_with_clean_msg lint clean

init:
	@echo "Updating apt..."
	sudo apt update

	@echo "Installing pipx..."
	sudo apt install -y pipx
	pipx ensurepath

	@echo "Installing ansible..."
	pipx install --include-deps ansible

	@echo "Installing ansible-lint..."
	pipx install ansible-lint

venv:
	@echo "Creating virtual environment..."
	python3 -m venv $(VENV)
	
activate:
	@echo "Run this to activate your environment:"
	@echo "source $(VENV)/bin/activate"

install: venv
	$(activate) && pip install -U pip
	$(activate) && pip install -r requirements.txt

sanity:
	ansible-test sanity --docker --color yes

unit:
	ansible-test units --docker --color yes --requirements --coverage

lint:
	ansible-lint .

clean:
	rm -rf $(VENV) __pycache__ .pytest_cache