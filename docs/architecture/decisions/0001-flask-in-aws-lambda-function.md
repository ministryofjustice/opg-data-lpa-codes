# 1. Flask in AWS Lambda Function

Date: 2020-04-29

## Status

Accepted

## Context

For this project, we would like to package up the API endpoints and logic into a small Flask app in a single lambda function.

We found whilst working on the Documents integration that managing multiple lambda functions quickly became quite hard work, 
especially as in that project there was a lot of shared code about the place. In hindsight, we should have refactored the 
shared code into separate lambda functions, but we never got to it due to time constraints. Also this would just give us 
more lambda functions to maintain. 

#### Why Flask (or any other WSGI app) in a Lambda is a good idea

* We can re-use most of the infra setup from the last project so we can get started fast
* Easy to run and develop locally, just run like a normal Flask app
* Easy to test as it's a normal Flask app
* Is it an anti-pattern? AWS have a library called Chalice which does a very similar thing to how we propose to use Flask
(but with more deployment stuff in that we don't need), so if AWS have an official package that does it, can it be an 
anti-pattern? 


#### Why Flask (or any other WSGI app) in a Lambda is a bad idea
* A whole app in a FaaS seems like an anti-pattern
* Potentially longer cold-start as it has to initialise the whole app not just a single function

## Decision

* Single lambda function containing small Flask app that provides all endpoints

## Consequences

* API may be slow to respond due to Flask app start-up time
    * We will be implementing some metrics to time this to see if it is a concern
* If we are wrong and want to move to an ECS container the code needs very little rework, but the infra rework is large
* If we are wrong and want to move to separate lambda functions the code needs some rework but the infra will be pretty 
much the same
 


