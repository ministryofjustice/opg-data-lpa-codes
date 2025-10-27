# Terraform in Opg-Data-LPA-Codes

The purpose of this readme is to clarify what the terraform code is doing and how it interacts
with the CI pipeline as well as giving some common commands and tasks anyone can perform with the
right permissions

### Workspace based environments

This repository uses workspaces. Workspaces allow you modify a terraform state file through applying
and destroying configuration independently of other workspaces. For example if I was in workspace 'X'
and locked the state file by killing off an apply half way through then although no one could work on
workspace 'X', workspace 'Y' would be completely unaffected.

We use this principal so that in our dev environments we create workspaces based on our branch name.
As such we can have multiple copies of an environment in the same AWS account.

The workspaces are controlled by the variable TF_WORKSPACE. If you wish manually run a plan or apply against
one of your branch workspaces for development purposes then you must be in the
```terraform/environment``` folder.
You would then run the following replacing myworkspace with your workspace name:
```export TF_WORKSPACE=myworkspace```.
Next run your terraform command (aws vault profile could be different depending how you set it up):
```aws-vault exec identity -- terraform plan```.

### OpenApi orientated rest API (and tests)

The API gateway is generated from an OpenApi spec. The OpenApi spec controls
the auth method, validation and the versioning
by means of using stage variables to point
to separate lambdas.

### API Gateway deployment

The way the amazon API Gateway product works is that we have a rest api that has integrations to end points.
In our case this is a lambda running a flask application. To access the gateway a stage needs
to be deployed and a DNS entry can then point to a particular stage.

### Release a new version

Stages point to the relevant version of the lambda for the stage using stage variables. These are defined in
the OpenApi spec and assigned by the terraform code.

It is not practical using this method, to support long term, multiple versions as deployments are per
Rest API. As such the deployment and old stage crystallised in time and cannot be modified once new version is released.
The lambdas are completely separate so a bug fix on the lambda side could be done on a previous version.

### Lambdas

Lambdas are controlled through modules as per above.
