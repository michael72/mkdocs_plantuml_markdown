import base64
from pathlib import Path
import string
import zlib

import httplib2
from mkdocs.config import config_options
from mkdocs.config.base import Config
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page

import logging as log

# helper functions to URL encode the UML image
plantuml_alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase + '-_'
base64_alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits + '+/'
b64_to_plantuml = bytes.maketrans(base64_alphabet.encode('utf-8'), plantuml_alphabet.encode('utf-8'))


class PlantUmlMarkdown(BasePlugin):
    """
    Helper plugin to search the markdown file for ```plantuml``` markers and replace the content with
    a link to the actual generated plantuml output.
    """

    config_scheme = (
                ('server', config_options.Type(str, default="http://localhost")),
                ('server_port', config_options.Type(int, default=8080)),
                # actual image output type used for the html rendering. Default is SVG.
                ('image_type', config_options.Type(str, default="svg"))
        )

    def __init__(self):
        self.http = httplib2.Http({})
        self.current_page : Page = None
        self.current_files : Files = None
        self.current_config : Config = None
        self.temp_dir = 'tmp'
        
    def on_page_markdown(self, markdown: str, page: Page, config: Config, files: Files) -> str:
        """ Called by the framework. 
        Input: markdown page as read in the src directory. 
        Output: markdown page that is saved to the output directory with plantuml diagrams replaced by image links."""
        self.current_page, self.current_files, self.current_config = page, files, config
        return self._replace_plantuml(markdown, page.file)
    
    def _replace_plantuml(self, markdown: str, file: File) -> str:
        """ Replace ```plantuml``` sections with links to rendered content """
        segments = markdown.split("```plantuml")
        if len(segments) > 1:
            for idx, content in enumerate(segments[1:], 1):
                idx_end = content.find('```')
                uml = content[:idx_end].strip().replace("\r\n", "\n")
                link = self._create_doc_link(uml, file, idx)
                segments[idx] = link + '\n' + content[idx_end + 3:]  # remove triple ```
            return "".join(segments)
        return markdown
    
    def _create_doc_link(self, uml: str, file: File, idx: int) -> str:
        """ Creates a link ![title](outputfilename) and generates the output file""" 
        out_file = self._get_out_file(file, idx)
        self._write_outfile(uml, out_file)
        ref = self._get_reference(uml, out_file)
        return f"![{ref}](./{out_file.name})"
    
    def _get_out_file(self, file: File, idx: int) -> Path:
        """ Returns the filename of the created diagram output file """
        image_type = self.config['image_type']
        md_file = Path(file.abs_dest_path)
        out_dir = md_file.parent / self.temp_dir 
        if not out_dir.exists():
            out_dir.mkdir()
        out_file = out_dir / f"{md_file.stem}_{idx}.{image_type}"
        return out_file
    
    def _get_reference(self, uml: str, out_file: Path) -> str:
        """ In the created link this is the name of the diagram used in the [].
        This is either the title after the @startuml or the title that is set within the diagram.
        E.g.
        @startuml diagram-title
        title other title
        """
        startuml = "@startuml"
        if uml.startswith(startuml):
            first_line = uml[:uml.find("\n")+1].strip()
            title = first_line[:first_line.find(" ")+1].strip()
            if len(title) > len(startuml):
                return first_line[len(startuml)+1:].strip()
        idx = uml.find('title')
        if idx == 0 or idx > 1 and uml[idx - 1] == '\n':
            return uml[idx: uml.find('\n')].strip()
        return out_file.stem
    
    def _write_outfile(self, uml: str, out_file: Path):
        """ Creates the diagram output file given the UML content and the output file name."""
        output = self._convert_diagram(uml)
        if len(output):
            with open(out_file, 'bw+') as out:
                out.write(output)
                self._append_file(out_file)
        
    def _append_file(self, file: Path):
        """ Appends the file to the known files. 
        Internally this leads to the svg file being copied from the tmp-output directory to the output directory."""
        dir_len = len(str(self.current_page.file.src_path))
        dest_dir = self.current_page.file.abs_dest_path[:-dir_len - 2]  # md -> html
        src_dir = Path(dest_dir) / self.temp_dir
        path = Path(self.current_page.file.src_path).with_name(file.name)
        
        self.current_files.append(File(path=str(path), src_dir=str(src_dir), dest_dir=dest_dir, use_directory_urls=False))
        
    def _convert_diagram(self, uml: str) -> bytes:
        """ Converts the diagram to the actual html linked content by calling the plantuml server."""
        url = self._get_url(self._zip_diagram(uml))
        result = bytes()
        try:
            response, content = self.http.request(url)
            if response.reason == "OK":
                result = content
            else:
                log.error("Got %s response %d for '%s'", response.reason, response.status, url)
        except:
            log.error("Server error while processing '%s'", url)
        return result
        
    def _zip_diagram(self, uml: str) -> str:
        """ Gets the compressed UML diagram needed that is called with the plantuml server.
        """
        try:
            compressed = zlib.compress(uml.encode('utf-8'))[2:-4]
            return base64.b64encode(compressed).translate(b64_to_plantuml).decode('utf-8')
        except:
            log.error("failed to encode '%s'", uml)
            return ""

    def _get_url(self, zipped: str):
        """ The plantuml server URL to call """
        return f"{self.config['server']}:{self.config['server_port']}/plantuml/{self.config['image_type']}/{zipped}"

