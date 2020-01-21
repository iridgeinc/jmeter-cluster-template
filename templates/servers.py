import yaml
from troposphere import Base64, GetAtt, Join, Output, Parameter, Ref, Template
from troposphere.ec2 import Instance, Tag


class JMeterServers:
    def __init__(self, sceptre_user_data):
        self.template = Template()
        self.sceptre_user_data = sceptre_user_data
        self.template.set_description("JMeter Servers")
        with open("variables.yaml") as file:
            self.variables = yaml.load(file, Loader=yaml.SafeLoader)

    def add_parameters(self):
        self.jmeter_ami_id = self.template.add_parameter(
            Parameter("JMeterAmiId", Description="jmeter_ami_id", Type="String",)
        )

        self.jmeter_security_group = self.template.add_parameter(
            Parameter(
                "JMeterSecurityGroup",
                Description="jmeter_security_group",
                Type="String",
            )
        )

        self.jmeter_subnet = self.template.add_parameter(
            Parameter("JMeterSubnet", Description="jmeter_subnet", Type="String",)
        )

        self.jmeter_server_instance_type = self.template.add_parameter(
            Parameter(
                "JMeterServerInstanceType",
                Description="jmeter_server_instance_type",
                Type="String",
            )
        )

        self.jmeter_key_pair = self.template.add_parameter(
            Parameter("JMeterKeyPair", Description="jmeter_key_pair", Type="String",)
        )

    def add_resources(self):
        jmeter_install_version = self.variables["jmeter_install_version"]
        jmeter_heap_initial_size = self.variables["jmeter_heap_initial_size"]
        jmeter_heap_max_size = self.variables["jmeter_heap_max_size"]
        jmeter_max_meta_space_size = self.variables["jmeter_max_meta_space_size"]
        jmeter_max_open_file = self.variables["jmeter_max_open_file"]

        instance_count = self.variables["jmeter_servers_count"]

        for i in range(0, instance_count):
            user_data = f"""#!/bin/sh
                yum install -y git wget java-1.8.0-openjdk java-1.8.0-openjdk-devel
                mkdir /home/ec2-user/jmeter && cd /home/ec2-user/jmeter
                wget -O ./jmeter.tar.gz \\
                https://archive.apache.org/dist/jmeter/binaries/apache-jmeter-{jmeter_install_version}.tgz
                tar xvfz jmeter.tar.gz --strip=1 && rm -f jmeter.tar.gz
                chown ec2-user:ec2-user -R .
                echo >> ./bin/user.properties
                echo server.rmi.ssl.disable=true >> ./bin/user.properties
                ulimit -n {jmeter_max_open_file}
                export HEAP=\\
                "-Xms{jmeter_heap_initial_size} \\
                -Xmx{jmeter_heap_max_size} \\
                -XX:MaxMetaspaceSize={jmeter_max_meta_space_size}"
                nohup ./bin/jmeter-server \\
                -Jserver_number={i+1} \\
                -Jserver_count={instance_count} &
                """

            self.template.add_resource(
                Instance(
                    f"JMeterServer{i+1}",
                    ImageId=Ref(self.jmeter_ami_id),
                    InstanceType=Ref(self.jmeter_server_instance_type),
                    KeyName=Ref(self.jmeter_key_pair),
                    SecurityGroupIds=[Ref(self.jmeter_security_group)],
                    SubnetId=Ref(self.jmeter_subnet),
                    Tags=[Tag(key="Name", value=f"jmeter-server-{i+1}")],
                    UserData=Base64(user_data),
                )
            )

    def add_outputs(self):
        instance_count = self.variables["jmeter_servers_count"]

        jmeter_endpoints = []
        for i in range(0, instance_count):
            jmeter_endpoints.append(
                Join(":", [GetAtt(f"JMeterServer{i+1}", "PrivateDnsName"), "1099"])
            )
        jmeter_remote_hosts = Join("=", ["remote_hosts", Join(",", jmeter_endpoints)])

        self.template.add_output(
            [Output("JMeterRemoteHosts", Value=jmeter_remote_hosts)]
        )


def sceptre_handler(sceptre_user_data):
    _jmeter_servers = JMeterServers(sceptre_user_data)
    _jmeter_servers.add_parameters()
    _jmeter_servers.add_resources()
    _jmeter_servers.add_outputs()
    return _jmeter_servers.template.to_json()
