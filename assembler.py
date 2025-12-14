class Assembler:
    def __init__(self):
        self.commands = {
            'LOAD_CONST': {'opcode': 45, 'size': 6, 'fields': ['A', 'B', 'C']},
            'READ_MEM': {'opcode': 31, 'size': 4, 'fields': ['A', 'B', 'C']},
            'WRITE_MEM': {'opcode': 34, 'size': 6, 'fields': ['A', 'B', 'C', 'D']},
            'POPCNT': {'opcode': 14, 'size': 4, 'fields': ['A', 'B', 'C']}
        }

    def parse_line(self, line):
        line = line.strip()
        if not line or line.startswith(';'):
            return None

        parts = line.split()
        if not parts:
            return None

        cmd = parts[0]
        if cmd not in self.commands:
            raise ValueError(f"Неизвестная команда: {cmd}")

        args = [int(arg.strip(',')) for arg in parts[1:]]
        cmd_info = self.commands[cmd]

        expected_args = len(cmd_info['fields']) - 1
        if len(args) != expected_args:
            raise ValueError(
                f"Неверное количество аргументов для {cmd}: ожидалось {expected_args}, получено {len(args)}")

        return {
            'opcode': cmd_info['opcode'],
            'args': args,
            'cmd_name': cmd,
            'size': cmd_info['size'],
            'fields': cmd_info['fields']
        }

    def format_intermediate(self, cmd):
        fields = cmd['fields']
        values = [cmd['opcode']] + cmd['args']
        field_str = [f"{field}={value}" for field, value in zip(fields, values)]
        return f"{cmd['cmd_name']}: {', '.join(field_str)}"

    def encode_instruction(self, cmd):
        opcode = cmd['opcode']
        args = cmd['args']
        size = cmd['size']
        cmd_name = cmd['cmd_name']

        if cmd_name == 'LOAD_CONST':
            B, C = args
            if not (0 <= B < (1 << 12)):
                raise ValueError(f"B (адрес) должен быть 0–{1 << 12 - 1}")
            if not (0 <= C < (1 << 25)):
                raise ValueError(f"C (константа) должен быть 0–{1 << 25 - 1}")

            value = (C << 18) | (B << 6) | opcode
            return value.to_bytes(6, byteorder='little')

        elif cmd_name == 'READ_MEM':
            B, C = args
            if not (0 <= B < (1 << 12)) or not (0 <= C < (1 << 12)):
                raise ValueError("Адреса B и C должны быть 0–4095")

            value = (C << 18) | (B << 6) | opcode
            return value.to_bytes(4, byteorder='little')

        elif cmd_name == 'WRITE_MEM':
            B, C, D = args
            if not (0 <= B < (1 << 12)):
                raise ValueError("B должен быть 0–4095")
            if not (0 <= C < (1 << 13)):
                raise ValueError("C (смещение) должно быть 0–8191")
            if not (0 <= D < (1 << 12)):
                raise ValueError("D должен быть 0–4095")

            value = (D << 31) | (C << 18) | (B << 6) | opcode
            return value.to_bytes(6, byteorder='little')

        elif cmd_name == 'POPCNT':
            B, C = args
            if not (0 <= B < (1 << 12)) or not (0 <= C < (1 << 12)):
                raise ValueError("Адреса B и C должны быть 0–4095")

            value = (C << 18) | (B << 6) | opcode
            return value.to_bytes(4, byteorder='little')

        else:
            raise ValueError(f"Неизвестная команда для кодирования: {cmd_name}")

    def assemble(self, source_file, output_file, test_mode=False):
        with open(source_file, 'r') as f:
            lines = f.readlines()

        intermediate = []
        for line_num, line in enumerate(lines, 1):
            try:
                parsed = self.parse_line(line)
                if parsed:
                    intermediate.append(parsed)
            except Exception as e:
                print(f"Ошибка в строке {line_num}: {e}")
                return None

        if test_mode:
            print("\nПромежуточное представление:")
            for cmd in intermediate:
                print(self.format_intermediate(cmd))

        binary_data = b''
        for cmd in intermediate:
            try:
                encoded = self.encode_instruction(cmd)
                binary_data += encoded
            except Exception as e:
                print(f"Ошибка кодирования команды {cmd['cmd_name']}: {e}")
                return None

        with open(output_file, 'wb') as f:
            f.write(binary_data)

        file_size = len(binary_data)
        print(f"Бинарный файл записан: {output_file} ({file_size} байт)")

        if test_mode:
            print("\nМашинный код в hex:")
            hex_bytes = [f"0x{b:02X}" for b in binary_data]
            print(', '.join(hex_bytes))

            self.run_tests(intermediate, binary_data)

        return intermediate

    def run_tests(self, intermediate, binary_data):
        expected_bytes = [
            bytes([0x6D, 0xBC, 0x60, 0x00, 0x00, 0x00]),  # LOAD_CONST
            bytes([0x5F, 0x44, 0x5C, 0x0E]),  # READ_MEM
            bytes([0x22, 0x2C, 0x44, 0x85, 0xD5, 0x00]),  # WRITE_MEM
        ]

        print("\nЗапуск тестов этапа 3:")

        offset = 0
        passed = True
        test_count = 0

        for i, exp in enumerate(expected_bytes):
            if i >= len(intermediate):
                print(f"Тест {i + 1} не пройден: недостаточно команд в программе")
                passed = False
                break

            if offset + len(exp) > len(binary_data):
                print(f"Тест {i + 1} не пройден: недостаточно данных")
                passed = False
                break

            actual = binary_data[offset:offset + len(exp)]
            cmd_name = intermediate[i]['cmd_name']

            if actual == exp:
                print(f"Тест {i + 1} пройден: {cmd_name}")
                test_count += 1
            else:
                print(f"Тест {i + 1} НЕ пройден!")
                print(f"  Команда: {cmd_name}")
                print(f"  Ожидалось: {[f'0x{b:02X}' for b in exp]}")
                print(f"  Получено : {[f'0x{b:02X}' for b in actual]}")
                passed = False
            offset += len(exp)

        if test_count == len(expected_bytes):
            print(f"\nВсе {test_count} теста этапа 3 пройдены успешно.")
        else:
            print(f"\nПройдено {test_count} из {len(expected_bytes)} тестов.")


