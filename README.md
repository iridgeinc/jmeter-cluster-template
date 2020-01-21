# JMeter Cluster
By using this repository, you can deploy jmeter cluster(a client instance and some server instances) in your aws account. **This repository is featured on the iRidge Developer Blog!** [here!](https://iridge-tech.hatenablog.com/entry/<記事入れたい>)

## Usage
### Preparation
* First, install dependent packages.

```
$ pip install pipenv
$ pipenv install
$ pipenv shell
```

* Second, copy variables yaml file.

```
$ cp variables.yaml.sample variables.yaml
```

* Thrid, set values of variables. The mean of each variable is follow;

|variable|description|
|------|----|
| jmeter_region| aws region in which cluster is deployed |
| jmeter_vpc| vpc id in which cluster is deployed |
| jmeter_subnet| subnet in which cluster is deployed|
| jmeter_allowed_ip| souce ip cidr to be allowed to ssh into instances of cluster|
| jmeter_ami_id| the id of ami for cluster (recommendation: amazon linux 2 ami, restriction: redhat type distribution)|
| jmeter_client_instance_type| instance type for client|
| jmeter_server_instance_type| instance type for server|
| jmeter_key_pair| key pair name of instances of cluster|
| jmeter_servers_count| the count of servers|
| jmeter_install_version| jmeter version to be installed|
| jmeter_heap_initial_size| initial heap memory size (it will be given to `Xms`)|
| jmeter_heap_max_size| max heap memory size (it will be given to `Xmx`)|
| jmeter_max_meta_space_size| max meta space size (it will be given to `XX:MaxMetaspaceSize`)|
| jmeter_max_open_file| max numbers of files to be opened (it will be given to command `ulimit -n`)|

* Forth, set your aws credential. (if needed, aws profile too by exporting env var `AWS_PROFILE`)

### Deploy cluster
* deploy cluster by only executing this command!

```
$ sceptre --var-file ./variables.yaml launch cluster
```

### Destroy cluster
* destroy cluster by only executing this command...

```
$ sceptre --var-file ./variables.yaml delete cluster
```

### Tips
Each of JMeter servers has local variables in the following;

|variable|description|
|------|----|
| server_number| the number of each JMeter server |
| server_count| the total count of JMeter servers |

You can use these variables in your test scenarios by describing as `${__P(<variable name>)}`.