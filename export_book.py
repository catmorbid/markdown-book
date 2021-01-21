import os, sys, re
import argparse
import subprocess
import shlex

def sort_list(a_list):
    list_with_indeces = []
    for item in a_list:
        result = re.findall(r'\d+', item)
        if result:
            index = int(result[0])
        else:
            index = 999

        # print(result, item, index)

        list_with_indeces.append([item, index])
    list_with_indeces.sort(key=lambda x: x[1])  # sort by index

    sorted_list = []
    for item in list_with_indeces:
        sorted_list.append(item[0])
    return sorted_list


# get chapters first if they exist as directories
# then Scenes, or just Chapters if they are md files.
def get_list_of_files(path, extension, chapter_folders=False):
    sorted_markdown_list = []
    if chapter_folders:
        chapters_list = [item for item in os.listdir(path) if os.path.isdir(os.path.join(path, item))]
        chapters_list = sort_list(chapters_list)

        for chapter in chapters_list:
            chapter_markdown_files = []
            all_files = os.listdir(path + "/" + chapter)
            for a_file in all_files:
                if a_file.endswith("." + extension):
                    # path + "/" + chapter + "/" + 
                    chapter_markdown_files.append(a_file)
            chapter_markdown_files = sort_list(chapter_markdown_files)
            for index in range(len(chapter_markdown_files)):
                current_path = chapter_markdown_files[index]
                chapter_markdown_files[index] = path + "/" + chapter + "/" + current_path
            sorted_markdown_list.extend(chapter_markdown_files)
    else:
        # process only MD files make sure they are numbered
        all_files = os.listdir(path)
        for a_file in all_files:
            if a_file.endswith("." + extension):
                sorted_markdown_list.append(a_file)
        sorted_markdown_list = sort_list(sorted_markdown_list)
        for index in range(len(sorted_markdown_list)):
            current_path = sorted_markdown_list[index]
            sorted_markdown_list[index] = path + "/" + current_path

    return sorted_markdown_list


# get all files from root path recursively, by looking at each sub-directory.
def get_list_of_files_recursively(path, extension):
    sorted_markdown_list = []
    sorted_items = sort_list(os.listdir(path))
    for item in sorted_items:
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            sorted_markdown_list.extend(get_list_of_files_recursively(item_path, extension))
        else:
            if item.endswith("." + extension):
                sorted_markdown_list.append(item_path)

    return sorted_markdown_list


def export_dir_to_format(path):
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--root-path', help='Root path for book files', required=True)
    # parser.add_argument('-c', '--using-chapter-folders',
    #                     help='Are you using folders for chapters?', default=False, action='store_true')
    parser.add_argument('-f', '--file-extension', default='md')
    # parser.add_argument('-r', '--recursive', default=True, action='store_true')
    parser.add_argument('-t', '--convert-to', default='pdf', help='supported: pdf, icml')
    parser.add_argument('-o', '--output', help='output file and path')
    args = parser.parse_args()

    # if args.recursive:
    #     file_list = get_list_of_files_recursively(args.root_path, args.file_extension)
    # else:
    #     file_list = get_list_of_files(args.root_path, args.file_extension, args.using_chapter_folders)

    file_list = get_list_of_files_recursively(args.root_path, args.file_extension)

    if not file_list:
        print("No markdown files found, if you\'re using folder chapters use -c, else do not use -c")
        print("Exiting...")
        exit()

    for file in file_list:
        print(file)

    if args.root_path[-1] != '/' or args.root_path[-1] != '\\':
        args.root_path = args.root_path + '/'

    if not args.output:
        args.output = args.root_path + 'book.' + args.convert_to

    # if args.convert_to == 'pdf':
    #     default_pandoc_cmd = "pandoc --pdf-engine=xelatex --toc " \
    #                          "-V colorlinks " \
    #                          "-V urlcolor=NavyBlue " \
    #                          "-V geometry:\"top=2cm, bottom=1.5cm, left=2cm, right=2cm\" "\
    #                          "-t pdf " \
    #                          "-o "+ args.output + " " + args.root_path + "title.txt "
    # elif args.convert_to == 'icml':
    #     default_pandoc_cmd = "pandoc -s -f markdown -t icml -o " + args.output + " " + args.root_path + "title.txt "

    if args.convert_to == 'pdf':
        proc_args = ["pandoc",
                     "--standalone",
                     "--pdf-engine=xelatex",
                     "--toc",
                     "--data-dir=pandoc_data",
                     "--template=eisvogel",
                     "-V table-use-row-colors",
                     "-V book",
                     "-V fontsize:10",
                     "--top-level-division=chapter",
                     "-V classoption=oneside",
                     # "-V colorlinks",
                     # "-V urlcolor=NavyBlue",
                     "-V geometry:\"top=3cm, bottom=3cm, left=1cm, right=1cm\"",
                      "-V mainfont:\"Palatino Linotype\"",
                     "-t pdf",
                     "-o " + args.output,
                     ]
    elif args.convert_to == 'icml':
        proc_args = ["pandoc",
                     "--standalone",
                     "-f markdown",
                     "-t icml",
                     "-o " + args.output,
                     ]


    proc_args.extend(file_list)

    print (" ".join(proc_args))
    subprocess.run(" ".join(proc_args))



if __name__ == "__main__":
    main()
