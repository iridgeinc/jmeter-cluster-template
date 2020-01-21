import troposphere.ec2 as ec2
from troposphere import Output, Parameter, Ref, Tags, Template


class JMeterSecurityGroups:
    def __init__(self, sceptre_user_data):
        self.template = Template()
        self.sceptre_user_data = sceptre_user_data
        self.template.set_description("JMeter SecurityGroups")

    def add_parameters(self):
        self.jmeter_vpc = self.template.add_parameter(
            Parameter("JMeterVpc", Description="id of vpc", Type="String",)
        )

        self.jmeter_allowed_ip = self.template.add_parameter(
            Parameter(
                "JMeterAllowedIp", Description="ip allowed to ssh", Type="String",
            )
        )

    def add_resources(self):
        self.jmeter_security_group = self.template.add_resource(
            ec2.SecurityGroup(
                "JMeterSecurityGroup",
                VpcId=Ref(self.jmeter_vpc),
                GroupDescription="jmeter_security_group",
                Tags=Tags(Name="jmeter_security_group"),
            )
        )

        self.jmeter_ingress_rule_01 = self.template.add_resource(
            ec2.SecurityGroupIngress(
                "JMeterIngressRule01",
                GroupId=Ref(self.jmeter_security_group),
                ToPort="22",
                IpProtocol="tcp",
                CidrIp=Ref(self.jmeter_allowed_ip),
                FromPort="22",
            )
        )

        self.jmeter_ingress_rule_02 = self.template.add_resource(
            ec2.SecurityGroupIngress(
                "JMeterIngressRule02",
                GroupId=Ref(self.jmeter_security_group),
                ToPort="1099",
                IpProtocol="tcp",
                SourceSecurityGroupId=Ref(self.jmeter_security_group),
                FromPort="1099",
            )
        )

        self.jmeter_ingress_rule_03 = self.template.add_resource(
            ec2.SecurityGroupIngress(
                "JMeterIngressRule03",
                GroupId=Ref(self.jmeter_security_group),
                ToPort="65535",
                IpProtocol="tcp",
                SourceSecurityGroupId=Ref(self.jmeter_security_group),
                FromPort="30000",
            )
        )

    def add_outputs(self):
        self.template.add_output(
            [Output("JMeterSecurityGroup", Value=Ref(self.jmeter_security_group))]
        )


def sceptre_handler(sceptre_user_data):
    _jmeter_security_groups = JMeterSecurityGroups(sceptre_user_data)
    _jmeter_security_groups.add_parameters()
    _jmeter_security_groups.add_resources()
    _jmeter_security_groups.add_outputs()
    return _jmeter_security_groups.template.to_json()
