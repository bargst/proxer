env:
	pipenv --three
	pipenv install
	git submodule update --init
	rm -f .env
	echo 'PYTHONPATH=$$PYTHONPATH'$$(ls -d lib/* | awk -v pwd=$$(pwd) '{printf(":"pwd"/"$$1)}') >> .env
devenv: env
	pipenv install --dev
test:
	pipenv run py.test tests/
