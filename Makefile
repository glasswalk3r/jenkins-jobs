VIRTUALENV:=$(shell basename $$PWD)

config:
	pyenv virtualenv $(VIRTUALENV)
	pyenv local $(VIRTUALENV)
	pip install --upgrade pip wheel
	pip install -r requirements-dev.txt
debug:
	export JOBS_REPORTER_DATA=$(DATA_SAMPLE) && python -m pdb jobs_reporter.py --user foobar --token foobar --jenkins foobar
run:
	python jobs_reporter.py --user $(USER) --token $(TOKEN) --jenkins $(SERVER)
local:
	export JOBS_REPORTER_DATA=$(DATA_SAMPLE) && python jobs_reporter.py --user foobar --token foobar --jenkins foobar
test:
	flake8

