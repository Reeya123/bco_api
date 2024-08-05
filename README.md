![biocompute](https://github.com/user-attachments/assets/785e87f2-66a5-4a17-821b-c52bdf3c56e6)

# BioCompute: A Platform for Bioinformatics Analysis Workflow
## Introduction
BioCompute is a platform designed to facilitate the documentation and communication of bioinformatics analysis workflows. Following the IEEE 2791-2020 standard, BioCompute aims to ease communication burdens between research centers, organizations, and industries by providing a standardized, human- and machine-readable format for BioCompute Objects (BCOs).

## Key Features
- **Standardized Documentation**: Adopts the IEEE 2791-2020 standard for bioinformatics analyses.
- **User-Friendly Interface**: Build BioCompute Objects through an intuitive web portal.
- **Extensible**: Supports integration with various bioinformatics tools and databases.
- **Community-Driven**: Open-source and welcoming contributions from the community.

# BCO DB
The BioCompute Database is designed to be deployable in a variety of environments. If configured properly it should work with the [BioCompute Portal](https://biocomputeobject.org/) reguardelss of the deployment. 

The BCO API repository contains a top-level folder “admin_only” which contains service definitions for gunicorn and django, an example database, and a prepopultated `.secrets` file (called `local_deployment.secrets`). 

The service definitions are for deployment on a server exposed to the internet. A local deployment will not need to use those files. Below are links to instructions for deployment in different environments. 

## BCODB Deployment

- [Local deployment](docs/deployment/localDeployment.md) 
    - For develpment or internal use only
- [Production deployment](docs/deployment/productionDeployment.md)
    - For deployment that is exposed to the internet
- [Docker deployment](docs/deployment/dockerDeployment.md)
    - WIP: comming soon

## BCODB Development and troubleshooting
- [FAQ and trouble shooting](docs/faq.md)
- [`.secretes` configuration](docs/config.md)
- [Testing](docs/testing.md)
