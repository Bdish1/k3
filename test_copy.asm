; Тестовая программа для этапа 3 - копирование массива
; Исходный массив: адреса 100-104
; Целевой массив: адреса 200-204

; 1. Инициализация исходного массива
LOAD_CONST 100, 10    ; array[0] = 10
LOAD_CONST 101, 20    ; array[1] = 20
LOAD_CONST 102, 30    ; array[2] = 30
LOAD_CONST 103, 40    ; array[3] = 40
LOAD_CONST 104, 50    ; array[4] = 50

; 2. Копирование через READ_MEM
READ_MEM 100, 200     ; copy[0] = array[0]
READ_MEM 101, 201     ; copy[1] = array[1]
READ_MEM 102, 202     ; copy[2] = array[2]
READ_MEM 103, 203     ; copy[3] = array[3]
READ_MEM 104, 204     ; copy[4] = array[4]

; 3. Дополнительный тест WRITE_MEM
LOAD_CONST 300, 1000  ; base = 1000
WRITE_MEM 200, 5, 300 ; memory[1000 + 5] = copy[0] (10)