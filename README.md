# RF-service

RF-service is a service for running tests. It can work in two modes: on-demand execution with [frontend](https://github.com/devopsspiral/rf-service-fe) and as Kubernetes CronJob that executes tests at given schedule and publish it in Caddy server. 

## Quick start

```
git clone https://github.com/devopsspiral/rf-service.git
cd rf-service
helm install rf-service ~/git/rf-service/chart/rf-service/

#By default rf-service-fe is exposed on http://rf-service.local
#If you running it on k3d/k3s you might need to add entries to you /etc/hosts
```

To run tests you need to first go to Configure tab and define fetcher (for getting test source) and publisher (to define where to put results). You can use internal caddy container as publisher target just use values from configuration file described in [rf-service configuration](#rf-service-configuration).

If executed as CronJob with default settings, every minute there should be test execution and results will be published in Results tab.
Executed tests are taken from [KubeLibrary](https://github.com/devopsspiral/KubeLibrary/tree/master/testcases) and will most 
probably fail on your cluster. If you want to see them pass you need k3s/k3d and example grafana service as described in [KubeLibrary README](https://github.com/devopsspiral/KubeLibrary).

## Usage

### 0.3.1 changes

*Helm chart doesn't support those changes yet.*

See [Testing with octopus](https://devopsspiral.com/articles/k8s/testing-with-octopus/).

#### CLI improvements

Since 0.3.1 rf-service can be configured using CLI parameters in a form of:

```
rf-service --LocalFetcher-src ~/test/source --LocalPublisher-dest ~/test/results
```

which is equivalent of:

```
{
    "fetcher": {
        "type": "LocalFetcher",
        "src": "~/test/source"
    },
    "publisher": {
        "type": "LocalPublisher",
        "dest": "~/test/results"
    }
}
```

Additionally CLI support following flags:

| CLI parameter | Comment           |
| ------------- | ----------------- |
| -i/--include  | include test tags |
| -e/--exclude  | exclude test tags |

#### Dependency resolution

In a path towards making rf-service generic enough to be executed as a base for different kinds of testcases, support for pip requirements was added. This way if fetcher collects directory containg *requirements.txt* file, it will install packages as with `pip install -r requirements.txt`. Just remember first spotted requirements.txt file will be used, so it is best to keep one in top level directory.

### Building own test image

rf-service image should contain only logic connected with running RobotFramework tests, to include external test libraries you should build your own image similar to dockerfile in `docker-k8s/Dockerfile`:

```
FROM mwcislo/rf-service

COPY docker-k8s/requirements.txt .

RUN pip install -r requirements.txt

CMD rf-service
```

By default helm chart is using this image for running tests

### rf-service configuration

If rf-service is utilized as CronJob it needs .json file to configure its behaviour. It is passed as only argument to rf-service executable (see [this line](https://github.com/devopsspiral/rf-service/blob/f07716d068b9e7aa739f0c6c024e8b62c78d23c0/chart/rf-service/templates/test-job.yaml#L17))

The example content of the file is as below:
```
  {
    "fetcher": {
        "type": "ZipFetcher",
        "url": "https://github.com/devopsspiral/KubeLibrary/archive/incluster.zip"
    },
    "publisher": {
        "type": "CaddyPublisher",
        "url": "http://rf-service:8090/uploads"
    }
  }
```

It configures rf-service to get testcases from given url (branch in github) and publish results in Caddy server using k8s service DN rf-service (providing you named release rf-service when executing helm install). You can create your own fetchers and publishers.

In helm chart, config file content can be defined using .Values.config and it is kept as ConfigMap on cluster.

When using Web UI (.Values.config is empty string) the same configuration can be done in Configure tab. You need to save both Publisher and Fetcher config separetly. To use internal Caddy container you need to pass http://localhost:8090/uploads - as all the containers are part of the same pod, all the ports are accessible on localhost.

### Helm chart

Below you can find table with parameters that are most important.

| Chart parameter   | Default | Comment |
| ------------- | ------------- | ------------- |
| image.repository | mwcislo/rf-service-k8s | should point to your custom test image
| schedule | \*/1 \* \* \* \* | cron=like schedule for test execution
| storageSize | 1Gi | volume size used for keeping reports in Caddy
| config | "" | .json file with configuration
| bindToClusterRole | cluster-admin |  defines which cluster role to use
| rfFE.service.type | ClusterIP | defines way of exposing rf-service-fe
| caddy.setup | ... | configures caddy, upload part shouldn't be changed

## Development

```
# clone repo
git clone https://github.com/devopsspiral/rf-service.git
cd rf-service

# create virtualenv
virtualenv .venv
. .venv/bin/activate
pip install --user -r requirements.txt
export PYTHONPATH=./src:${PYTHONPATH}
cd src
python -m rf_runner.api
# or
scripts/rf-service [config.json]
# or from docker
docker run -it --rm -p 5000:5000 mwcislo/rf-service:0.x.0
# API is on http://localhost:5000/api/


# testing
python -m unittest
```

## References

### Articles

[Robot Framework library for testing Kubernetes](https://devopsspiral.com/articles/k8s/robotframework-kubelibrary/)

[Testing on kubernetes - rf-service](https://devopsspiral.com/articles/k8s/robotframework-service/)

[Intro to Vue.js. Testing on kubernetes - rf-service frontend.](https://devopsspiral.com/articles/k8s/robotframework-service-fe/)

[Testing with octopus](https://devopsspiral.com/articles/k8s/testing-with-octopus/)

### Repositories

[KubeLibrary](https://github.com/devopsspiral/KubeLibrary)

[rf-service-fe](https://github.com/devopsspiral/rf-service-fe)
