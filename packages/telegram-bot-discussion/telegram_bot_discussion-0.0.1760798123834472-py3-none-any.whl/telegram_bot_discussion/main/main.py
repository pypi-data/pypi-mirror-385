from optparse import OptionParser
from os import path
from shutil import copytree


def main():
    usage = "Params: -n/--new project_path"
    parser = OptionParser(usage=usage)
    parser.add_option(
        "-n",
        "--new",
        dest="new",
        help="new project directory name",
        metavar="FILE",
    )
    (options, _) = parser.parse_args()
    if not options.new:
        print(usage)
        exit(1)
    from_dir = path.join(path.dirname(path.abspath(__file__)), "template_bot")
    to_dir = path.join(path.abspath("./"), str(options.new))
    if path.exists(to_dir):
        print(f"Dir `{to_dir}` already exists")
        exit(1)
    copytree(
        from_dir,
        to_dir,
        False,
    )


if __name__ == "__main__":

    main()
