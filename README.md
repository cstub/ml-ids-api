# ML-IDS API

## General

This project implements the REST API serving the network attack detector developed in the [ML-IDS project](https://github.com/cstub/ml-ids).    
The ML-IDS project is an implementation of a machine learning based [intrusion detection system](https://en.wikipedia.org/wiki/Intrusion_detection_system), providing a classifier capable of detecting network attacks. The classifier analyses prerecorded network flows and categorises a network flow as either benign or malicious. A network flow in this context is defined as an aggregation of interrelated network packets between two hosts.    
The classifier is deployed using the [Amazon SageMaker platform](https://aws.amazon.com/sagemaker/) and is not publicly accessible.    

This REST API acts as a public interface to the classifier by providing a REST API that can be used to send prediction requests. Furthermore, upon detection of network attacks, an attack notification is published to an [AWS SNS topic](https://aws.amazon.com/sns/) and subsequently to an [AWS SQS queue](https://aws.amazon.com/sqs/). Clients can subscribe to this queue to be notified of network attacks in real-time.

## Prediction API

The REST API provides a `/api/predictions` endpoint that accepts prediction requests containing network flows in [Pandas split JSON format](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_json.html). Each submitted network flow is analyzed and classified via the [ML-IDS estimator](https://github.com/cstub/ml-ids). The API responds with a binary prediction of either `[0 - Benign]` or `[1 - Attack]` per network flow.     
To use the API you can either use a standard HTTP client or use the REST client provided by the [ML-IDS API Client project](https://github.com/cstub/ml-ids-api-client).

The [OpenAPI](https://swagger.io/specification/) specification for the Prediction API is provided in the `api-spec.yaml` file.

## Attack Notifications

Each prediction, combined with the corresponding prediction request, is published to an AWS SNS topic. Predictions of malicious network flows are filtered by this topic and published to an AWS SQS queue to be received by API clients subsequently.    
To receive attack notifications, a client must subscribe to the corresponding AWS SQS queue. This can either be done by implementing a custom AWS SQS client or by using the client provided by the [ML-IDS API Client project](https://github.com/cstub/ml-ids-api-client).

## Build

The REST API is implemented using [Flask](http://flask.palletsprojects.com/en/1.1.x/) and packaged via [docker](https://www.docker.com/), allowing for deployments on any environment that supports docker containers.

To build and package the application ensure that docker is installed and run the following command.

```
docker build -t ml-ids-api:1.0 -f container/Dockerfile .
```

To run the container, the following configuration parameters must be passed via environment variables:

* AWS_REGION: AWS region in which the SageMaker classifier and SNS topic are registered.
* AWS_SAGEMAKER_HOST: Host of the SageMaker API providing the classifier (omitting the protocol).
* AWS_SAGEMAKER_ENDPOINT: Endpoint of the SageMaker API providing the classifier.
* AWS_SNS_PREDICTIONS_TOPIC: ARN of the SNS prediction topic.
* AWS_ACCESS_KEY: Access key of an AWS user permitted to access the SageMaker API and the SNS topic.
* AWS_SECRET_KEY: Secret key of an AWS user permitted to access the SageMaker API and the SNS topic.

```
docker run --rm -it -p 5000:5000 \
  -e AWS_REGION={REGION} \
  -e AWS_ACCESS_KEY={SECRET_KEY} \
  -e AWS_SECRET_KEY={ACCESS_KEY} \
  -e AWS_SAGEMAKER_HOST={SAGEMAKER_HOST} \
  -e AWS_SAGEMAKER_ENDPOINT={SAGEMAKER_ENDPOINT} \
  -e AWS_SNS_PREDICTIONS_TOPIC={TOPIC_ARN} \
  ml-ids-api:1.0
```

## Deployment on AWS ECS

This project contains a task definition to deploy the docker container to a predefined [AWS ECS](https://aws.amazon.com/ecs/) cluster. If you want to use the task definition for your own deployments the `task-definition.json` has to be adapted accordingly.
