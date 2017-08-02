import poplib
import imaplib
import email
import io
from email import parser

# 链接 IMAP
host = 'smtp.qiye.163.com'
username = 'baiquaninvest@baiquaninvest.com'
password = 'Baiquan1818'

M = imaplib.IMAP4_SSL(host)
M.login(username, password)
M.select('INBOX')
typ, data = M.search(None, 'ALL')  # 找到邮件 arg2 'UNSEEN'

count = 0
print(len(data[0].split()))
emails = data[0].split()

for num in emails:
    if count<1:
        # 提取 byte 格式
        tp, dat = M.fetch(emails[5], '(RFC822)')
        # 生成msg
        msg = email.message_from_string(str(dat[0][1],encoding='GB2312'))
        print(msg.keys())
        print(msg.get_charset())
        print('\n')
        for part in msg.walk():
            if not part.is_multipart():
                print(part.get_content_type())
                print(part.get_params())
                print(part.get_filename())
                print('\n')

        # for part in msg.walk():
        #     if not part.is_multipart():
        #         contenttype = part.get_content_type()
        #         filename = part.get_filename()
        #         print(filename)
        #         # for f in filename:
        #         #     if f is not None:
        #         #         fname = email.header.decode_header(f)
        #         #         print(fname)

        # # 解码
        # header = email.header.decode_header(msg['Subject'])
        # fromadd = email.utils.parseaddr(msg['From'])
        # toadd = email.utils.parseaddr(msg['To'])
        #
        # print(str(header[0][0],encoding='gb2312'))
        # print(fromadd[1])
        # print(toadd[1])
        #
        # print('\n')
        count+=1
    else:
        break

M.close()
M.logout()

# try:
#     pop_conn = poplib.POP3(host)
#     pop_conn.user(username)
#     pop_conn.pass_(password)
#
#     print('connected \n')
#     print(pop_conn.stat())
#
#     #messages = [pop_conn.retr(i) for i in range(1, 2)]#len(pop_conn.list()[1]) + 1)]
#     message = pop_conn.retr(2191)
#     print(message)
# except:
#     raise
# finally:
#     print('conn closed')
#     pop_conn.quit()

print("[-] {0},{1}".format('test','hello'))