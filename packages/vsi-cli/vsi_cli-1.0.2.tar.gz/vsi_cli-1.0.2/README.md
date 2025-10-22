# vsi-cli 1.0.2

a vsi cli wrapper built on top of aws cli to simply aws operations based on daily usage.
## Installation

```bash
pip install vsi-cli==1.0.2
```
*reqs: latest aws cli, aws ssm plugin

## Usage
non-stable, wip.
supported commands:
    - set up sso profile
    - list configured sso profiles
    - tunnel to bastion
    - port forward to resources through bastion
    - install latest aws cli