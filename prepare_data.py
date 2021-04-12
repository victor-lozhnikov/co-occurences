import os
import re
import csv

def prepare_co_occurrences_data(log_file):
    pairs = 0
    tree_files = os.walk('data/co-occurrences')
    co_occurrences_main_dict = {}
    for directory in tree_files:
        for file_name in directory[2]:
            if file_name.startswith('.') or not file_name.endswith('.txt'):
                continue

            """
            if file_name != 'CELLS_PATHWAY.txt' and file_name != 'PATHWAY_PATHWAY.txt':
                continue
            """

            full_file_name = directory[0] + '/' + file_name
            log_file.write(file_name + ' is processed...\n')
            log_file.flush()
            file = open(full_file_name)
            co_occurrences_main_dict[file_name[:-4]] = {}

            for s in file:
                line = s.split()
                co_occurrences_main_dict[line[5] + '_' + line[7]][line[6] + '_' + line[8]] = line[0]
                pairs += 1

    log_file.write(str(pairs) + ' pairs added to co-occurrences map\n')
    log_file.flush()
    # 117'907'628 pairs
    return co_occurrences_main_dict


def prepare_positive_set(co_occurrences_main_dict: dict, log_file):
    file = open('data/corpus.out')

    read_sentence = False
    current_sentence = ""
    current_entities = []

    all_sentences = 0
    normal_sentences = 0

    csv_file = open('sentence_to_co_occurrence_data.csv', 'w', newline='')
    csv_writer = csv.writer(csv_file, delimiter='\t')

    sentence_to_co_occurrence = {}

    for line in file:
        if read_sentence:
            current_sentence = line[1:-1]
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
            split_line = re.split("[ $|\n]", line)[2:]
            if line.endswith("$\n"):
                split_line = split_line[:-2]
            else:
                split_line = split_line[:-1]
            if len(split_line) % 3 != 0:
                log_file.write("Error: ")
                log_file.write(str(split_line) + '\n')
                log_file.flush()
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

            for key, value in sentence_to_co_occurrence.items():
                csv_writer.writerow([key, value])
                # print("write")
            csv_file.flush()
            sentence_to_co_occurrence = {}
            # print(current_entities)

            if all_sentences >= 1000000:
                break

            for i in range(len(current_entities) - 1):
                for j in range(i + 1, len(current_entities)):
                    entity1 = current_entities[i]
                    entity2 = current_entities[j]
                    # print(str(entity1) + '\t\t' + str(entity2))
                    for ii in range(len(entity1[0])):
                        for jj in range(len(entity2[0])):
                            entity11 = entity1[0][ii]
                            entity22 = entity2[0][jj]

                            if entity11[0] == entity22[0] and entity11[1] > entity22[1]:
                                entity11, entity22 = entity22, entity11

                            if entity11[0] > entity22[0]:
                                entity11, entity22 = entity22, entity11

                            # print(str(entity11) + '\t\t' + str(entity22))

                            if entity1[1][0] > entity2[1][0]:
                                entity1, entity2 = entity2, entity1

                            if co_occurrences_main_dict.get(entity11[0] + '_' + entity22[0]) is None:
                                # print("category not found")
                                continue

                            if co_occurrences_main_dict[
                                entity11[0] + '_' + entity22[0]
                            ].get(entity11[1] + '_' + entity22[1]) is None:
                                # print("co-occurrence not found")
                                continue

                            tagged_sentence = ""
                            tagged_sentence += current_sentence[0: entity1[1][0]]
                            """
                            tagged_sentence += "[EntityStart] "
                            tagged_sentence += current_sentence[entity1[1][0]:entity1[1][1]]
                            tagged_sentence += " [EntityEnd]"
                            """
                            tagged_sentence += "ENTITY_MASK"
                            tagged_sentence += current_sentence[entity1[1][1]:entity2[1][0]]
                            """
                            tagged_sentence += "[EntityStart] "
                            tagged_sentence += current_sentence[entity2[1][0]:entity2[1][1]]
                            tagged_sentence += " [EntityEnd]"
                            """
                            tagged_sentence += "ENTITY_MASK"
                            tagged_sentence += current_sentence[entity2[1][1]:]
                            # print(tagged_sentence)

                            co_occurrence = co_occurrences_main_dict[
                                entity11[0] + '_' + entity22[0]][entity11[1] + '_' + entity22[1]]

                            if sentence_to_co_occurrence.get(tagged_sentence) is None:
                                sentence_to_co_occurrence[tagged_sentence] = co_occurrence
                                normal_sentences += 1
                                # log_file.write(str(normal_sentences) + '\n')
                                # log_file.flush()
                            else:
                                sentence_to_co_occurrence[tagged_sentence] = max(
                                    sentence_to_co_occurrence[tagged_sentence],
                                    co_occurrence
                                )

            current_entities = []

        # if line.startswith('}'):
        #     break

    log_file.write("dict created\n")
    log_file.flush()

    csv_file.close()

    log_file.write(str(len(sentence_to_co_occurrence)) + " sentences added\n")
    log_file.flush()
    # all_sentences = 10'742'963
    # normal_sentences = 3'002'238

