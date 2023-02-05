import os
import shutil

dir = os.path.dirname(__file__)

input_dir = os.path.join(dir, "blog")
output_dir = os.path.join(dir, "pdf")
work_dir = os.path.join(dir, "tmp_md2pdf_work_dir")

os.system("docker pull lwabish/mdout:chinese")

class Table:
    levels = {
        "# ": 1,
        "## ": 2,
        "### ": 3,
        "#### ": 4,
        "##### ": 5,
        "###### ": 6
    }

    def __init__(self, row: str):
        self.is_table = False
        for key, val in self.levels.items():
            if row.startswith(key):
                self.level = val
                self.content = row.removeprefix(key)
                self.is_table = True
                break


    def toString(self):
        str = ""
        for i in range(self.level - 1):
            str += "\t"
        str += "- [{}](#{})".format(self.content, self.content.replace(" ", "-"))
        return str


def my_copy(path1, path2):
    if os.path.isfile(path1):
        shutil.copyfile(path1, path2)
        print('文件复制成功')
    elif os.path.isdir(path1):
        shutil.copytree(path1, path2)
        print('目录复制成功')
    return


def rmtree(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)


def gen_table(file):
    with open(os.path.join(work_dir, file), 'r', encoding='utf-8') as f:
        data = str(f.read())
    data = data.replace("[toc]", "")
    data = data.replace("[TOC]", "")
    data = data.replace(".md)", ".pdf)")
    table_content = ""
    code_block = 0
    for line in data.splitlines():
        if line.startswith("```"):
            if code_block == 0:
                code_block = code_block + 1
            else:
                code_block = code_block - 1

        if code_block > 0:
            continue

        table = Table(line)
        if table.is_table:
            table_content += (table.toString() + "\n")

    data = table_content + "\n" + data

    with open(os.path.join(work_dir, file), 'w', encoding='utf-8') as f:
        f.write(data)


def work(file):
    print("开始转换 " + file)
    print("生成目录中...")
    gen_table(file)
    work_file = "".join(file.split())
    os.rename(os.path.join(work_dir, file), os.path.join(work_dir, work_file))
    cmd = "docker run --rm -v {}:/data lwabish/mdout:chinese {}".format(work_dir, work_file)
    print(os.popen(cmd).read())
    os.rename(os.path.join(work_dir, work_file), os.path.join(work_dir, file))
    os.rename(os.path.join(work_dir, work_file.replace(".md", ".pdf")),
              os.path.join(work_dir, file.replace(".md", ".pdf")))
    my_copy(os.path.join(work_dir, file.replace(".md", ".pdf")), os.path.join(output_dir, file.replace(".md", ".pdf")))


if __name__ == '__main__':
    rmtree(work_dir)
    rmtree(output_dir)

    os.mkdir(output_dir)
    my_copy(input_dir, work_dir)
    for f in os.listdir(work_dir):
        if f.endswith('.md'):
            work(f)

    rmtree(work_dir)
