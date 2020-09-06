import os
import re


def prepare_data():
    prepare_co_occurrences_data()


def prepare_co_occurrences_data():
    pairs = 0
    tree_files = os.walk('data/co-occurrences')
    co_occurrences_main_dict = {}
    for directory in tree_files:
        for file_name in directory[2]:
            if file_name.startswith('.') or not file_name.endswith('.txt'):
                continue
            full_file_name = directory[0] + '/' + file_name
            print(file_name + ' is processed...')
            file = open(full_file_name)
            co_occurrences_main_dict[file_name[:-4]] = {}

            for s in file:
                line = s.split()
                co_occurrences_main_dict[line[5] + '_' + line[7]][line[6] + '_' + line[8]] = line[0]
                pairs += 1

    print('\n' + str(pairs) + ' pairs added to co-occurrences map')
    # 117'907'628 pairs
    return co_occurrences_main_dict


def prepare_positive_set(co_occurrences_main_dict):
    file = open('data/positive_set.txt')

    read_sentence = False
    current_sentence = ""
    current_entities = []

    all_sentences = 0
    normal_sentences = 0

    x_train = []
    y_train = []

    for line in file:
        if read_sentence:
            current_sentence = line[1:]
            read_sentence = False
        if line.startswith("Sentence:"):
            read_sentence = True
        if line.startswith("Position:"):
            split_line = line.split(" ")
            current_entities[len(current_entities) - 1].append(
                [int(split_line[1]), int(split_line[2])]
            )
            # print(current_sentence[int(split_line[1]):int(split_line[2])])
        if line.startswith("From dictionary:"):
            split_line = re.split("[ $|]", line)[2:-1]
            if len(split_line) % 3 != 0:
                print("Error:")
                print(split_line)
                break
            current_entities.append([[]])
            for i in range(len(split_line) // 3):
                current_entities[len(current_entities) - 1][0].append(
                    [split_line[i * 3 + 1], split_line[i * 3 + 2]]
                )
            # print(split_line)
        if line.startswith("<>"):
            all_sentences += 1
            if len(current_entities) == 1:
                current_entities = []
                continue
            normal_sentences += 1
            # print(current_entities)

            for i in range(len(current_entities) - 1):
                for j in range(i + 1, len(current_entities)):
                    entity1 = current_entities[i]
                    entity2 = current_entities[j]
                    print(str(entity1) + '\t\t' + str(entity2))
                    for ii in range(len(entity1[0])):
                        for jj in range(len(entity2[0])):
                            entity11 = entity1[0][ii]
                            entity22 = entity2[0][jj]
                            if entity11[0] > entity22[0]:
                                entity11, entity22 = entity22, entity11
                                entity1, entity2 = entity2, entity1

                            print(str(entity11) + '\t\t' + str(entity22))
                            # co_occurrence = co_occurrences_main_dict[
                            #     entity11[0] + '_' + entity22[0]][entity11[1] + '_' + entity22[1]]

            current_entities = []
        if line.startswith('}'):
            break
    print(all_sentences)
    print(normal_sentences)
    # all_sentences = 10'742'963
    # normal_sentences = 3'002'238