class Interpreter:
    def __init__(self):
        self.memory_size = 65536
        self.memory = [0] * self.memory_size
        self.pc = 0

    def decode_instruction(self, instruction_bytes):
        if len(instruction_bytes) == 6:
            value = int.from_bytes(instruction_bytes, byteorder='little')
            opcode = value & 0x3F

            if opcode == 45:
                B = (value >> 6) & 0xFFF
                C = (value >> 18) & 0x1FFFFFF
                return {
                    'cmd_name': 'LOAD_CONST',
                    'opcode': opcode,
                    'args': [B, C],
                    'fields': ['A', 'B', 'C'],
                    'size': 6
                }
            elif opcode == 34:
                B = (value >> 6) & 0xFFF
                C = (value >> 18) & 0x1FFF
                D = (value >> 31) & 0xFFF
                return {
                    'cmd_name': 'WRITE_MEM',
                    'opcode': opcode,
                    'args': [B, C, D],
                    'fields': ['A', 'B', 'C', 'D'],
                    'size': 6
                }

        elif len(instruction_bytes) == 4:
            value = int.from_bytes(instruction_bytes, byteorder='little')
            opcode = value & 0x3F

            if opcode == 31:
                B = (value >> 6) & 0xFFF
                C = (value >> 18) & 0xFFF
                return {
                    'cmd_name': 'READ_MEM',
                    'opcode': opcode,
                    'args': [B, C],
                    'fields': ['A', 'B', 'C'],
                    'size': 4
                }
        return None

    def execute_instruction(self, instruction):
        cmd_name = instruction['cmd_name']
        args = instruction['args']

        if cmd_name == 'LOAD_CONST':
            addr, value = args
            self.memory[addr] = value
            print(f"LOAD_CONST: memory[{addr}] = {value}")

        elif cmd_name == 'READ_MEM':
            src_addr, dst_addr = args
            value = self.memory[src_addr]
            self.memory[dst_addr] = value
            print(f"READ_MEM: memory[{dst_addr}] = memory[{src_addr}] = {value}")

        elif cmd_name == 'WRITE_MEM':
            src_addr, offset, base_addr_ptr = args
            base_addr = self.memory[base_addr_ptr]
            target_addr = base_addr + offset
            value = self.memory[src_addr]
            self.memory[target_addr] = value
            print(f"WRITE_MEM: memory[{target_addr}] = memory[{src_addr}] = {value}")

    def load_program(self, binary_file):
        with open(binary_file, 'rb') as f:
            binary_data = f.read()

        for i, byte in enumerate(binary_data):
            if i < self.memory_size:
                self.memory[i] = byte
            else:
                break
        return len(binary_data)

    def run(self, binary_file, verbose=True):
        program_size = self.load_program(binary_file)

        self.pc = 0
        step = 0
        while self.pc < program_size:
            instruction_bytes = bytes(self.memory[self.pc:self.pc + 6])
            instruction = self.decode_instruction(instruction_bytes)

            if instruction is None:
                instruction_bytes = bytes(self.memory[self.pc:self.pc + 4])
                instruction = self.decode_instruction(instruction_bytes)

            if instruction is None:
                break

            step += 1
            if verbose:
                print(f"[Шаг {step}, PC={self.pc:04X}] ", end="")
            self.execute_instruction(instruction)
            self.pc += instruction['size']
            if step > 1000:
                break

        return step

    def dump_memory(self, output_file, start_addr=0, end_addr=100):
        if end_addr > self.memory_size:
            end_addr = self.memory_size

        memory_dump = {}
        for addr in range(start_addr, end_addr):
            if self.memory[addr] != 0:
                memory_dump[hex(addr)] = self.memory[addr]

        with open(output_file, 'w') as f:
            json.dump(memory_dump, f, indent=2)


