# Cotor #
Closed issues for bugs and enhancements are a great way to learn a new codebase. This repo hosts code for a webapp where users can login with their GitHub accounts, search for a public repo and closed issue or pull request, and get an AI-generated summary of code changes that occured. Video below illustrates functioning of the webapp.

https://github.com/user-attachments/assets/8f2cc9c0-15eb-4303-b160-501cb150ce96

# Setup #
The webapp is powered by a React front-end (with Material UI components), Python FastAPI backend, GitHub REST API, Supabase as the database, and OpenAI as the large language model to generate code summaries. All relevant code to setup is under folders **api** and **webapp**. Code under prototyping can be ignored. 
1. Host the React app on a service such as [AWS Amplify](https://aws.amazon.com/amplify/)
2. The FastAPI app was hosted on AWS Elastic Beanstalk. Refer to this helpful [article](https://testdriven.io/blog/fastapi-elastic-beanstalk/) on how to set this up
3. Setup an **Issues** table in Supabase. Refer to /researchissue route under API for schema details
4. Setup your OpenAI API key
5. Setup authentication using Supabase with GitHub as provider 
