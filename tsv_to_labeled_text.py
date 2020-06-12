import os
import csv
import sys
import random
# input_filename:
# text, label_1, label_2, label_3, ...
# xxxx, 0,       1,       2,
# yyyy, 0,       1,       0,
# output_path:
# file in label_1.txt
# N, xxxx
# N, yyyy
# file in label_2.txt
# Y, xxxx
# Y, yyyy
# file in label_3.txt
# Y, xxxx
# N, yyyy
def main(*, input_filename='', output_path='',
         max_seq_len=500,
         train_rate=0.8, test_rate=0.1, dev_rate=0.1,
         max_rows=0,
         delimiter='\t', quotechar='"'):

    one = test_rate + train_rate + dev_rate
    test_count, dev_count = int(test_rate / one * 10000), int(dev_rate / one * 10000)

    sample_ids = [0] * (10000 - test_count - dev_count) + [1] * test_count + [2] * dev_count

    with open(input_filename) as input_file:
        rows = [row for row in csv.reader(input_file, delimiter=delimiter, quotechar=quotechar)]
        label_list = rows[0][1:]
        out_files = {}
        for label in label_list:
            test_filename, train_filename, dev_filename = [os.path.sep.join([output_path, label, i]) for i in ['test.tsv', 'train.tsv', 'dev.tsv', ]]
            if not os.path.exists(os.path.sep.join([output_path, label])):
                os.mkdir(os.path.sep.join([output_path, label]))
            out_files[label] = [open(train_filename, 'w'), open(test_filename, 'w'), open(dev_filename, 'w')]

        label_count = {}

        row_count = 0

        label_id_dict = {'Y': 0, 'N':1, }

        for row_id in range(1, len(rows)):

            if row_id > max_rows > 0:
                break
            row_count += 1

            row = rows[row_id]
            text = row[0]

            for label_id in range(1, len(rows[0])):
                label = rows[0][label_id]

                if label not in label_count:
                    label_count[label] = [[0, 0, 0, ], [0, 0, 0, ]]
                    # [ [Y_in_train, Y_in_test, Y_in_dev], [N_in_train, N_in_test, N_in_dev] ]

                dest_no = random.choice(sample_ids)

                if row[label_id] != '0': # 非零都是True
                    out_label = 'Y'
                else:
                    out_label = 'N'

                if out_label:
                    label_count[label][label_id_dict[out_label]][dest_no] += 1
                    for text in [row[0][i:i+max_seq_len] for i in range(0, len(row[0]), max_seq_len)]:
                        out_files[label][dest_no].write('{}\t{}\n'.format(out_label, text.replace('\n', '||||')))

    for out_file in [f for l in label_list for f in out_files[l]]:
        out_file.close()

    with open(os.path.sep.join([output_path, 'labeled_text_data_split_count.txt']), 'w') as out:
        out.write('row_count: {}\n'.format(row_count))
        out.write('label_name: Y_in_train / N_in_train, Y_in_test / N_in_test, Y_in_dev / N_in_dev; [Y_sum / N_sum]\n')
        label_count_sorted = sorted([(k, v) for k, v in label_count.items()], key=lambda x: sum(x[1][0]), reverse=True)
        for label, data in label_count_sorted:
            out.write('\t{}: {}/{}, {}/{}, {}/{}; [{}/{}]\n'.format(label,
                                 label_count[label][0][0],
                                 label_count[label][1][0],
                                 label_count[label][0][1],
                                 label_count[label][1][1],
                                 label_count[label][0][2],
                                 label_count[label][1][2],
                                 sum(label_count[label][0]),sum(label_count[label][1])))

if __name__ == '__main__':
    main(input_filename=sys.argv[1], output_path=sys.argv[2],
         max_rows=int(sys.argv[3]))