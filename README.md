# Lean auto-deploy static site CloudFormation template

_First off I'd like to thank the following two GitHub users, [MMusket](https://github.com/mmusket/) and [Alestic](https://github.com/alestic/), for providing their knowledge and resources for everyone to use._

I've adapted, combined and rewritten parts of their code to suit my needs for a minimal stack on AWS and for learning purposes. If you're just looking to get the full automated stack, check out [Alestic](https://github.com/alestic/)

## To get started

Check out my written guide on [blog.FXAugury.com](http://blog.fxaugury.com/post/automated-static-site-with-codepipeline-using-cloudformation-on-aws/) to understand how it all works together.

You can use the **cf_stack.yml** to create an AWS CodePipeline process that will automate the generation and deployment of a Hugo static site.

The python file, **generate_static_site.py**, will generate a static site from your Hugo source code and then minify it using GZIP before deploying it to your S3 website bucket.

You will need the hugo binary, see <https://github.com/spf13/hugo/releases> , zip the binary 'hugo' together with generate_static_site.py and upload this to an S3 bucket. Note the bucket and key (path in the bucket) to enter these parameters in the CloudFormation template.

## Costs

The following is a cost overview of running this static site on AWS:

|   Service|  Item|   Cost|   Subtotal|
|---|---|---|---|
|   **S3**|   1 GB storage|    $0.03|   $0.03|
|   |   10,0000 put/list requests|    $0.50|   $0.53|
|   |   10,0000 Get and Other Requests |    $0.04|   $0.57|
|   |   (Optional) depending on where you want to host your website and IF CodePipeline is available in that region. Inter region bucket transfers of 1GB/month|    $0.02|   $0.59|
|   **Route53**|  Hosted zone |   $0.50|   $1.09|
|   |  Standard queries: 1 million / month |   $0.40|   $1.49|
|   **CodePipeLine**|  1 Free pipeline per month |   $0.00|   $1.49|
|   **CodeCommit**|   First 5 users free with 50GB storage and 10,000 git requests/month|   $0.00|   $1.49|
|   **Lambda**|   Memory: 256Mb you get 1,600,000 seconds of compute time for free|  $0.00|    $1.49|
|   **Free tier**|  Discount|   -$0.05|   $1.44|
|   |   |   |   **$1.44**|

Compare this to running your blog on **Wordpress** (no custom domain costs included):

|   Service|  Monetize|   Cost|
|---|---|---|
| **Static site on AWS**| Yes| $1.49|
| **Wordpress Free** (No custom domain)| No| $0.00|
| **Wordpress Personal**| No| $2.99|
| **Wordpress Premium**| Yes| $8.25|

## Sources

Free tier explained:
- **[CodePipeline](https://aws.amazon.com/codepipeline/pricing/)**
    - Free tier offers 1 pipeline for free, does not expire after 12 months!
- **[CodeCommit](https://aws.amazon.com/codecommit/pricing/)**
    - Offer is valid regardless of Free Tier.
- **[AWS Lambda](https://aws.amazon.com/lambda/pricing/)**
    - Every run takes about 5 seconds, divide 1.6 million seconds by 5 = 320,000 runs per month(!)
    - Free tier does not expire after 12 months!

To check your current AWS infrastructure cost situation or calculate this example, go to the [AWS Calculator](https://calculator.s3.amazonaws.com/).

For an overview of Free tier participating services, see [Free tier](https://aws.amazon.com/free/) at Amazon.

Please see the pricing section on [Wordpress](https://wordpress.com/pricing/) for more details.