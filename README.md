# Thanks goes out to MMusket and Alesco

Thanks a lot to the following two GitHub users, [MMusket](https://github.com/mmusket/) and [Alestic](https://github.com/alestic/), for providing solid code and materials.

## Why i adapted their code?

Code you see here has been adapted, combined, and rewritten in order for me to better understand CloudFormation and automation with CodePipeline.

It's on purpose much more simple setup that what is featured on Alesco's github. It doesn't automate setup of; CloudFront CDN, some S3 bucket creation, SNS Notifications, and a CodeCommit repo.

The goal is understanding how all of this works by providing a step by step [guide](http://blog.fxaugury.com/) so you can reproduce it yourself.

I hope this guide helps out in some way.

## To get started

You can use the **cf_stack.yml** template to import in CloudFormation and subsequently run it to create AWS resources that will help automate your static site deployment to AWS hosted on S3.

The python file, **generate_static_site.py**, will generate a static site from your hugo source code and then minify it using GZIP before deploying it to your S3 website bucket.

## Written guide & tuturial

Check out my written guide on [blog.FXAugury.com](http://blog.fxaugury.com/) to understand how it all works together.