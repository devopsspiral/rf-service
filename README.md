# RF-service

RobotFramework service for running tests/healthchecks from kubernetes cluster and publish results there. Currently implemented as Kubernetes CronJob that executes tests at given schedule and publish it in Caddy server. Next steps include making the service RESTful.

## Quick start

```
git clone https://github.com/devopsspiral/rf-service.git
cd rf-service
helm install rf-service ~/git/rf-service/chart/rf-service/

#Caddy is exposed as service type LoadBalancer by default, but you can use ingress
kubectl get svc rf-service-caddy

#open browser with url http://<external-ip>/ or http://<worker ip>:<node port>/
```

You should see Caddy browsing empty dir. Every minute there should be test execution and results will be published in Caddy.
Executed tests are taken from [KubeLibrary](https://github.com/devopsspiral/KubeLibrary/tree/master/testcases) and will most 
probably fail on your cluster. If you want to see them pass you need k3s/k3d and example grafana service as described in [KubeLibrary README](https://github.com/devopsspiral/KubeLibrary).

## Usage

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

At this point rf-service is utilized as CronJob and it needs .json file to configure its behaviour. It is passed as only argument to rf-service executable (see [this line](https://github.com/devopsspiral/rf-service/blob/f07716d068b9e7aa739f0c6c024e8b62c78d23c0/chart/rf-service/templates/test-job.yaml#L16))

The example content of the file is as below:
```
  {
    "fetcher": {
        "type": "ZipFetcher",
        "url": "https://github.com/devopsspiral/KubeLibrary/archive/incluster.zip"
    },
    "publisher": {
        "type": "CaddyPublisher",
        "url": "http://rf-service-caddy/uploads"
    }
  }
```

It configures rf-service to get testcases from given url (branch in github) and publish results in Caddy server using k8s service DN rf-service-caddy. You can create your own fetchers and publishers.

In helm chart file content can be defined using .Values.config and it is kept as ConfigMap on cluster.

### Helm chart

Below you can find table with parameters that are most important.

| Chart parameter   | Default | Comment |
| ------------- | ------------- | ------------- |
| image.repository | mwcislo/rf-service-k8s | should point to your custom test image
| schedule | \*/1 \* \* \* \* | cron=like schedule for test execution
| storageSize | 1Gi | volume size used for keeping reports in Caddy
| config | (as described in [rf-service configuration](#rf-service-configuration)) | .json file with configuration
| bindToClusterRole | cluster-admin |  defines which cluster role to use
| caddy.service.type | LoadBalancer | defines way of exposing rf-service
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

# testing
python -m unittest
```
