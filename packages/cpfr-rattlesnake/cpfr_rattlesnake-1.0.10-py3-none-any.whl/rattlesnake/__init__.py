import jinja2 as jj
import watchdog.events
import watchdog.observers
import time
import argparse
import yaml
import http.server
import os
import os.path
import shutil
import scss
import scss.source
import pathlib
from termcolor import colored
import frontmatter
import markdown
import datetime
from dateutil.parser import parse as parse_date
from email.utils import formatdate
import xml.sax.saxutils
import re

content_block_regex = re.compile("{% block content %}(.*?){% endblock %}", re.MULTILINE | re.DOTALL | re.IGNORECASE)
underscore_dir_regex = re.compile("(.*?)/_(.*?)", re.DOTALL | re.IGNORECASE)


# monkey-patching the bugfix from pyscss
scss.grammar.expression.SassExpressionScanner._patterns = [
        ('"="', '='),
        ('":"', ':'),
        ('","', ','),
        ('SINGLE_STRING_GUTS', "([^'\\\\#]|[\\\\].|#(?![{]))*"),
        ('DOUBLE_STRING_GUTS', '([^"\\\\#]|[\\\\].|#(?![{]))*'),
        ('INTERP_ANYTHING', '([^#]|#(?![{]))*'),
        ('INTERP_NO_VARS', '([^#$]|#(?![{]))*'),
        ('INTERP_NO_PARENS', '([^#()]|#(?![{]))*'),
        ('INTERP_START_URL_HACK', '(?=[#][{])'),
        ('INTERP_START', '#[{]'),
        ('SPACE', '[ \r\t\n]+'),
        ('[ \r\t\n]+', '[ \r\t\n]+'),
        ('LPAR', '\\(|\\['),
        ('RPAR', '\\)|\\]'),
        ('END', '$'),
        ('MUL', '[*]'),
        ('DIV', '/'),
        ('MOD', '(?<=\\s)%'),
        ('ADD', '[+]'),
        ('SUB', '-\\s'),
        ('SIGN', '-(?![a-zA-Z_])'),
        ('AND', '(?<![-\\w])and(?![-\\w])'),
        ('OR', '(?<![-\\w])or(?![-\\w])'),
        ('NOT', '(?<![-\\w])not(?![-\\w])'),
        ('NE', '!='),
        ('INV', '!'),
        ('EQ', '=='),
        ('LE', '<='),
        ('GE', '>='),
        ('LT', '<'),
        ('GT', '>'),
        ('DOTDOTDOT', '[.]{3}'),
        ('SINGLE_QUOTE', "'"),
        ('DOUBLE_QUOTE', '"'),
        ('BAREURL_HEAD_HACK', '((?:[\\\\].|[^#$\'"()\\x00-\\x08\\x0b\\x0e-\\x20\\x7f]|#(?![{]))+)(?=#[{]|\\s*[)])'),
        ('BAREURL', '(?:[\\\\].|[^#$\'"()\\x00-\\x08\\x0b\\x0e-\\x20\\x7f]|#(?![{]))+'),
        ('UNITS', '(?<!\\s)(?:[a-zA-Z]+|%)(?![-\\w])'),
        ('NUM', '(?:\\d+(?:\\.\\d*)?|\\.\\d+)'),
        ('COLOR', '#(?:[a-fA-F0-9]{6}|[a-fA-F0-9]{3})(?![a-fA-F0-9])'),
        ('KWVAR', '\\$[-a-zA-Z0-9_]+(?=\\s*:)'),
        ('SLURPYVAR', '\\$[-a-zA-Z0-9_]+(?=[.][.][.])'),
        ('VAR', '\\$[-a-zA-Z0-9_]+'),
        ('LITERAL_FUNCTION', '(-moz-calc|-webkit-calc|calc|expression|progid:[\\w.]+)(?=[(])'),
        ('ALPHA_FUNCTION', 'alpha(?=[(])'),
        ('OPACITY', '(?i)(opacity)'),
        ('URL_FUNCTION', 'url(?=[(])'),
        ('IF_FUNCTION', 'if(?=[(])'),
        ('FNCT', '[-a-zA-Z_][-a-zA-Z0-9_]*(?=\\()'),
        ('BAREWORD', '(?!\\d)(\\\\[0-9a-fA-F]{1,6}|\\\\.|[-a-zA-Z0-9_])+'),
        ('BANG_IMPORTANT', '!\\s*important'),
        ('INTERP_END', '[}]'),
    ]







def date_to_rfc822(date):
    if not isinstance(date, datetime.datetime) and not isinstance(date, datetime.date):
        date = parse_date(date)
    return formatdate(float(date.strftime("%s")))

