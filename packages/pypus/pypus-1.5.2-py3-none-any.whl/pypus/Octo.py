class OctoVar:
    def __init__(self, name, value, scope):
        self.name = name
        self.value = value
        self.scope = scope

    def __repr__(self):
        return f'OctoVar({self.name}, {self.value}, {self.scope})'

    def getName(self):
        return(self.name)

    def setName(self, newName):
        self.name = newName

    def getValue(self):
        return(self.value)

    def setValue(self, newValue):
        self.value = newValue

    def getScope(self):
        return(self.scope)

    def setScope(self, newScope):
        self.scope = newScope

    def getScopeEnvironment(self):
        if 'Environment' in self.scope:
            return self.scope['Environment']

    def setScopeEnvironment(self, newScopeEnvironment):
        self.scope['Environment'] = newScopeEnvironment

    def getVarAsDict(self):
        vdict = {'Name': self.name, 'Value': self.value, 'Scope': self.scope}
        return vdict
