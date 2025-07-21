import os, curses, datetime
from functools import partial

cls = lambda: os.system('clear')
comm = None
name_list_file = 'books.txt'
name_deadline_file = 'days.txt'
separator = ' # '
tmp = None
tmpUser = None
booksF = None
daysF = None
state = 'hi'
pageDel = 0
booksL = []

def close_program():
    if state == 'exit':
        os._exit(0)
    else:
        daysF.close()
        booksF.close()
        os._exit(0)

def expect_user_input(my_term, lines=[]):
    global state
    curses.noecho()
    my_term.clear()
    max_y = my_term.getmaxyx()[0]
    if state == 'hi':
        my_term.addstr(0, 0, '###############')
        my_term.addstr(1, 0, 'В этой программе ты можешь рассчитать количество страниц в день,')
        my_term.addstr(2, 0, 'чтобы успеть вовремя прочитать весь нужный список литературы')
        my_term.addstr(3, 0, 'Нажмите enter, чтобы продолжить.')
        my_term.addstr(4, 0, 'Или q - закрыть программу.')
        my_term.addstr(5, 0, '...')
        while True:
            key = my_term.getch()
            if key == ord('q'):
                state = 'exit'
                break
            elif key == 10 or key == 13:
                break
    elif state == 'bye':
        for i in range(len(lines)):
            my_term.addstr(i, 0, lines[i])
        my_term.addstr(len(lines), 0, '\n\nНажмите enter для выхода из программы.\n')
        while True:
            key = my_term.getch()
            if key == 10 or key == 13:
                break
    elif state == 'showing buffer':
        if lines != None and max_y < len(lines):
            start_line = len(lines) - max_y + 2
        else:
            start_line = 0
        while True:
            try:
                my_term.clear()
                for i in range(start_line, min(start_line + max_y - 4, len(lines))):
                    my_term.addstr(i - start_line, 0, lines[i])
                my_term.addstr(max_y - 2, 0, 'Выше выведено содержимое буфера.')
                my_term.addstr(max_y - 1, 0, 'Нажмите enter, чтобы вернуться обратно в меню.')
                my_term.refresh()
            except TypeError:
                my_term.addstr(0, 0, 'Буфер пуст. Нажмите enter, чтобы вернуться обратно в меню.\n')

            key = my_term.getch()
            if key == 10 or key == 13:
                break
            elif key == curses.KEY_DOWN:
                if start_line + max_y - 4 < len(lines):
                    start_line += 1
            elif key == curses.KEY_UP:
                if start_line > 0:
                    start_line -= 1

curses.wrapper(expect_user_input)
if state == 'exit':
    close_program()
else:
    state = 'main'

def print_list(fileL):
    global booksL
    fileL.seek(0)
    booksL = fileL.readlines()
    for i in range(len(booksL)):
        print(f'{i + 1} - {booksL[i][:-1:].replace(separator, ' - ')}')

def fill_in_the_list(fileL, isEmpty=False):
    global comm, tmpUser
    if isEmpty:
        fileL.seek(0, 0)
    else:
        fileL.seek(0, 2)
    print(f'\nВводите ниже через "{separator}" название произведения и количество страниц в нём.')
    print('Когда закончите запись произведений, введите "STOP!"\n')
    if tmpUser != None:
        print('Буфер не пуст! Вы можете прописать "paste!", чтобы список от туда был записан в файл.')
        print('После вставки можно ещё дописывать произведения и закончить с этим такой же командой "STOP!"')
    while True:
        comm = input().split(separator)
        if comm[0] == 'paste!':
            fileL.writelines(tmpUser)
        elif comm[0] != 'STOP!':
            if len(comm) < 2 or len(comm) > 2 or not comm[1].isdigit():
                print('\nНеверный ввод! Сделай как надо.\n')
            else:
                fileL.write(f'{comm[0]}{separator}{comm[1]}\n')
        else:
            break

def remove_books(fileL):
    global comm, booksL
    print_list(booksF)
    print('\n\nВведите диапазон книг, которые нужно убрать из списка:' \
    '\nчерез пробел введи индекс первой и последней книг,' \
    ' в диапазоне которых нужно убрать книги.')

    while True:
        try:
            comm = [int(i) for i in input().split()]
            if 2 > len(comm) > 2:
                print('Неверный ввод!\n')
            else:
                isNice = True
                for i in comm:
                    if (i < 1 and i != 0) or i > len(booksL):
                       print('Неверный ввод!\n') 
                       isNice = False
                       break
                if isNice:
                    break
        except ValueError:
            print('Вводи цифры!\n')
    
    if comm != [0, 0]:
        for i in range(comm[1] - comm[0] + 1):
            booksL.pop(comm[0] - 1)
            if comm[0] == comm[1]:
                break
        fileL.seek(0, 0)
        fileL.writelines(booksL)
        fileL.truncate()

def change_read_pages():
    global pageDel, comm
    print('\n\nВведите количество страниц, которые нужно убрать из общей суммы')
    while True:
        try:
            comm = int(input())
            pageDel = comm
            break
        except ValueError:
            print('\nВводи цифры!\n')