def format_date(date, format="%Y-%m-%d"):
    if not isinstance(date, datetime.datetime) and not isinstance(date, datetime.date):
        date = parse_date(date)
    return date.strftime(format)

# available colors: blue, red, green, yellow, blue, magenta, cyan, white

class DictObject:
    def __init__(self, **entries):
        self.__dict__.update(entries)
    
    def __repr__(self):
        return repr(self.__dict__)

    def __getattr__(self, attr):
        if attr in self.__dict__.keys():
            return self.__dict__[attr]

        return None


class TemplateLoader(jj.BaseLoader):
    def __init__(self, path, dependencies, ignore_dependency):
        self.path = path
        self.dependencies = dependencies
        self.ignore_dependency = ignore_dependency

    def get_source(self, environment, template):
        path = os.path.join(self.path, template)
        if not os.path.exists(path):
            raise jj.TemplateNotFound(template, "in " + path)

        # remember the template in the dependency list (for the watchdog)
        if template != self.ignore_dependency:
            self.dependencies.append(template)

        mtime = os.path.getmtime(path)
        source = frontmatter.load(path).content
        return source, path, lambda: mtime == os.path.getmtime(path)


def render_template(path, config, file_path, dependencies):
    env = jj.Environment(
        loader = TemplateLoader(path, dependencies, file_path),
        autoescape = jj.select_autoescape()
    )

    env.filters["xml_escape"] = xml.sax.saxutils.escape
    env.filters["date_to_rfc822"] = date_to_rfc822
    env.filters["format_date"] = format_date

    template = env.get_template(file_path)
    rendered = template.render(**config)
    return rendered

def render_template_from_string(text_content, path, config, file_path, dependencies):
    env = jj.Environment(
        loader = TemplateLoader(path, dependencies, file_path),
        autoescape = jj.select_autoescape()
    )

    env.filters["xml_escape"] = xml.sax.saxutils.escape
    env.filters["date_to_rfc822"] = date_to_rfc822
    env.filters["format_date"] = format_date

    template = env.from_string(text_content)
    rendered = template.render(**config)
    return rendered


def get_target_path(file_path, source_dir, target_dir):
    if file_path.endswith("index.html"):
        return os.path.normpath(os.path.join(target_dir, file_path))
    elif file_path.endswith("index.md"):
        return os.path.normpath(os.path.join(target_dir, file_path))[:-2] + "html"
    elif file_path.endswith("index.markdown"):
        return os.path.normpath(os.path.join(target_dir, file_path))[:-8] + "html"
    elif file_path.endswith(".html"):
        return os.path.join(target_dir, file_path)[:-5] + "/index.html"
    elif file_path.endswith(".md"):
        return os.path.join(target_dir, file_path)[:-3] + "/index.html"
    elif file_path.endswith(".markdown"):
        return os.path.join(target_dir, file_path)[:-9] + "/index.html"
    elif file_path.endswith(".scss"):
        return os.path.join(target_dir, file_path)[:-5] + ".css"

    return os.path.normpath(os.path.join(target_dir, file_path))


