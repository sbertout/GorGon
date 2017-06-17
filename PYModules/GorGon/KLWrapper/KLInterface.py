from KLFunction import KLFunction

class KLInterface:

    def __init__(self, name):
        self.__name = name
        self.__members = []

    def getName(self):
        return self.__name

    def _setMembers(self, members):
        for m in members:
            functionName = m['name']
            access = m['cgAccess']
            returnType = m['returnType'] if 'returnType' in m else None
            params = m['params'] if 'params' in m else None
            klFunction = KLFunction(functionName, returnType=returnType, access=access)
            if params:
                klFunction._addParams(params)
            self.__members.append(klFunction)

    def getMemberCount(self):
        return len(self.__members)

    def getMember(self, idx):
        return self.__members[idx]
