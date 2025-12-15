# Ассемблирование с выводом промежуточного представления и hex-дампа
python assembler.py test_program.asm output.bin --test

# Формат команд в исходном файле (пример):
; LOAD_CONST: opcode: 45, аргументов: 2
; READ_MEM:   opcode: 31, аргументов: 2
; WRITE_MEM:  opcode: 34, аргументов: 3
; POPCNT:     opcode: 14, аргументов: 2

LOAD_CONST 100, 12345
READ_MEM 100, 200
WRITE_MEM 200, 5, 300
POPCNT 200, 400

# Запуск интерпретатора
python assembler.py --run output.bin memory_dump.json

# Генерация тестовых программ
python assembler.py --create-test      # → test_copy.asm
python assembler.py --create-simple    # → simple_test.asm
