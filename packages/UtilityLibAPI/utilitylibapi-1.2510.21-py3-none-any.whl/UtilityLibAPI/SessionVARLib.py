import pymysql
import pickle
import time
import uuid

class CLASS_SessionVAR:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.table_name = "_session_table"

    # ----------------------------
    # 建立 SessionID
    # ----------------------------
    def CUF_New_SessionID(self):
        return(str(uuid.uuid4()))

    # ----------------------------
    # 建立連線與表
    # ----------------------------
    def CUF_Create(self, Pms_host:str, Pmi_port:int, Pms_user:str, Pms_password:str, Pms_db:str, 
                   Pms_SessionID:str=None,
                   Pms_table_name:str="_session_table"):
        self.conn = pymysql.connect(
            host=Pms_host,
            port=Pmi_port,
            user=Pms_user,
            password=Pms_password,
            database=Pms_db,
            charset='utf8mb4',
            autocommit=True
        )
        self.cursor = self.conn.cursor()
        self.table_name = Pms_table_name

        # 建立表格，如果不存在
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS `{self.table_name}` (
            `SessionID` VARCHAR(36) NOT NULL,
            `VarName` VARCHAR(255) NOT NULL,
            `VarValue` LONGBLOB,
            `UpdateTime` BIGINT NOT NULL,
            PRIMARY KEY (`SessionID`, `VarName`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        self.cursor.execute(create_sql)

        # 回傳 SessionID
        if(Pms_SessionID == ""):
            session_id = self.CUF_New_SessionID();
        else:
            session_id = Pms_SessionID;
        return(session_id);

    # ----------------------------
    # 儲存變數
    # ----------------------------
    def CUF_SET(self, Pms_SessionID, Pms_VarName, Pms_VarValue):
        blob_data = pickle.dumps(Pms_VarValue)
        update_time = int(time.time())
        sql = f"""
        INSERT INTO `{self.table_name}` (SessionID, VarName, VarValue, UpdateTime)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            VarValue = VALUES(VarValue),
            UpdateTime = VALUES(UpdateTime)
        """
        self.cursor.execute(sql, (Pms_SessionID, Pms_VarName, blob_data, update_time))

    # ----------------------------
    # 取得變數
    # ----------------------------
    def CUF_GET(self, Pms_SessionID, Pms_VarName):
        sql = f"SELECT VarValue FROM `{self.table_name}` WHERE SessionID=%s AND VarName=%s"
        self.cursor.execute(sql, (Pms_SessionID, Pms_VarName))
        result = self.cursor.fetchone()
        if result:
            return pickle.loads(result[0])
        return None

    # ----------------------------
    # 釋放 Session
    # ----------------------------
    # 依 SessionID 刪除，或依秒數刪除舊資料
    def CUF_Release(self, Pms_param):
        if isinstance(Pms_param, str):
            sql = f"DELETE FROM `{self.table_name}` WHERE SessionID=%s"
            self.cursor.execute(sql, (Pms_param,))
        elif isinstance(Pms_param, (int, float)):
            threshold = int(time.time()) - int(Pms_param)
            sql = f"DELETE FROM `{self.table_name}` WHERE UpdateTime < %s"
            self.cursor.execute(sql, (threshold,))

    # ----------------------------
    # 關閉資源
    # ----------------------------
    def CUF_Close(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn:
            self.conn.close()
            self.conn = None

# =============================
# 範例用法
# =============================
if(__name__ == "__main__"):
    objSession = CLASS_SessionVAR()
    session_id = objSession.CUF_Create(Pms_host="mis.gotech.biz", 
                                       Pmi_port=3300, Pms_db="df8000", 
                                       Pms_user="root",
                                       Pms_password="gotechdf8000sys",
                                       Pms_SessionID="xx-202510131127");

    # 儲存資料
    objSession.CUF_SET(session_id, "mylist", [1,2,3])
    objSession.CUF_SET(session_id, "mydict", {"a":1, "b":2})
    
    # 取得資料
    mylist = objSession.CUF_GET(session_id, "mylist")
    mydict = objSession.CUF_GET(session_id, "mydict")
    print(mylist, mydict)

    # 釋放單一 session
    # objSession.CUF_Release(session_id)

    # 釋放超過 600 秒的資料
    # objSession.CUF_Release(600)

    
    mylist = [5,6,7,8,9];
    objSession.CUF_SET(session_id, "mylist", mylist);

    mylist = [0];
    print(mylist);

    mylist = objSession.CUF_GET(session_id, "mylist");
    print(mylist);

    objSession.CUF_SET(session_id, "")

    objSession.CUF_Close()