def create_test_program():
    test_code = """; Тестовая программа для этапа 3 - копирование массива
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
WRITE_MEM 200, 5, 300 ; memory[1000 + 5] = copy[0] (10)"""

    with open('test_copy.asm', 'w') as f:
        f.write(test_code)

def create_simple_test():
    test_code = """; Простая тестовая программа для этапа 3
LOAD_CONST 0, 12345
READ_MEM 0, 10
LOAD_CONST 20, 1000
WRITE_MEM 10, 5, 20"""

    with open('simple_test.asm', 'w') as f:
        f.write(test_code)


def main():
    if len(sys.argv) < 2:
        print("Использование:")
        print("  1. Ассемблер: python assembler.py <input.asm> <output.bin> [--test]")
        print("  2. Интерпретатор: python assembler.py --run <binary.bin> <memory_dump.json> [start_addr] [end_addr]")
        print("  3. Создать тест: python assembler.py --create-test")
        print("  4. Создать простой тест: python assembler.py --create-simple")
        return

    if sys.argv[1] == '--run':
        if len(sys.argv) < 4:
            print("Использование интерпретатора: python assembler.py --run <binary.bin> <memory_dump.json> [start_addr] [end_addr]")
            return

        binary_file = sys.argv[2]
        dump_file = sys.argv[3]
        start_addr = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        end_addr = int(sys.argv[5]) if len(sys.argv) > 5 else 1100

        interpreter = Interpreter()
        interpreter.run(binary_file, verbose=False)
        interpreter.dump_memory(dump_file, start_addr, end_addr)

    elif sys.argv[1] == '--create-test':
        create_test_program()
    elif sys.argv[1] == '--create-simple':
        create_simple_test()
    else:
        if len(sys.argv) < 3:
            print("Использование ассемблера: python assembler.py <input.asm> <output.bin> [--test]")
            return

        source_file = sys.argv[1]
        output_file = sys.argv[2]
        test_mode = len(sys.argv) > 3 and sys.argv[3] == '--test'

        assembler = Assembler()
        intermediate = assembler.assemble(source_file, output_file, test_mode)

        if intermediate is None:
            sys.exit(1)


if __name__ == "__main__":
    main()
