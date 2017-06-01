# Lean auto-deploy static site CloudFormation template

First off I'd like to thank the following two GitHub users, [MMusket](https://github.com/mmusket/) and [Alestic](https://github.com/alestic/), for providing solid code and materials.

I've adapted, combined and rewritten parts of their code to suit my needs for a minimal stack on AWS and for learning purposes.

## What is not automated?

IIt's on purpose much more simple setup than what is featured on Alesco's github. It doesn't automate setup of;

- CloudFront CDN,
- Route53 DNS,
- S3 bucket creation for logs and CloudFront,
- SNS Notifications, and a
- CodeCommit repo.

I provide a guide on how to setup Route53 DNS, the CodeCommit repo and the minimal CloudFormation stack to help understand how it all fits together.

## To get started

You can use the **cf_stack.yml** template to import in CloudFormation and subsequently run it to create AWS resources that will help automate your static site deployment to AWS hosted on S3.

The python file, **generate_static_site.py**, will generate a static site from your hugo source code and then minify it using GZIP before deploying it to your S3 website bucket.

Check out my written guide on [blog.FXAugury.com](http://blog.fxaugury.com/) to understand how it all works together.