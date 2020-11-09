# Purpose
This document describes about the Upstream Operator Test Playbooks CI Pipeline and how it works.

# Introduction
The Upstream Operator Test Playbooks CI Pipeline exists to automatically run tests against pull requests in the [redhat-operator-ecosystem/operator-test-playbooks GitHub repository](https://github.com/redhat-operator-ecosystem/operator-test-playbooks).

# Configuration
A webhook is configured so that the repository sends events to the github2fedmsg web application.
Any activity (ex: adding comments) in the repository is therefore sent to github2fedmsg, which then rebroadcasts on the Fedora Messaging bus (fedmsg).
For more information on github2fedmsg and Fedora Messaging see [github2fedmsg](https://github.com/fedora-infra/github2fedmsg)

# Usage
* The test-operator-test-playbooks jenkins job runs on the CVP CI Jenkins server.

* The job is triggered by a message on the Fedora Messaging bus:

  * Indicates that a pull request was opened, re-opened, or synchronized (“synchronized” meaning that code changes were pushed to an already-opened pull request)

    Ex: [PR-opened](https://apps.fedoraproject.org/datagrepper/raw?topic=org.fedoraproject.prod.github.pull_request.opened)

  * Indicates a comment was added that contains the text `/retest` or `/test CVP`

    Ex: [PR-comment-added](https://apps.fedoraproject.org/datagrepper/raw?topic=org.fedoraproject.prod.github.issue.comment&delta=3600)

* The openshift project name for `test-operator-test-playbooks` is `cvp-ci-operatortestplaybooks`

* The test-operator-test-playbooks job parses the fedmsg to determine what files have changed and what repository and branch needs to be tested.

* If the data can be successfully parsed, test-operator-test-playbooks uses `CVP bot account` on GitHub to create a check status, `CVP/pr-sanity-test`, for the pull request, this check can also be seen on the PR among other tests.

* Note: If the only file that has changed is README.md, test-operator-test-playbooks will then exit successfully. No further tests are required since no ansible playbooks have changed.

* The test-operator-test-playbooks jenkins job configures it’s own Product/Team Jenkins server to run the testing pipelines.

* When this is complete the test-operator-test-playbooks job currently triggers three test pipelines on it’s Team Jenkins server:

  * cvp-redhat-operator-bundle-image-validation-test
  * cvp-redhat-operator-metadata-validation-test
  * cvp-isv-operator-metadata-validation-test

* These are the same pipelines that runs in production. The sample operators used for testing in these pipelines are the same used in CVP-CI setup tests.

* The pipelines are running in parallel, although they are started one minute apart from each other. 

* When a testing pipeline is started, the test-operator-test-playbooks job adds a new check status to the pull request on GitHub indicating the name of the test pipeline and it sets the status to “pending”, so that end-users are informed that a test is in progress.

* When a testing pipeline completes, the check status is updated with either `success` or `failure`.

* Each pipeline’s artifacts are uploaded to Amazon S3, the same artifacts as are uploaded in production, and can be viewed externally to determine which stages in the testing pipeline failed.

* The artifacts also contain a generalized link at the bottom of each test logs, so that the CVP team can access all the artifacts for the test pipeline that are not available externally.