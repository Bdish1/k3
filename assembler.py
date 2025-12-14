import sys


class Assembler:
    def __init__(self):
        self.commands = {
            'LOAD_CONST': {'fields': ['A', 'B', 'C']},
            'READ_MEM':   {'fields': ['A', 'B', 'C']},
            'WRITE_MEM':  {'fields': ['A', 'B', 'C', 'D']},
            'POPCNT':     {'fields': ['A', 'B', 'C']}
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
                f"Неверное количество аргументов для {cmd}: ожидалось {expected_args}, получено {len(args)}"
            )

        return {
            'cmd_name': cmd,
            'args': args,
            'fields': cmd_info['fields']
        }

    def format_intermediate(self, cmd):
        opcode_map = {
            'LOAD_CONST': 45,
            'READ_MEM': 31,
            'WRITE_MEM': 34,
            'POPCNT': 14
        }
        opcode = opcode_map[cmd['cmd_name']]
        values = [opcode] + cmd['args']
        field_str = [f"{field}={value}" for field, value in zip(cmd['fields'], values)]
        return f"{cmd['cmd_name']}: {', '.join(field_str)}"

    def parse_only(self, source_file):
        try:
            with open(source_file, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Ошибка: файл '{source_file}' не найден.")
            return False

        intermediate = []
        for line_num, line in enumerate(lines, 1):
            try:
                parsed = self.parse_line(line)
                if parsed:
                    intermediate.append(parsed)
            except Exception as e:
                print(f"Ошибка в строке {line_num}: {e}")
                return False

        print("Промежуточное представление:")
        for cmd in intermediate:
            print(self.format_intermediate(cmd))

        return True


def main():
    if len(sys.argv) != 2:
        print("Использование (только этап 1):")
        print("  python stage1.py <input.asm>")
        return

    source_file = sys.argv[1]
    assembler = Assembler()
    success = assembler.parse_only(source_file)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
