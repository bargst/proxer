env:
	pipenv --three
	pipenv install
	git submodule update --init
	rm -f .env
	for lib in lib/*; do echo 'PYTHONPATH=$$PYTHONPATH':$$(pwd)/$$lib >> .env ;  done
devenv: env
	pipenv install --dev
test:
	pipenv run py.test tests/
