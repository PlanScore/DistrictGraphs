# Just one Lambda codebase is created, with different entry points and environments.
dgraphs-lambda.zip: gdal-geos-python.tar.gz
	mkdir -p dgraphs-lambda
	pip install -t dgraphs-lambda .
	tar -C dgraphs-lambda -xzf gdal-geos-python.tar.gz
	cp lambda.py dgraphs-lambda/lambda.py
	cd dgraphs-lambda && zip -rq ../dgraphs-lambda.zip .

clean:
	rm -rf dgraphs-lambda dgraphs-lambda.zip

local-test: dgraphs-lambda.zip
	./setup-localstack.py dgraphs-lambda.zip
