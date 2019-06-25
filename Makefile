live-lambda: dgraphs-lambda.zip
	env AWS=amazonaws.com \
		parallel -j9 ./deploy.py dgraphs-lambda.zip \
		::: DistrictGraphs-upload_file DistrictGraphs-read_file

# Just one Lambda codebase is created, with different entry points and environments.
dgraphs-lambda.zip: gdal-geos-python.tar.gz
	mkdir -p dgraphs-lambda
	pip install -t dgraphs-lambda .
	tar -C dgraphs-lambda -xzf gdal-geos-python.tar.gz
	cp lambda.py dgraphs-lambda/lambda.py
	cd dgraphs-lambda && zip -rq ../dgraphs-lambda.zip .

gdal-geos-python.tar.gz:
	curl https://planscore.s3.amazonaws.com/code/gdal-2.1.3-geos-3.6.1-python-3.6.1.tar.gz -o $@ -s

clean:
	rm -rf dgraphs-lambda dgraphs-lambda.zip

local-test: dgraphs-lambda.zip
	./setup-localstack.py dgraphs-lambda.zip
