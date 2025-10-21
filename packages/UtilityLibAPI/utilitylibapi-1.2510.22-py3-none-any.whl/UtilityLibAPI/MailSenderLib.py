import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formataddr
from typing import List, Optional
import os
import mimetypes

class CLASS_MailSender:
    def __init__(self,
                 Pms_SMTP_Server: str,
                 Pmi_Port: int,
                 Pms_Account: str,
                 Pms_Password: str,
                 Pmb_UseSSL: bool = True):
        """
        初始化郵件寄送物件
        :param Pms_SMTP_Server: 郵件伺服器主機 (ex: smtp.gmail.com)
        :param Pmi_Port: 通訊埠 (SSL=465, TLS=587)
        :param Pms_Account: 登入帳號
        :param Pms_Password: 登入密碼或應用程式密碼
        :param Pmb_UseSSL: 是否使用 SSL 連線 (預設 True)
        """
        self.Pms_SMTP_Server = Pms_SMTP_Server
        self.Pmi_Port = Pmi_Port
        self.Pms_Account = Pms_Account
        self.Pms_Password = Pms_Password
        self.Pmb_UseSSL = Pmb_UseSSL

    #------------------------------------------------------------
    def CUF_CreateMessage(self,
                          Pms_Subject: str,
                          Pms_BodyText: str,
                          Pms_BodyHTML: Optional[str] = None,
                          Pms_From: Optional[str] = None,
                          Pobj_To: Optional[List[str]] = None,
                          Pobj_Cc: Optional[List[str]] = None,
                          Pobj_Bcc: Optional[List[str]] = None,
                          Pobj_Attachments: Optional[List[str]] = None) -> MIMEMultipart:
        """
        建立郵件內容（支援 HTML / 附件）
        """
        msg = MIMEMultipart("alternative")
        msg["From"] = formataddr((Pms_From or self.Pms_Account, self.Pms_Account))
        msg["To"] = ", ".join(Pobj_To or [])
        if Pobj_Cc:
            msg["Cc"] = ", ".join(Pobj_Cc)
        msg["Subject"] = Pms_Subject

        # 純文字版本
        msg.attach(MIMEText(Pms_BodyText or "", "plain", "utf-8"))

        # HTML 版本
        if Pms_BodyHTML:
            msg.attach(MIMEText(Pms_BodyHTML, "html", "utf-8"))

        # 附件
        if Pobj_Attachments:
            for ms_path in Pobj_Attachments:
                try:
                    if not os.path.isfile(ms_path):
                        print(f"⚠️ Attachements not exists: {ms_path}")
                        continue

                    ctype, encoding = mimetypes.guess_type(ms_path)
                    if ctype is None or encoding is not None:
                        ctype = "application/octet-stream"
                    maintype, subtype = ctype.split("/", 1)

                    with open(ms_path, "rb") as f:
                        part = MIMEApplication(f.read(), _subtype=subtype)
                        filename = os.path.basename(ms_path)
                        part.add_header(
                            "Content-Disposition",
                            "attachment",
                            filename=("utf-8", "", filename)
                        )
                        msg.attach(part)
                except Exception as e:
                    print(f"⚠️ Can not add attachment: {ms_path} ({e})")

        return msg

    #------------------------------------------------------------
    def CUF_SendMail(self,
                     Pms_Subject: str,
                     Pms_BodyText: str,
                     Pms_BodyHTML: Optional[str],
                     Pobj_To: List[str],
                     Pobj_Cc: Optional[List[str]] = None,
                     Pobj_Bcc: Optional[List[str]] = None,
                     Pobj_Attachments: Optional[List[str]] = None) -> bool:
        """
        實際寄送郵件
        """
        msg = self.CUF_CreateMessage(
            Pms_Subject=Pms_Subject,
            Pms_BodyText=Pms_BodyText,
            Pms_BodyHTML=Pms_BodyHTML,
            Pobj_To=Pobj_To,
            Pobj_Cc=Pobj_Cc,
            Pobj_Bcc=Pobj_Bcc,
            Pobj_Attachments=Pobj_Attachments,
        )

        all_recipients = (Pobj_To or []) + (Pobj_Cc or []) + (Pobj_Bcc or [])

        try:
            if self.Pmb_UseSSL:
                with smtplib.SMTP_SSL(self.Pms_SMTP_Server, self.Pmi_Port) as server:
                    server.login(self.Pms_Account, self.Pms_Password)
                    server.sendmail(self.Pms_Account, all_recipients, msg.as_string())
            else:
                with smtplib.SMTP(self.Pms_SMTP_Server, self.Pmi_Port) as server:
                    server.ehlo()
                    server.starttls()
                    server.login(self.Pms_Account, self.Pms_Password)
                    server.sendmail(self.Pms_Account, all_recipients, msg.as_string())

            print("✅ Send Success!")
            return True
        except Exception as e:
            print("❌ Failure:", e)
            return False


# ================================================================================
# [範例]
# 匯入剛才寫好的 CLASS_MailSender
#from MailSender import CLASS_MailSender  # 假設你把上面的 class 儲存為 MailSender.py
if __name__ == "__main__":
    # === 初始化郵件傳送物件 ===
    mailer = CLASS_MailSender(
        Pms_SMTP_Server="msr.xxxx.net",
        Pmi_Port=465,
        Pms_Account="xxx.biz@xx.hxxxt.net",
        Pms_Password="xxxxx*",
        Pmb_UseSSL=True
    )

    # === 郵件收件者設定 ===
    ml_To  = ["gt504@gxxxxxh.biz", "txxxxx@ms27.xxxt.net"]
    ml_Cc  = ["ebooxxx3@hotmail.com.tw"]
    ml_Bcc = ["xxxxsty.lin@xxx.hinet.net"]  # 密件副本，不會顯示在郵件中

    # === 郵件主題與內容 ===
    ms_Subject = "團隊週報通知"

    ms_BodyText = """
這是一封自動寄出的團隊週報通知。
請參閱附加的 PDF 檔或 HTML 內文。
    """

    ms_BodyHTML = """
    <html>
      <body style="font-family: Microsoft JhengHei;">
        <h2 style="color: green;">🌟 團隊週報</h2>
        <p>各位同仁您好：</p>
        <p>以下為本週重點摘要：</p>
        <ul>
          <li>完成模組 A 測試</li>
          <li>修正 ERP 匯出問題</li>
          <li>新增客戶報表功能</li>
        </ul>
        <p>詳細報表請參閱附件。</p>
        <p style="color: gray;">系統自動寄出，請勿回覆。</p>
      </body>
    </html>
    """

    # === 附件路徑 ===
    ml_Attachments = [
        "X:\\TEMP\\BOOK\\RCR6000_匯出外部資料_RCR6000EXT_XXX.pdf",
        "X:\\TEMP\\BOOK\\K9AKW4.jpg"
    ]

    # === 寄送 ===
    mb_OK = mailer.CUF_SendMail(
        Pms_Subject=ms_Subject,
        Pms_BodyText=ms_BodyText,
        Pms_BodyHTML=ms_BodyHTML,
        Pobj_To=ml_To,
        Pobj_Cc=ml_Cc,
        Pobj_Bcc=ml_Bcc,
        Pobj_Attachments=ml_Attachments
    )

    if mb_OK:
        print("✅ 多人郵件已成功寄出！")
    else:
        print("❌ 寄送失敗，請檢查設定。")
