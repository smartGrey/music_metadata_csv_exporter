from pprint import pprint
import os, sys
import csv
from tinytag import TinyTag
from pathlib import Path
from datetime import datetime



# 使用方式: 不需要编辑这个文件, 直接在终端执行下面命令
# pip install tinytag
# python3 save_to_csv.py /Volumes/SanDisk256g/MUSIC
# 就会在 MUSIC 的父级目录中创建一个'歌曲元数据备份 2025-05-02 21_47.csv'文件, 和 MUSIC 同级
# 包括了 MUSIC 中所有音频文件的元数据
# 如果有一天你的音乐播放器丢了,就可以凭借这个备份文件,以及所有音频文件的备份,重新组织你的音乐内容,而不用一无所有



# 得到所有音频文件的路径
def get_all_audio_files_path(path):
    paths = []
    for location, _, files_name in os.walk(path):
        for file_name in files_name:
            file_path = os.path.join(location, file_name)
            if TinyTag.is_supported(file_path) and file_name[0]!='.': # mac系统中每个文件都会出现.开头的同名文件,会报错,需要过滤掉
                paths.append(file_path)
    return paths


# 根据一个文件的路径,获得它的所有元数据
def get_audio_metadata(file_path, base_dir):
    tag = TinyTag.get(file_path)
    # 处理m4a文件读不到duration属性(为None)的情况
    duration = tag.duration
    if not duration:
        duration = '未知'
    else:
        duration = int(round(duration))
        duration = f'{duration//60:02d}:{duration%60:02d}'
    return {
        '曲名': tag.title,
        '艺人': tag.artist,
        '专辑': tag.album,
        '出版日期': tag.year,
        '音轨编号': tag.track,
        '时长': duration,
        '文件大小': f'{round(tag.filesize/1000000, 1)} MB',
        '文件路径': Path(*Path(file_path).parts[len(Path(base_dir).parts)-1:]), # 绝对路径 - base_dir
    }


# 将元数据写入CSV文件
def save_metadata_to_csv_and_count(file_paths, output_csv_path, base_dir, counter):
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            '计数',
            '曲名',
            '艺人',
            '专辑',
            '出版日期',
            '音轨编号',
            '时长',
            '文件大小',
            '文件路径',
        ])
        writer.writeheader()
        for i in range(len(file_paths)):
            file_path = file_paths[i]
            count = i+1
            # print(f'正在读取{count}: {file_path}') # 遇到报错可以把这个打开调试
            metadata = get_audio_metadata(file_path, base_dir)
            metadata['计数'] = count # 加一列,作为索引,也作为统计
            counter.doCount(metadata) # 进行统计
            try:
                writer.writerow(metadata)
                # print('记录成功')  # 遇到报错可以把这个打开调试
            except Exception as e:
                print(f"向 csv 文件 {file_path} 写入时发生错误: {e}")


# 删除原先根目录下的元数据备份文件
def delete_old_metadata_backup_file(source_directory_path, backup_file_name):
    for filename in os.listdir(source_directory_path):
        if backup_file_name in filename  and filename[0]!='.': # mac系统中每个文件都会出现.开头的同名文件,会报错,需要过滤掉
            file_path = os.path.join(source_directory_path, filename)
            os.remove(file_path)


# 一个自定义的统计器
# 只需要在这里定义数据、统计操作、最终输出三个函数即可
class Counter():
    def __init__(self):
        # 例子:
        # self.zuoxiao_songs_num = 0
        pass

    def doCount(self, metadata):
        # 例子:
        # if '左小祖咒' in metadata['艺人']:
        #     self.zuoxiao_songs_num += 1
        pass

    def __del__(self):
        # 例子:
        # print(f'统计结果: 左小祖咒一共有: [{self.zuoxiao_songs_num}] 首歌')
        pass



# 程序从这里开始执行:

counter = Counter() # 生成一个统计器对象
args = sys.argv # 获取终端传入的参数
backup_file_name = '歌曲元数据备份' # 生成的元数据备份文件的标题
if not len(args)>1:
    print('缺少一个参数: 要导出目录的绝对路径')
else:
    # 将第一个参数处理为绝对路径, 作为源路径
    source_directory_path = os.path.abspath(args[1]) # 把源路径转换成绝对路径
    source_directory_parent_path = os.path.dirname(source_directory_path) # 源路径的父路径
    # 删除原先的元数据文件
    delete_old_metadata_backup_file(source_directory_parent_path, backup_file_name)
    # 设置输出路径(放到要备份的目录的父级里,和要备份的目录同级)
    timestamp = datetime.now().strftime('%Y-%m-%d %H_%M')
    target_csv_file_path = source_directory_parent_path+f"/{backup_file_name} {timestamp}.csv"
    # 提取数据
    audio_files_paths = get_all_audio_files_path(source_directory_path)
    save_metadata_to_csv_and_count(audio_files_paths, target_csv_file_path, source_directory_path, counter)
    # 提示成功
    print(f"{len(audio_files_paths)} 首歌曲的元数据已成功保存在: {target_csv_file_path}")
