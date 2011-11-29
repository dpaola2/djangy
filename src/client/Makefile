all: develop

develop: setup.py djangy/* find_git_repository/*
	python setup.py develop

upload: setup.py djangy/* find_git_repository/*
	python setup.py register sdist upload

clean:
	rm -rf dist
	rm -rf build
	rm -rf Djangy.egg-info
