class ResourceInfo2:
    def __init__(self, name, address, family, model, map_path=None, serial='-1'):
        self.name = name
        self.address = address
        self.family = family
        self.model = model
        self.serial = serial
        self.map_path = map_path
        self.subresources = []
        self.attrname2typevaluetuple = {}
        if False:
            self.subresources.append(ResourceInfo2(None, None, None, None))

    def set_attribute(self, name, value, typename='String'):
        self.attrname2typevaluetuple[name] = (typename, value)

    def get_attribute(self, name):
        return self.attrname2typevaluetuple[name][1]

    def to_string(self, tabs=''):
        def indent(t, s):
            return t + (('\n' + t).join(s.split('\n'))).strip()

        return indent(tabs,
'''<ResourceInfo
        Name="''' + self.name + '''"
        Address="''' + self.address + '''"
        ResourceFamilyName="''' + self.family + '''"
        ResourceModelName="''' + self.model + '''"
        SerialNumber="''' + self.serial + '''">
    <ChildResources>
''' + (
            '\n'.join([x.to_string(tabs=tabs + '    ') for x in self.subresources])
        ) + '''
    </ChildResources>
    <ResourceAttributes>
''' + (
            '\n'.join(['''<Attribute Name="''' + attrname + '''" Type="''' + self.attrname2typevaluetuple[attrname][0] + '''" Value="''' + self.attrname2typevaluetuple[attrname][1] + '''"/>''' for attrname in self.attrname2typevaluetuple.keys()])
        ) + '''    </ResourceAttributes>
''' + ('    <ResourceMapping><IncomingMapping>' + self.map_path + '</IncomingMapping></ResourceMapping>' if self.map_path else '') +
'''</ResourceInfo>
''')
