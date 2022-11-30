import ftplib
import os

def himawari_download(year, month, day, hour, minute, band, working_dir_path='./working/'):

    os.makedirs(working_dir_path, exist_ok=True)
    # ftp接続情報
    ftp_user = 'meguyama'
    ftp_pass = 'hWzL92BM'
    ftp_address = 'sc-trans.nict.go.jp'

    # ftp接続
    ftp = ftplib.FTP(ftp_address)
    ftp.set_pasv('true')
    ftp.login(ftp_user, ftp_pass)

    # ftpサーバー内ディレクトリ名を構築
    yyyy = str(year).zfill(4)
    mm = str(month).zfill(2)
    dd = str(day).zfill(2)
    HH = str(hour).zfill(2)
    MM = str(minute).zfill(2)
    Bbb = f'B{str(band).zfill(2)}'

    # 最下層のディレクトリ名を構築
    ftp_dir_name= f'/himawari_real/HIMAWARI-8/HINC/Ncjp/{yyyy}{mm}/{dd}/{yyyy}{mm}{dd}{HH}00/{MM}/{Bbb}/'

    # ftp内ファイルのpathリストを作成
    ftp_ls = ftp.nlst(ftp_dir_name)

    # ftp_ls内のファイルをひとつづつ out_dir_path内にダウンロード
    for ftp_file_path in ftp_ls:
        out_file_name = ftp_file_path.split('/')[-1]

        # 空白のバイナリファイルを作成し開いて、ダウンロードデータを書き込む
        with open(f'{working_dir_path}/{out_file_name}', 'wb') as ftp_fb:
            ftp.retrbinary(f'RETR {ftp_file_path}', ftp_fb.write)

    ftp.close()