def specify_deadline():
    global comm, tmp
    while True:
        print('Нужно ввести дату начала чтения. По умолчанию устанавливается сегодняшний день.')
        print('Вводить нужно по следующему шаблону:')
        print('\nдень:месяц:год\n')
        print('Год нужно указывать в четырёхзначном виде.')
        print('Для установки сегодняшнего дня начальной датой достаточно нажать на enter.\n\n')
        comm = input().split(':')
        if len(comm) == 3:
            isNice = True
            for i in range(3):
                if not comm[i].isdigit():
                    isNice = False
                    break
                else:
                    if i < 2 and (len(comm[i]) < 2 or len(comm[i]) > 2):
                        isNice = False
                        break
                    elif i == 2 and (len(comm[i]) < 4 or len(comm[i]) < 4):
                        isNice - False
                        break
            if isNice:
                tmp = ':'.join(comm)
                break
        elif comm[0] == '':
            tmp = datetime.date.today().strftime('%d:%m:%Y')
            print(tmp)
            break

        cls()
        print('Некорректный ввод!\n\n')
    cls()
    while True:
        print('Теперь нужно ввести дату окончания чтения (этот день входит в период чтения).')
        print('Вводить нужно по следующему шаблону:')
        print('\nдень:месяц:год\n')
        print('Год нужно указывать в четырёхзначном виде.\n\n')
        comm = input().split(':')
        if len(comm) == 3:
            isNice = True
            for i in range(3):
                if not comm[i].isdigit():
                    isNice = False
                    break
                else:
                    if i < 2 and (len(comm[i]) < 2 or len(comm[i]) > 2):
                        isNice = False
                        break
                    elif i == 2 and (len(comm[i]) < 4 or len(comm[i]) < 4):
                        isNice - False
                        break
            if isNice:
                return [(tmp + '\n'), (':'.join(comm) + '\n')]
        cls()
        print('Некорректный ввод!\n\n')

cls()
if not os.path.exists(name_list_file):
    open(name_list_file, 'w', encoding='utf-8').close()
    print('Создан новый файл, в котором будет список литературы')
booksF = open(name_list_file, 'r+')
tmp = booksF.read(1)

if tmp == '':
    print('Список пуст. Сейчас будем заполнять его.')
    fill_in_the_list(booksF, True)
    cls()

is_there_err = False
while True:
    print_list(booksF)
    if tmpUser != None:
        print('\n\nБуфер не пуст!')
    booksF.seek(0, 0)
    tmp = booksF.read(1)
    if tmp == '':
        print('\n\nСписок пуст.')
    else:
        print('\n\nСписок имеется.')
    print('Выберите действие:\n')
    print('1 - Продолжить...')
    print('2 - Дополнить список')
    print('3 - Удалить произведения из списка')
    print('4 - Убрать прочитанные страницы из итогового расчёта')
    print('5 - Скопировать текущий список в буфер')
    print('6 - Показать буфер\n')
    if is_there_err:
        print('Неверно введен номер команды!\n')
    comm = input()
    if comm.isdigit() and 0 < int(comm) < 7:
        comm = int(comm)
        cls()
        if comm == 2:
            fill_in_the_list(booksF)
        elif comm == 3:
            remove_books(booksF)
        elif comm == 4:
            change_read_pages()
        elif comm == 5:
            tmpUser = booksL
        elif comm == 6:
            state = 'showing buffer'
            curses.wrapper(partial(expect_user_input, lines=tmpUser))
            state = 'main'
        else:
            is_there_err = False
            break
        is_there_err = False
    else:
        is_there_err = True
    cls()
        

if not os.path.exists(name_deadline_file):
    open(name_deadline_file, 'w', encoding='utf-8').close()
daysF = open(name_deadline_file, 'r+')
if daysF.read(1) == '':
    print('Не указан срок прочтения.\n\n')
    daysF.seek(0, 0)
    daysF.writelines(specify_deadline())
    daysF.truncate()

while True:
    cls()
    print('Даты указаны. Выберите действие:\n')
    print('1 - Сделать вычисление')
    print('2 - Изменить даты')
    comm = input()
    if comm.isdigit() and 0 < int(comm) < 3:
        comm = int(comm)
        cls()
        if comm == 2:
            daysF.seek(0, 0)
            daysF.writelines(specify_deadline())
            daysF.truncate()
        else:
            break
    elif comm != '':
        cls()
        print('Неверно введён номер команды.')

daysF.seek(0)
tmp = daysF.readlines()
start_day = datetime.datetime.strptime(tmp[0][:-1:], '%d:%m:%Y')
end_date = datetime.datetime.strptime(tmp[1][:-1:], '%d:%m:%Y')
remaining_days = (end_date - start_day).days + 1
all_pages = 0
tmp = len(booksL)
for book in booksL:
    try:
        all_pages += int(book.split(separator)[1])
    except (IndexError, ValueError):
        print('У вас повреждён файл списка.\n' \
            'Необходимо его очистить и в программе его снова заполнить.')
        close_program()

all_pages = max(0, all_pages - pageDel)
cls()
lines = [f'Осталось книг: {tmp}',
    f'Осталось страниц: {all_pages}',
    f'Осталось дней до конца срока прочтения: {remaining_days}', '',
    f'Норматив: {all_pages / remaining_days}']
state = 'bye'
curses.wrapper(partial(expect_user_input, lines=lines))

close_program()

#this program isn't finished