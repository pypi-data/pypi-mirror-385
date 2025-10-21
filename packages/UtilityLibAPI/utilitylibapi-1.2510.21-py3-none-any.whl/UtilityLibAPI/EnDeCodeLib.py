# ============================================================================
#                           通用 加密/解密 (跨平台)
# ============================================================================
import base64

# ================================================================================
class CLASS_EnDeCodeLib:
    def __init__(self):
        # 設定預設的 CROSS 加密金鑰
        self.CVmba_CROSS_KEY = [];
        self.CVmba_CROSS_KEY.append(0x3f);
        self.CVmba_CROSS_KEY.append(0x6b);
        self.CVmba_CROSS_KEY.append(0x59);
        self.CVmba_CROSS_KEY.append(0x48);
        # ------------------------------------------------------------------
        self.CVms_CROSS_ASC = \
             "AaBbFfGg 125~!@#$)HhIiLlMm_+`-=CcD34dEe:[]JjKk\\\'"\
             "NnOoSsTt670%UuXxYyZz^&*Pp89QqRr(<>?VvWw,./;{}|\"";
        self.CVms_CROSS_MAP = \
             "~!@#$%^& ()_+QWERbnmTOP{}|ASghjkDFL:\"ZXiopCV<>?`" \
             "125-=*qwert67890yuBNM[]\\asd34fGHJKl;\'zxYUIcv,./";
        # ------------------------------------------------------------------
        
        
    # ================================================================================
    #                                   PRIVATE
    # ================================================================================
    # ----------------------------------------------------------------------------
    # 功能: CROSS 金鑰加密 (針對不可視字元: 使用金鑰加密)
    # 傳入:
    # 傳回:
    # ----------------------------------------------------------------------------
    def CVF_CROSS_XOR(self, Pmc_SRC_CH):
        mia_SRCCH = [];
        ms_ENCODE = "";
        mi_ENCODE = 0;
        mi_c      = 0;

        mia_SRCCH = Pmc_SRC_CH.encode('big5');
        # ------------------------------------------------------------
        for mi_c in range(0, len(mia_SRCCH)):
            mi_ENCODE = mia_SRCCH[mi_c];
            # ------------------------------------------------------------
            for mi_d in range(0, len(self.CVmba_CROSS_KEY)):
                mi_ENCODE ^= self.CVmba_CROSS_KEY[mi_d];
            # ------------------------------------------------------------
            ms_ENCODE += chr(mi_ENCODE);
        # ------------------------------------------------------------
        return(ms_ENCODE);
    
    
    # ================================================================================
    #                                   PUBLIC
    # ================================================================================
    # ----------------------------------------------------------------------------
    # 功能: 設定 CROSS 加密金鑰
    # 傳入:
    # 傳回:
    # ----------------------------------------------------------------------------
    def CUF_CROSS_SetKey(self, Rmca_KeyCode):
        if(len(Rmca_KeyCode) <= 0):
            return;
        # ------------------------------------------------------------
        self.CVmba_CROSS_KEY.clear();
        # ------------------------------------------------------------
        for mi_c in range(0, len(Rmca_KeyCode)):
            self.CVmba_CROSS_KEY = Rmca_KeyCode[mi_c];
    
    # ----------------------------------------------------------------------------
    # 功能: 回傳 CROSS 加密金鑰
    # 傳入:
    # 傳回:
    # ----------------------------------------------------------------------------
    def CUF_CROSS_GetKey(self):
        return(self.CVmba_CROSS_KEY);
    
    
    # ----------------------------------------------------------------------------
    # 功能: CROSS 加密程序
    # 傳入:
    # 傳回:
    # ----------------------------------------------------------------------------
    def CUF_CROSS_EnCode(self, Pms_SRC_Text):
        ms_RET_STR = "";
        mB_Found   = False;
        mi_c       = 0;
        mi_d       = 0;
        # ------------------------------------------------------------
        if(type(Pms_SRC_Text) is bytes):
            Pms_SRC_Text = str(Pms_SRC_Text);
        # ------------------------------------------------------------
        # (1) 判斷是否為 ASCII 可視字元,若是則搜尋對應的 CVms_CROSS_MAP[?] 字元
        for mi_c in range(0, len(Pms_SRC_Text)):
            mB_Found = False;
            # --------------------------------------------
            for mi_d in range(0, len(self.CVms_CROSS_ASC)):
                if(Pms_SRC_Text[mi_c] == self.CVms_CROSS_ASC[mi_d]):
                    mB_Found = True;
                    break;
            # --------------------------------------------
            if(mB_Found):
                # (1-1) 可視字元  : 找到可視字元對應的加密表字元
                ms_RET_STR += self.CVms_CROSS_MAP[mi_d];
            else:
                # (1-2) 不可視字元: 使用金鑰加密
                ms_RET_STR += self.CVF_CROSS_XOR(Pms_SRC_Text[mi_c]);
        # ------------------------------------------------------------
        return(ms_RET_STR);
    
    
    # ----------------------------------------------------------------------------
    # 功能: CROSS 解密程序
    # 傳入:
    # 傳回:
    # ----------------------------------------------------------------------------
    def CUF_CROSS_DeCode(self, Pms_ENC_Text):
        ms_RET_STR = "";
        mB_Found   = False;
        mi_c       = 0;
        mi_d       = 0;
        # ------------------------------------------------------------
        # (1) 判斷是否為 ASCII 可視字元,若是則搜尋對應的 CVms_CROSS_MAP[?] 字元
        for mi_c in range(0, len(Pms_ENC_Text)):
            mB_Found = False;
            # --------------------------------------------
            for mi_d in range(0, len(self.CVms_CROSS_MAP)):
                if(Pms_ENC_Text[mi_c] == self.CVms_CROSS_MAP[mi_d]):
                    mB_Found = True;
                    break;
            # --------------------------------------------
            if(mB_Found):
                # (1-1) 可視字元  : 找到可視字元對應的解密表字元
                ms_RET_STR += self.CVms_CROSS_ASC[mi_d];
            else:
                # (1-2) 不可視字元: 使用金鑰加密
                ms_RET_STR += self.CVF_CROSS_XOR(Pms_ENC_Text[mi_c]);
        # ------------------------------------------------------------
        return(ms_RET_STR);


    # ----------------------------------------------------------------------------
    # 功能: CROSS 加密程序 (Base64 版本)
    # 傳入:
    # 傳回:
    # ----------------------------------------------------------------------------
    def CUF_CROSS_EnCodeBase64(self, Pms_SRC_Text):
        ms_EnCode  = "";
        ms_BuffSTR = "";

        ms_BuffSTR = Pms_SRC_Text.encode('big5');
        # ------------------------------------------------------------
        for mi_c in range(0, len(ms_BuffSTR)):
            ms_EnCode += chr(ms_BuffSTR[mi_c]);
        # ------------------------------------------------------------
        # (1) Base64 轉碼
        ms_EnCode = base64.b64encode(ms_EnCode.encode('utf-8'));
        # ------------------------------------------------------------
        # (2) 明文加密
        ms_EnCode = self.CUF_CROSS_EnCode(ms_EnCode);
        # ------------------------------------------------------------
        ms_EnCode = ms_EnCode.encode("utf-8");
        # ---------e---------------------------------------------------
        return(ms_EnCode);


    # ----------------------------------------------------------------------------
    # 功能: CROSS 解密程序 (Base64 版本)
    # 傳入:
    # 傳回:
    # ----------------------------------------------------------------------------
    def CUF_CROSS_DeCodeBase64(self, Pms_ENC_Text):
        ms_DeCode = "";

        ms_EnCode = Pms_ENC_Text.encode('big5');
        # ------------------------------------------------------------
        # (1) Base64 解碼
        ms_DeCode = base64.b64decode(ms_EnCode);
        # ------------------------------------------------------------
        # (2) 解密 
        ms_DeCode = self.CUF_CROSS_DeCode(ms_DeCode);
        # ------------------------------------------------------------
        ms_DeCode = ms_DeCode.encode("utf-8");
        # ------------------------------------------------------------
        return(ms_DeCode);     
    

# ================================================================================
#                                   EXAMPLE
# ================================================================================
if(__name__=="__main__"):
    Gobj_EnDeCode = CLASS_EnDeCodeLib();
    
    ms_TEXT1 = "abcd,123 4567";
    ms_TEXT2 = "abc真正好123,Good 太棒了 ";
    # ------------------------------------------------------------
    print(Gobj_EnDeCode.CUF_CROSS_EnCode(ms_TEXT1));
    print(Gobj_EnDeCode.CUF_CROSS_EnCode(ms_TEXT2.encode('big5')));
    print(Gobj_EnDeCode.CUF_CROSS_EnCodeBase64(ms_TEXT2));