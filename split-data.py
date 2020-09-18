#!/usr/bin/env python
import random
import os
import pandas as pd

if __name__ == '__main__':
    """
    把csv格式的数据文件`filename` 按照比例`split_with` 分成若干部分（不能超过100份）
    
    输入文件格式：逗号分隔，第一行带列名：
        (1) label, 0或1，评论的极性
        (2) review, 字符串，评论
        
    输出：
    1. 用于公开的数据文件，1份，再按照`bert_split`分成`run_classifier.py`需要的tsv格式
        1.1 train.tsv
        1.2 dev.tsv
        1.3 test.tsv
    2. 用于黑盒测试的文件包，若干份
    """

    def split1(input_filename, output_filenames, proportion):
        input_data = pd.read_csv(input_filename)
        split_percent = [(sum(proportion[:i + 1]) + 1e-9) / sum(proportion)
                         for i, v in enumerate(proportion)]
        print('split_percent[1]:', [round(b if a == 0 else b - split_percent[a-1], 2)
                                    for a, b in enumerate(split_percent)])
        input_data = input_data.sample(frac=1)
        input_data.reset_index(drop=True)
        out_files = [open(output_filenames.format(i), 'w')
                     for i in range(len(proportion))]
        for index, row in input_data.iterrows():
            r = random.random()
            for i, v in enumerate(split_percent):
                if r <= v:
                    out_files[i].write('{}\t{}\n'.format(
                        row['label'], row['review'].replace('\t', '')))
                    break
        for f in out_files:
            f.close()


    def split2(input_filename, output_path, proportion):
        try:
            os.mkdir(output_path)
        except:
            pass
        split_percent = [(sum(proportion[:i + 1]) + 1e-9) / sum(proportion)
                         for i, v in enumerate(proportion)]
        print('split_percent[2]:', [round(b if a == 0 else b - split_percent[a - 1], 2)
                                    for a, b in enumerate(split_percent)])
        with open(input_filename) as input_file:
            rows = [i.strip('\n').split('\t', 1) for i in input_file]
        out_files = [open('{}{}{}'.format(output_path, os.path.sep, i), 'w')
                     for i in ['train.tsv', 'dev.tsv', 'test.tsv', ]]
        for row in rows:
            r = random.random()
            for i, v in enumerate(split_percent):
                if r <= v:
                    out_files[i].write('{}\t{}\n'.format(
                        row[0], row[1].replace('\t', '')))
                    break
        for f in out_files:
            f.close()


    filename = 'weibo_senti_100k.csv'
    out_filename = 'weibo_senti_100k-{:02d}.csv'
    split_with = [0.001, 0.49, 0.25, 0.25, ]  # list[float], 按照这个比例划分数据，比如：[0.4, 0.15, ]也行
    prepare_on = 0  # 把split_size[prepare_on]的数据分成：训练，开发，测试，剩下的做最终评估
    out_path = 'weibo_senti_100k-{:02d}'.format(prepare_on)  # tsv文件包路径
    bert_split = [0.8, 0.1, 0.1, ]  # list[float], 训练，开发，测试 的比例

    split1(filename, out_filename, split_with)
    split2(out_filename.format(prepare_on), out_path, bert_split)


