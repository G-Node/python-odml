How to contribute to python-odml
================================

This document gives some information about how to contribute to the odML project.


Governance model
----------------

The project has a core team of **maintainers** who are long-term contributors and responsible for coordinating the project. There is also a set of one-time or short period **contributors**. We consider everyone a contributor who reports issues, opens pull requests, or takes part in issue discussions. Any such contribution is welcome. Maintainers have commit access to the repository and will review and merge pull requests. Becoming a maintainer is possible for everyone who wants to help maintaining and shaping the project and to take over more responsibility. Requests to become a maintainer need to be approved by the existing maintainers.

Any addition to the code happens via pull requests (there are only very few exceptions in which someone pushes directly to master, see below for more information). Thus, any contribution will be reviewed before it is merged. Bug fixes and other contributions to the API will undergo this pragmatic approach. Format or API changes, especially those that would lead to breaking changes, will be discussed via the issue tracker and video meetings and need to be agreed on by the maintainters. We aim at consensus decisions, but where this is not possible decisions are made by majority vote among the maintainers.


Contributing
------------

If you want to contribute to the project please first create a fork of the repository on GitHub.
When you are done with implementing a new feature or with fixing a bug, please send
us a pull request.

If you contribute to the project regularly, it would be very much appreciated if you
would stick to the following development workflow:

1. Select an *issue* from the issue tracker that you want to work on and assign the issue to your account.
   If the *issue* is about a relatively complex matter or requires larger API changes the description of the
   *issue* or its respective discussion should contain a brief concept about how the solution will look like.

2. During the implementation of the feature or bug-fix add your changes in small atomic commits.
   Commit messages should be short but expressive.
   The first line of the message should not exceed **50** characters and the 2nd line should be empty.
   If you want to add further text you can do so from the 3rd line on without limitations.
   If possible reference fixed issues in the commit message (e.g. "fixes #101").

3. When done with the implementation, compile and test the code.
   If your work includes a new function or class please write a small unit test for it.

4. Send us a pull request with your changes.
   The pull request message should explain the changes and reference the *issue* addressed by your code.
   Your pull request will be reviewed by one of our team members.
   Pull requests should never be merged by the author of the contribution, but by another team member.
   Merge conflicts or errors reported by travis should be resolved by the original author before the request is merged.


Google Summer of Code contributors
---------------------

Please see the corresponding [Google Summer of Code](GSoC.md) file if you are interested in contributing as part of the GSoC programme.


The issue tracker
-----------------

Please try to avoid duplicates of issues. If you encounter duplicated issues, please close all of them except
one, reference the closed issues in the one that is left open and add missing information from the closed issues
(if necessary) to the remaining issue.

Assign meaningful tags to newly crated issues and if possible assign them to milestones.


Reviewing pull requests
-----------------------

Every code (even small contributions from core developers) should be added to the project via pull requests.
Before reviewing a pull request it should pass all builds and tests on travis-ci.
Each pull request that passes all builds and tests should be reviewed by at least one of the core developers.
If a contribution is rather complex or leads to significant API changes, the respective pull request should be
reviewed by two other developers.
In such cases the first reviewer or the contributor should request a second review in a comment.


Testing
-------

* Unit test can be found in the test sub directory. Currently, the test coverage is a bit low but we are working on improving it.

* Provide a unit test for every class, method or function.

* Please make sure that all tests pass before merging/sending pull requests.


Style guide
-----------

Always keep your code PEP8 compliant.
