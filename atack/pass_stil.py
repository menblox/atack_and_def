import re

def give_pass(logs):
    with open(logs, 'r', encoding='utf-8') as input_file, \
        open('all_pass.txt', 'a', encoding='utf-8') as output_file:
        
        text = re.compile(r"password=(\S+)", re.I)

        for line in input_file:
            
            text_1 = text.search(line)

            if text_1:
                text_dic = text_1.group(1)

                output_file.write(f'{text_dic}\n')
            
            else:
                pass
    print("Готово")