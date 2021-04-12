read_file = open('sentence_to_co_occurrence_data.csv', 'r', newline='')
write_file = open('little_data.csv', 'w', newline='')
i = 0
for line in read_file:
    write_file.write(line)
    i += 1
    if i == 1000000:
        break