def run():
    print("---------------------------------\nRATTLESNAKE STATIC SITE GENERATOR\n---------------------------------\n")
    parser = argparse.ArgumentParser(
        prog = "rattlesnake",
        description = "This tool converts your markdown text and HTML into a static website.",
        epilog = "See https://pac4.gitlab.io/rattlesnake/ for more documentation."
    )
    parser.add_argument("source_dir", default="./src/", nargs="?")
    parser.add_argument("-w", "--watch", action='store_true')
    parser.add_argument("-o", "--output-dir", default="./build/")
    parser.add_argument("-p", "--port", default="8000")
    parser.add_argument("-c", "--config-file", default="config.yml")
    parser.add_argument("-a", "--additional-config", default="")

    args = parser.parse_args()

    config = {}
    if not os.path.isfile(args.config_file):
        print("config file '%s' could not be found!" % args.config_file)
        return

    with open(args.config_file, 'r') as stream:
        config = yaml.safe_load(stream)

    if args.additional_config != "":
        with open(args.additional_config, 'r') as stream:
            additional_config = yaml.safe_load(stream)
            config.update(additional_config)

    # clean output directory
    try:
        shutil.rmtree(args.output_dir)
    except FileNotFoundError:
        pass
    os.mkdir(args.output_dir)

    dependencies = {}
    def collect_file_meta_information(source_path, full_path):
        rel_path = os.path.relpath(full_path, source_path)
        file_path = os.path.basename(full_path)
        if os.path.isfile(full_path) and not file_path.startswith("_"):
                if file_path.lower().endswith(".html") or file_path.lower().endswith(".md") or file_path.lower().endswith(".markdown"):
                    target_path = get_target_path(rel_path, source_path, "/")
                    if target_path.endswith("index.html"):
                        target_path = target_path[:-10]
                    return {
                        "_source_path": rel_path,
                        "_target_path": target_path,
                        **frontmatter.load(full_path).metadata
                    }
        return None


    def process_file(source_path, target_path, full_path, config, process_dependencies):
        rel_path = os.path.relpath(full_path, source_path)
        file_path = os.path.basename(full_path)
        if os.path.isfile(full_path):
            if not file_path.startswith("_"):
                target_file_path = get_target_path(rel_path, source_path, target_path)
                target_path2 = get_target_path(rel_path, source_path, "/")
                if target_path2.endswith("index.html"):
                    target_path2 = target_path2[:-10]

                try:
                    os.makedirs(os.path.dirname(target_file_path))
                except:
                    pass

                additional_template_file_extensions = config["additional_template_file_extensions"] if "additional_template_file_extensions" in config else []

                if file_path.lower().endswith(".html"):
                    dependencies[file_path] = []
                    print(colored("Processing HTML file %s, target is %s" % (file_path, target_file_path), "blue"))
                    metadata = frontmatter.load(full_path).metadata
                    metadata["_source_path"] = rel_path
                    metadata["_target_path"] = target_path2
                    rendered_html = render_template(source_path, {**config, **metadata}, rel_path, dependencies[file_path])
                    with open(target_file_path, "w") as stream:
                        stream.write(rendered_html)
                elif file_path.lower().endswith(".xml"):
                    dependencies[file_path] = []
                    print(colored("Processing XML file %s, target is %s" % (file_path, target_file_path), "blue"))
                    metadata = frontmatter.load(full_path).metadata
                    metadata["_source_path"] = rel_path
                    metadata["_target_path"] = target_path2
                    rendered_xml = render_template(source_path, {**config, **metadata}, rel_path, dependencies[file_path])
                    with open(target_file_path, "w") as stream:
                        stream.write(rendered_xml)
                elif file_path.lower().endswith(".md") or file_path.lower().endswith(".markdown"):
                    dependencies[file_path] = []
                    print(colored("Processing Markdown file %s, target is %s" % (file_path, target_file_path), "blue"))
                    front_matter = frontmatter.load(full_path)
                    metadata = front_matter.metadata
                    metadata["_source_path"] = rel_path
                    metadata["_target_path"] = target_path2
                    rendered_markdown = markdown.markdown(front_matter.content, extensions=['fenced_code'])

                    with open(os.path.join(source_path, front_matter["_template"])) as f:
                        template_text = f.read()
                    template_text = content_block_regex.sub("{% block content %}\n" + rendered_markdown + "\n{% endblock %}", template_text)
                    if "_template" in front_matter.keys():
                        dependencies[rel_path] = [front_matter["_template"]]
                        rendered_html = render_template_from_string(template_text, source_path, {**config, **metadata, "_content": rendered_markdown}, front_matter["_template"], dependencies[file_path])
                    else:
                        print(colored("%s does not have the `_template` variable set" % rel_path, "yellow"))
                        rendered_html = rendered_markdown
                    with open(target_file_path, "w") as stream:
                        stream.write(rendered_html)
                elif file_path.lower().endswith(".scss"):
                    dependencies[file_path] = []
                    print(colored("processing SCSS file: %s" % full_path, "blue"))

                    compiler = scss.Compiler(pathlib.Path(args.source_dir))
                    compilation = compiler.make_compilation()
                    source = scss.source.SourceFile.from_filename(full_path)
                    compilation.add_source(source)
                    rendered_css = compilation.run()
                    
                    # find out which files were imported (for the watchdog)
                    dependencies[rel_path] = [str(src.relpath) for src in compilation.sources if str(src.relpath) != rel_path]
                    with open(target_file_path, "w") as stream:
                        stream.write(rendered_css)
                elif any(file_path.lower().endswith(ext) for ext in additional_template_file_extensions):
                    dependencies[file_path] = []
                    print(colored("Processing file %s, target is %s" % (file_path, target_file_path), "blue"))
                    try:
                        metadata = frontmatter.load(full_path).metadata
                    except e:
                        print(colored("Error while parsing front matter: " + str(e), "red"))
                        metadata = {}
                    metadata["_source_path"] = rel_path
                    metadata["_target_path"] = target_path2
                    rendered_xml = render_template(source_path, {**config, **metadata}, rel_path, dependencies[file_path])
                    with open(target_file_path, "w") as stream:
                        stream.write(rendered_xml)
                else:
                    print(colored("Copying file %s to %s" % (file_path, target_file_path), "blue"))
                    shutil.copy(full_path, target_file_path)
            
            if process_dependencies:
                # check if any of the files has a dependency to the current one
                dependent_files = [key for key, value in dependencies.items() if rel_path in value]
                for dependent_file in dependent_files:
                    process_file(source_path, target_path, os.path.join(source_path, dependent_file), config, process_dependencies)

    
    def is_underscore_directory(dir_path):
        return dir_path.startswith("_") or underscore_dir_regex.match(dir_path) is not None

    # process files
    pages = []
    config["_pages"] = pages
    config["_generation_time"] = datetime.datetime.now()

    for dir_path, sub_dirs, file_paths in os.walk(args.source_dir):
        if is_underscore_directory(dir_path):
            continue
        print("DIR: " + dir_path)

        for file_path in file_paths:
            full_path = os.path.join(dir_path, file_path)
            page_metadata = collect_file_meta_information(args.source_dir, full_path)
            if page_metadata is not None:
                pages.append(DictObject(**page_metadata))

    for dir_path, sub_dirs, file_paths in os.walk(args.source_dir):
        if is_underscore_directory(dir_path):
            continue

        for file_path in file_paths:
            full_path = os.path.join(dir_path, file_path)
            process_file(args.source_dir, args.output_dir, full_path, config, False)

    def delete_empty_dirs(target_dir_path):
        while len(os.listdir(target_dir_path)) == 0:
            print(colored("deleting empty directory " + target_dir_path, "blue"))
            os.rmdir(target_dir_path)
            target_dir_path = os.path.dirname(target_dir_path)

    def process_deletion(path, is_directory):
        rel_path = os.path.relpath(path, args.source_dir)
        if is_directory:
            path_obj = pathlib.Path(rel_path)
            files_to_delete = [f for f in dependencies.keys() if path_obj in pathlib.Path(f).parents]
            for file_to_delete in files_to_delete:
                process_deletion(os.path.join(args.source_dir, file_to_delete), False)
        else:
            file_path = os.path.basename(path)
            if not file_path.startswith("_"):
                target_file_path = get_target_path(rel_path, args.source_dir, args.output_dir)
                print(colored("removing " + target_file_path, "blue"))
                os.remove(target_file_path)
                target_directory_path = os.path.dirname(target_file_path)
                delete_empty_dirs(target_directory_path)
            else:        
                dependent_files = [key for key, value in dependencies.items() if rel_path in value]
                for dependent_file in dependent_files:
                    print(colored("WARNING: Deleted file '%s' was required by '%s'" % (rel_path, dependent_file), "red"))
    if args.watch:
        def on_created(event):
            if event.is_directory:
                return # creating directories is not interesting for us

            print(colored("Watchdog: created %s" % event.src_path, "magenta"))
            process_file(args.source_dir, args.output_dir, event.src_path, config, True)

        def on_deleted(event):
            print(colored("Watchdog: deleted %s" % event.src_path, "magenta"))
            process_deletion(event.src_path, event.is_directory)

        def on_modified(event):
            if event.is_directory:
                return # modifying directories is not interesting for us

            print(colored("Watchdog: modified %s" % event.src_path, "magenta"))
            process_file(args.source_dir, args.output_dir, event.src_path, config, True)

        def on_moved(event):
            if event.is_directory:
                return # individual events will be raised for every single file

            print(colored("Watchdog: moved %s to %s" % (event.src_path, event.dest_path), "magenta"))
            process_deletion(event.src_path, event.is_directory)
            process_file(args.source_dir, args.output_dir, event.dest_path, config, True)

        event_handler = watchdog.events.PatternMatchingEventHandler(
            patterns= None,
            ignore_patterns=None,
            ignore_directories=False, # TODO: what if a directory is renamed?
            case_sensitive=True
        )
        event_handler.on_created = on_created
        event_handler.on_deleted = on_deleted
        event_handler.on_modified = on_modified
        event_handler.on_moved = on_moved

        observer = watchdog.observers.Observer()
        observer.schedule(
            event_handler = event_handler,
            path = args.source_dir,
            recursive = True
        )
        print("start observing '%s'..." % args.source_dir)
        observer.start()

        print("Starting HTTP server on Port %s..." % args.port)
        http_server = http.server.HTTPServer(('', int(args.port)), lambda *_: http.server.SimpleHTTPRequestHandler(*_, directory=args.output_dir))
        http_server.serve_forever()

        print("end observing")
        observer.stop()
        observer.join()

    print("-- done --")

if __name__ == "__main__":
    run()