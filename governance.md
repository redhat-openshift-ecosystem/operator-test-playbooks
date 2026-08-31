# Project Governance

# Project Overview

The complete overview of this project is located in the README.md file in this
repository.

# Roles and Responsibilities

## Maintainers

Maintainers drive development and review contributions. They are responsible
for decision-making and steering the development of this project. Work
delivered by the maintainers should have a JIRA ticket before it is made.
Larger changes should be discussed with the maintainer team in the form of
a design doc that is then jointly refined in order to reach required
functionality in a way that works well with the rest of the codebase and is
maintainable.

## Contributors

Contributors are community members. They help develop this project. All changes
which contributors work on should be signed off by the maintainers before the
work starts. This process can be started by opening an Issue in this
repository.

## Common responsibilities

Both maintainers and contributors must adhere to the following standards:

### Commit Standards

[Conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) are in
use in this repository, please use them. Commit messages should be brief,
descriptive, and contain a ticket reference (JIRA or Issue number).
[Commit signoffs](
https://git-scm.com/docs/git-commit#Documentation/git-commit.txt--s
) are required and must not be automated, but must be added by a human.
If your commit was created/assisted by an AI tool, you **must** disclose it in
the commit using the `Assisted-by:` commit message trailer. 

### Pull Request Requirements

* Pull requests should be isolated, as atomic as possible, and easily
  reviewable.
* Pull requests should contain relevant unit and integration tests where
  applicable (almost always).
* Code should be sufficiently documented and markdown documentation should be
  updated if made outdated in this merge request
* Every pull request needs to pass the repository CI before it is accepted. 
  Ideally, the CI should pass before reviewers are tagged to save their time.
* At least one maintainer must review the code before it is merged. In most
  cases it should be two reviewers, one reviewer is sufficient only for
  trivial, straightforward changes. Two reviewers are required for external
  contributions.

### AI Policy

AI-assisted contributions are welcome and you are encouraged to utilize any
tool you need to submit a quality contribution. We, however, request that you
adhere to a couple of rules when utilizing AI and LLMs in particular:

* Any AI usage in the process of creating the code submitted **must** be
  disclosed (see [Commit Standards](#commit-standards)).
* The human submitting the changes **must** first review any AI output, fully
  understand the code submitted and be able to explain the choices made during
  the implementation.
* If the effort put into creating the submitted code is less than the effort
  required to give a thorough review, such a contribution is not valuable
  enough to spend precious reviewer time on. This is especially true for
  external contributions.
* Please **do not** use purely auto-generated AI text in discussions, JIRA
  and design docs; however, you are welcome to use AI for spellchecking or 
  refining your text as long as the output is actively guided
  and verified by you.
* The intent here is to interact with the maintainers in a meaningful way
  that engages both sides equally.

# Decision Making Process

## Development

Technical decisions on implementation are made during the PR process between
the contributor and reviewers. If reviewers disagree, they should resolve it
amongst themselves before asking the contributor for changes. Bigger decisions
(architecture, new dependencies, API changes, and deprecations) should go
through a design document that the team refines together. The final call on
technical decisions rests with the relevant SMEs.

# Security

If you discover a vulnerability in this repository, please contact
the maintainers privately using the [provided contact e-mail](
#contact-information
).

# Communication

Everyone is encouraged to engage in a conversation about this project in the
relevant Issues, Discussions, and contributions. The communication must always
be respectful from all involved parties. Do not let AI-agents freely engage in
communication as the volume of information cannot easily be handled
by the maintainers.

# Contact Information

Point of contact: exd-guild-isv@redhat.com

# Acknowledgements

This governance was created as a template based on a text approved by the
maintainers. AI policy was created based on [policies](
https://github.com/melissawm/open-source-ai-contribution-policies
) in several well-established open source projects and as such hopefully
reflects the current state of the industry.
