from enum import Enum
import csv
import json

class IO_MODE(Enum):
    """
        w: creates the file if it does not exist
        r: requires the file to already exist
        a: also creates the file and appends content
    """
    W = "w"
    R = "r"
    A = "a"

class IO:
    def __init__(self, encoding="utf-8") -> None:
        pass
        self.encoding = encoding

    def read_file(self, path):
        with open(path, IO_MODE.R.value, encoding=self.encoding) as f:
            content = f.read()
        return content

    def write_file(
        self, 
        data, 
        path,
        type: IO_MODE
    ):
        with open(path, type.value, encoding=self.encoding) as f:
            f.write(data)

    def read_csv(self, path):
        with open(path, IO_MODE.R.value, encoding=self.encoding) as f:
            reader = csv.reader(f)
            
            rows = []
            for row in reader:
                rows.append(row)

            return rows

    def write_csv(
        self,
        rows,
        path,
        type: IO_MODE
    ):
        with open(path, type.value, newline="", encoding=self.encoding) as f:
            writer = csv.writer(f)

            for row in rows:
                writer.writerow(row)

    def read_csv(self, path):
        with open(path, IO_MODE.R.value, encoding=self.encoding) as f:
            reader = csv.reader(f)
            
            rows = []
            for row in reader:
                rows.append(row)

            return rows

    def write_json(
        self,
        data,
        path,
        type: IO_MODE
    ):
        with open(
            path, 
            type.value, 
            encoding=self.encoding
        ) as f:
            json.dump(
                data, 
                f,
                ensure_ascii=False,
                indent=4
            )

    def read_json(self, path):
        with open(
            path,
            IO_MODE.R.value,
            encoding=self.encoding
        ) as f:
            data = json.load(f)
            
        return data

books_csv = [
    ["uuid", "title", "category"],
    ["1", "Dế Mèn Phiêu Lưu Ký", "Thiếu nhi"],
    ["2", "Lập Trình Python", "Công nghệ"],
    ["3", "Tôi Thấy Hoa Vàng Trên Cỏ Xanh", "Tiểu thuyết"]
]
books_json = [
    {
        "uuid": "1",
        "title": "Dế Mèn Phiêu Lưu Ký",
        "category": "Thiếu nhi"
    },
    {
        "uuid": "2",
        "title": "Lập Trình Python",
        "category": "Công nghệ"
    }
]

io = IO()
print(io.read_file("data/data.txt"))
io.write_file(
    "Hello world IOE ", 
    "data/output.txt", 
    IO_MODE.W
)
io.write_csv(books_csv, "data/books.csv", IO_MODE.W)
print(io.read_csv("data/books.csv"))
io.write_json(books_json, "data/books.json", IO_MODE.W)
print(io.read_json("data/books.json"))