import prepare_data

log_file = open('log.txt', 'w')
co_occurrences_main_dict = prepare_data.prepare_co_occurrences_data(log_file)
prepare_data.prepare_positive_set(co_occurrences_main_dict, log_file)
log_file.close()
# print("ready")
