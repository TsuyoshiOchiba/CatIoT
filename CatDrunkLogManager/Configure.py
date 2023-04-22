import configparser

""" Configureクラス
    アプリ設定を管理するクラス
"""
class Configure:
    """ 設定ファイルパス
    """
    INI_FILE_PATH = './config.ini'
    """ 文字コード
    """
    INI_ENCODE = 'UTF-8'
    """ コンストラクタ
    """
    def __init__(self):
        self.inifile = configparser.ConfigParser()
        self.inifile.read(self.INI_FILE_PATH, self.INI_ENCODE)
        self.database_setting = self.inifile['database_setting']
        self.cabration_setting = self.inifile['cabration_setting']
    
    """ DB設定を個別に取得する
    """
    def getDataBaseSetting(self, prop):
        return self.database_setting.get(prop)
    
    """ DB設定のオブジェクトを取得する
    """
    def getDataBaseSettingAll(self):
        return {
            'host' : self.getDataBaseSetting('host'),
            'user' : self.getDataBaseSetting('user'),
            'password' : self.getDataBaseSetting('password'),
            'database' : self.getDataBaseSetting('database')
        }
    
    """ センサー設定を個別に取得する
    """
    def getCabrationSetting(self, prop):
        return self.cabration_setting.get(prop)

