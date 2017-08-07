import poplib
import imaplib
import email
import email.parser
import io
import os
import datetime as dt
import time

host = 'pop.qiye.163.com' #'imap.qiye.163.com' #'smtp.qiye.163.com'
username = 'baiquaninvest@baiquaninvest.com'
password = 'Baiquan1818'


def email_process(emlinfo,savepth):
    emlparser = email.parser.BytesParser()
    msg = emlparser.parsebytes(emlinfo)

    sub = msg.get('Subject')
    subh= email.header.decode_header(sub)
    substr = subh[0][0].decode(subh[0][1])

    dttm = msg.get('Date').split(',')[1]   # mail date and time
    dttmstr = time.strftime('%Y-%m-%d %H:%M:%S ',time.strptime(dttm.strip(),'%d %b %Y %H:%M:%S +0800'))

    for part in msg.walk():
        if not part.is_multipart():
            filename = part.get_filename()
            content = part.get_payload(decode=True)
            if filename:  # Attachment
                dh = email.header.decode_header(filename)
                if dh[0][1] is not None:
                    filenm = dh[0][0].decode(dh[0][1])
                else:
                    filenm = dh[0][0]
                result_file = os.path.join(savepth, filenm)
            else:
                result_file = os.path.join(savepth,'text.html')
            try:
                with open(result_file, "wb") as f:
                    f.write(content)
            except BaseException as e:
                print("[-] Write file of email {0} failed: {1}".format(1, e))
            print('downloaded')

def imap4(username,password,host,port=143):
    M = imaplib.IMAP4_SSL(host)
    M.login(username, password)
    M.select('INBOX')
    typ, allmails = M.search(None, 'ALL')  # 找到邮件 arg2 'UNSEEN'
    mailids = allmails[0].decode().split()
    count = 0
    for mlid in mailids:
        # 提取 byte 格式
        tp, data = M.fetch(mlid, '(RFC822)')
        # 生成msg
        #msg = emlparser.parsebytes(data[0][1])
        msg = email.message_from_bytes(data[0][1])

        sub = msg.get('Subject')
        subh= email.header.decode_header(sub)
        substr = subh[0][0].decode(subh[0][1])
        print('Subject : ',substr)

        dttm = msg.get('Date').split(',')[1].strip().split(' ')   # mail date and time
        dttm = ' '.join(dttm[0:4])
        print(time.strftime('%Y-%m-%d %H:%M:%S ',time.strptime(dttm,'%d %b %Y %H:%M:%S')))

        fromh = email.header.decode_header(msg.get('From'))
        for fh in fromh:
            if fh[1] is None:
                try:
                    fm = fh[0].decode()
                except AttributeError:
                    fm = fh[0]
                print('From : ', fm.strip(' <>') )

        pth = r'E:\netval_auto_v2.0\modules\emails_download\files'
        ccount = 0
        for part in msg.walk():
            if not part.is_multipart():
                filename = part.get_filename()
                content = part.get_payload(decode=True)
                if filename:  # Attachment
                    dh = email.header.decode_header(filename)
                    if dh[0][1] is not None:
                        filenm = dh[0][0].decode(dh[0][1])
                    else:
                        filenm = dh[0][0]
                    result_file = os.path.join(pth, filenm)
                else:
                    result_file = os.path.join(pth,'content_'+str(count)+'.html')
                try:
                    with open(result_file, "wb") as f:
                        f.write(content)
                except BaseException as e:
                    print("[-] Write file of email {0} failed: {1}".format(1, e))
                ccount+=1
        count+=1
        if count>10:
            break
    M.close()  # close the currently selected mailbox
    M.logout()

def pop3(username,password,host,port=110):
    pop_conn = poplib.POP3(host=host)
    pop_conn.user(username)
    pop_conn.pass_(password)
    print('connected')
    stat = pop_conn.stat()
    print(stat)
    totnum = stat[0]
    for dumi in range(totnum):
        message = pop_conn.retr(dumi)
        buf = io.BytesIO()
        for line in message[1]:
            buf.write(line)
            buf.write(b'\n')
        buf.write(b'\n')
        buf.seek(0)
    pop_conn.quit()
    # eml = email.message_from_binary_file(buf)
    # eml = email.message_from_bytes(buf.getvalue())
    # eml = email.message_from_string(buf.getvalue().decode())
    emlparser = email.parser.BytesParser()
    msg = emlparser.parsebytes(buf.getvalue())


    sub = msg.get('Subject')
    subh= email.header.decode_header(sub)
    print('Subject : ',subh[0][0].decode(subh[0][1]))

    date = msg.get('Date').split(',')[1]
    print(date)

    pth = r'E:\netval_auto_v2.0\modules\emails_download'
    for part in msg.walk():
        if not part.is_multipart():
            filename = part.get_filename()
            content = part.get_payload(decode=True)
            if filename:  # Attachment
                dh = email.header.decode_header(filename)
                filenm = dh[0][0].decode(dh[0][1])
                result_file = os.path.join(pth, filenm)#"mail{0}_attach_{1}".format(1,dh[0][0]))
            else:
                result_file = os.path.join(pth,'text.html')
            try:
                with open(result_file, "wb") as f:
                    f.write(content)
            except BaseException as e:
                print("[-] Write file of email {0} failed: {1}".format(1, e))


if __name__=='__main__':
    pop3(username=username,password=password,host=host)
    # print()
    imap4(username=username,password=password,host=host)