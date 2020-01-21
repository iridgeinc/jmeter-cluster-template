import yaml
from troposphere import Base64, Parameter, Ref, Template
from troposphere.ec2 import Instance, Tag


class JMeterClient:
    def __init__(self, sceptre_user_data):
        self.template = Template()
        self.sceptre_user_data = sceptre_user_data
        self.template.set_description("JMeter Client")
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

        self.jmeter_client_instance_type = self.template.add_parameter(
            Parameter(
                "JMeterClientInstanceType",
                Description="jmeter_client_instance_type",
                Type="String",
            )
        )

        self.jmeter_key_pair = self.template.add_parameter(
            Parameter("JMeterKeyPair", Description="jmeter_key_pair", Type="String",)
        )

    def add_resources(self):
        self.tag = Tag(key="Name", value="jmeter-client")
        jmeter_install_version = self.variables["jmeter_install_version"]

        user_data = f"""#!/bin/sh
            yum install -y git wget java-1.8.0-openjdk java-1.8.0-openjdk-devel
            mkdir /home/ec2-user/jmeter && cd /home/ec2-user/jmeter
            wget -O ./jmeter.tar.gz \\
            https://archive.apache.org/dist/jmeter/binaries/apache-jmeter-{jmeter_install_version}.tgz
            tar xvfz jmeter.tar.gz --strip=1 && rm -f jmeter.tar.gz
            chown ec2-user:ec2-user -R .
            """

        self.instance = self.template.add_resource(
            Instance(
                "JMeterClient",
                ImageId=Ref(self.jmeter_ami_id),
                InstanceType=Ref(self.jmeter_client_instance_type),
                KeyName=Ref(self.jmeter_key_pair),
                SecurityGroupIds=[Ref(self.jmeter_security_group)],
                SubnetId=Ref(self.jmeter_subnet),
                Tags=[self.tag],
                UserData=Base64(user_data),
            )
        )


def sceptre_handler(sceptre_user_data):
    _jmeter_client = JMeterClient(sceptre_user_data)
    _jmeter_client.add_parameters()
    _jmeter_client.add_resources()
    return _jmeter_client.template.to_json()
