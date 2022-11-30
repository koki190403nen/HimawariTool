# %%
import bz2
import os
import glob
import shutil

# %%
def bunzip(working_dir='./working/'):
    bzip_file_ls  = glob.glob(f'{working_dir}*.bz2')

    # workingディレクトリ内の物をひとつづつ解凍
    for bzip_file_path in bzip_file_ls:
        out_file_path = bzip_file_path[:-4]

        with bz2.BZ2File(bzip_file_path) as fr:
            with open(out_file_path,"wb") as fw:
                shutil.copyfileobj(fr,fw)  # 解凍する
        os.remove(bzip_file_path)  # 最後に解凍前ファイルは消す

