import time
import sys
from CatDrunkLogManager.Configure import Configure
from logging import getLogger, config
import json
import RPi.GPIO as GPIO
from hx711py.hx711 import HX711
import pymysql.cursors
from decimal import Decimal

""" Managerクラス
    重量のテーブルログを管理するクラス
"""
class Manager:
    PIN_DAT = 5
    PIN_CLK = 6
    """ コンストラクタ
    """
    def __init__(self):
        with open("/env/logsetting.json") as f:
            config.dictConfig(json.load(f))
        self.appLogger = getLogger("appLogger")
        self.errLogger = getLogger("errLogger")
        self.appLogger.info("Manager起動")
        self.config = Configure()
        self.referenceUnit = self.config.getCabrationSetting('referenceUnit')
        self.offset = self.config.getCabrationSetting('offset')
        self.hx = HX711(self.PIN_DAT, self.PIN_CLK)
        self.connectionParams = self.config.getDataBaseSettingAll()

    
    """ DBへの接続オブジェクトを取得する
    """
    def getConnection(self):
        self.appLogger.info("DB接続開始")
        return pymysql.connect(host=self.connectionParams['host'],
                                            user=self.connectionParams['user'],
                                            password=self.connectionParams['password'],
                                            database=self.connectionParams['database'],
                                            cursorclass=pymysql.cursors.DictCursor,
                                            autocommit=False)

    """ 重量センサーのドライバ初期化
    """
    def resetHX(self):
        self.appLogger.info("センサー初期化")
        # データの並び順を指定
        self.hx.set_reading_format("MSB", "MSB")
        # キャリブレーション値を設定
        self.appLogger.info('キャブレーション値:' + self.referenceUnit)
        self.appLogger.info('オフセット値:' + self.offset)
        self.hx.set_offset_A(float(self.offset))
        self.hx.set_reference_unit(float(self.referenceUnit))
        self.hx.reset()
        self.appLogger.info("Tare done! Add weight now...")

    """ 重量ログの記録開始
    """
    def startLog(self):
        self.appLogger.info("重量ログ記録開始")
        self.resetHX()
        self.recordingLog()

    """ 重量ログ記録実行
    """
    def recordingLog(self):
        try:
            # 重量計測
            val = self.hx.get_weight(5)
            # デバッグ用出力
            self.appLogger.info('計測結果：' + str(val))
            # DBコネクション接続
            with self.getConnection() as connection:
                # トランザクション開始
                connection.begin()
                with connection.cursor() as cursor:
                    try: 
                        # 検出拠点を取得
                        place = self.config.getCabrationSetting('logplace')
                        # 重量生ログにINSERT
                        w_sql = "insert into W_WEIGHT_LOG (LOG_PLACE, LOG_WEIGHT) values (%s, %s)"
                        # デバッグ用出力
                        self.appLogger.info('重量生ログSQL' + w_sql)
                        cursor.execute(w_sql, (place, val))
                        connection.commit()
                        # クロージング
                        self.appLogger.info("正常終了")
                        self.cleanAndExit()
                    except Exception as e:
                        self.errLogger.error("SQL ERRORがあったのでロールバックしました。")
                        self.errLogger.error(e, exc_info=True)
                        # print(traceback.format_exc())
                        # ロールバック／これを書いておかないと直前までの更新がコミットされる
                        connection.rollback()
                        self.cleanAndExit()
            self.hx.reset()
        except Exception as e:
            self.appLogger.error("何らかの異常終了")
            self.errLogger.error(e, exc_info=True)
            self.cleanAndExit()

    """ システム終了コマンド
        基本、エラー発生時にしかキックしないセーフティー機構
    """
    def cleanAndExit(self):
        self.appLogger.info("センサー Cleaning...")
        GPIO.cleanup()
        self.appLogger.info("プロセス終了")
        sys.exit()


