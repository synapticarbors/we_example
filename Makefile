all: setup

setup:
	cd mcsampler && python setup.py build_ext -i

bruteforce-run:
	cd bruteforce && python simulate.py -N 10000000 -s 25 --dsize 400000

bruteforce-analyze:
	cd bruteforce && python analyze.py

bruteforce: bruteforce-run bruteforce-analyze

we-run: check-env
	cd we && rm *.h5
	cd we && ./run.sh &

we-analyze: check-env
	cd we && $${WEST_ROOT}/bin/w_pdist --serial --bins '[numpy.arange(0.2, 2.8, 0.02)]'

we: we-run we-analyze

visualize:
	cd visualization && python gen_animation.py

check-env:
	@if [ -z "$${WEST_ROOT}" ]; then echo "The env variable WEST_ROOT must be specified"  && exit 1; fi

.PHONY: setup bruteforce-run bruteforce-analyze we-run we-analyze check-env visualize bruteforce we
