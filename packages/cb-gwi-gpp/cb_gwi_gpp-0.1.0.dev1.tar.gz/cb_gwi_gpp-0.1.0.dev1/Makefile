# Makefile for amarena

CB_GWI_GPP_DIR := ./cb_gwi_gpp

PYFILES :=  \
		   $(wildcard $(CB_GWI_GPP_DIR)/*.py) \
		   ./__version__.py \

BUILD_DIR := ./dist


# tools
E := @echo
PYCODESTYLE := pycodestyle
PYCODESTYLE_FLAGS := --show-source --show-pep8  #--ignore=E501,E228,E722

AUTOPEP8 := autopep8
AUTOPEP8_FLAGS := --in-place

FLAKE8 := flake8
FLAKE8_FLAGS := --show-source  --ignore=E501,E228,E722,W503

BANDIT := bandit
BANDIT_FLAGS := --format custom --msg-template \
    "{abspath}:{line}: {test_id}[bandit]: {severity}: {msg}"


HATCH := hatch


check: pycodestyle flake8 bandit


pycodestyle: $(patsubst %.py,%.pycodestyle,$(PYFILES))

%.pycodestyle:
	$(E) $(PYCODESTYLE) checking $*.py
	@$(AUTOPEP8) $(AUTOPEP8_FLAGS) $*.py
	@$(PYCODESTYLE) $(PYCODESTYLE_FLAGS) $*.py


flake8: $(patsubst %.py,%.flake8,$(PYFILES))

%.flake8:
	$(E) flake8 checking $*.py
	@$(FLAKE8) $(FLAKE8_FLAGS) $*.py


bandit: $(patsubst %.py,%.bandit,$(PYFILES))

%.bandit:
	$(E) bandit checking $*.py
	@$(BANDIT) $(BANDIT_FLAGS) $*.py


# .PHONY: test
# test:
# 	@$(E) "running tests..."
# # 	pytest -v -rP test/test_0.py::Test_Nucleo_G474RE
# 	coverage run    -m pytest -v -rP ./test/test_0_cb_bit.py
# 	coverage run -a -m pytest -v -rP ./test/test_cb_jtag_iface.py
# 	coverage run -a -m pytest -v -rP ./test/test_0_nucleo_G474RE.py

# 	# 	coverage run -m pytest -v -rP test/test_0_board_LPC1837.py

# cov_report: test
# 	coverage report -m
# 	coverage html

.PHONY: all
all:
	$(E) "building all..."
	$(HATCH) build


build:
	$(HATCH) build


install: build
	@pip install dist/cb_jtag*.whl --force-reinstall


deploy: build
	$(E) Uploading package to PyPI...
	twine upload dist/*


clean:
	@$(E) "cleaning up..."
	@rm -rf ./__pycache__
	@rm -rf ./*/__pycache__
	@rm -rf ./htmlcov
	@rm -f ./.coverage
	@rm -rf ./.pytest_cache
	@rm -rf ./*.log*


mr_proper: clean
	@$(E) "doing a mr_proper..."
	@rm -rf ./$(BUILD_DIR)