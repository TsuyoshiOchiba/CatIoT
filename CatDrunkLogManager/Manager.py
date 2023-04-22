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
        with open("logsetting.json") as f:
            config.dictConfig(json.load(f))
        self.appLogger = getLogger("appLogger")
        self.errLogger = getLogger("errLogger")
        self.appLogger.info("Manager起動")
        self.config = Configure()
        self.referenceUnit = self.config.getCabrationSetting('referenceUnit')
        self.hx = HX711(self.PIN_DAT, self.PIN_CLK)
        self.isRecording = False
        self.connectionParams = self.config.getDataBaseSettingAll()
        self.beforeVal = float(0)

    
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
        self.hx.set_reference_unit(float(self.referenceUnit))
        self.hx.reset()
        self.hx.tare()
        self.appLogger.info("Tare done! Add weight now...")

    """ 重量ログの記録開始
    """
    def startLog(self):
        self.appLogger.info("重量ログ記録開始")
        self.isRecording = True
        self.resetHX()
        self.recordingLog()

    """ 重量ログの停止
        タイマーを強制キャンセルできないので、停止後一定時間以内に1回はログ記録される
    """
    def endLog(self):
        self.isRecording = False

    """ 重量ログ記録実行
        設定ファイルのlogsleep秒の間隔でテーブルへ記録をInsert
    """
    def recordingLog(self):
        while self.isRecording:
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
                            # 重量生ログにINSERT
                            w_sql = "insert into W_WEIGHT_LOG (LOG_WEIGHT) values (%s)"
                            # デバッグ用出力
                            self.appLogger.info('重量生ログSQL' + w_sql)
                            cursor.execute(w_sql, (val))
                            # 飲水量ログのための計算
                            drunkVal = self.getDrunkeVal(val)
                            if 10 < drunkVal and drunkVal < 100:
                                # 飲水量ログにINSERT
                                t_sql = "insert into T_DRUNKED_LOG (DRUNKED_WEIGHT) values (%s)"
                                # デバッグ用出力
                                self.appLogger.info('飲水量ログSQL' + t_sql)
                                cursor.execute(t_sql, (drunkVal))
                        except Exception as e:
                            self.errLogger.error("SQL ERRORがあったのでロールバックしました。")
                            self.errLogger.error(e, exc_info=True)
                            # print(traceback.format_exc())
                            # ロールバック／これを書いておかないと直前までの更新がコミットされる
                            connection.rollback()
                            self.cleanAndExit()
                        connection.commit()
                self.hx.power_down()
                self.hx.power_up()
                time.sleep(float(self.config.getCabrationSetting('logsleep')))

            except (KeyboardInterrupt, SystemExit):
                self.cleanAndExit()
    
    """ 飲水量を計算
    """
    def getDrunkeVal(self, val: float):
        # 飲水量ログのための計算
        self.appLogger.info("前回重量" + str(self.beforeVal))
        self.appLogger.info("今回重量" + str(val))
        drunkVal = self.beforeVal - val
        self.beforeVal = val
        if self.beforeVal == 0:
            drunkVal = 0
        self.appLogger.info("導出飲水量" + str(drunkVal))
        return drunkVal

    """ システム終了コマンド
        基本、エラー発生時にしかキックしないセーフティー機構
    """
    def cleanAndExit(self):
        self.appLogger.info("センサー Cleaning...")
        GPIO.cleanup()
        self.appLogger.info("プロセス終了")
        sys.exit()


