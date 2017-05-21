# http://ozzmaker.com/add-colour-to-text-in-python/
class ColoredString:
    @staticmethod
    def Grey(str):
        return '\033[1;30m'+ str + '\033[1;m'

    @staticmethod
    def Red(str):
        return '\033[1;31m'+ str + '\033[1;m'
    
    @staticmethod
    def Green(str):
        return '\033[1;32m'+ str + '\033[1;m'
    
    @staticmethod
    def Yellow(str):
        return '\033[1;33m'+ str + '\033[1;m'
    
    @staticmethod
    def Blue(str):
        return '\033[1;34m'+ str + '\033[1;m'
    
    @staticmethod
    def Magenta(str):
        return '\033[1;35m'+ str + '\033[1;m'
    
    @staticmethod
    def Cyan(str):
        return '\033[1;36m'+ str + '\033[1;m'
    
    @staticmethod
    def White(str):
        return '\033[1;37m'+ str + '\033[1;m'
    
    @staticmethod
    def BgGrey(str):
        return '\033[1;40m'+ str + '\033[1;m'
    
    @staticmethod
    def BgRed(str):
        return '\033[1;41m'+ str + '\033[1;m'
    
    @staticmethod
    def BgGreen(str):
        return '\033[1;42m'+ str + '\033[1;m'
    
    @staticmethod
    def BgYellow(str):
        return '\033[1;43m'+ str + '\033[1;m'
    
    @staticmethod
    def BgBlue(str):
        return '\033[1;44m'+ str + '\033[1;m'
    
    @staticmethod
    def BgMagenta(str):
        return '\033[1;45m'+ str + '\033[1;m'
    
    @staticmethod
    def BgCyan(str):
        return '\033[1;46m'+ str + '\033[1;m'
    
    @staticmethod
    def BgWhite(str):
        return '\033[1;47m'+ str + '\033[1;m'