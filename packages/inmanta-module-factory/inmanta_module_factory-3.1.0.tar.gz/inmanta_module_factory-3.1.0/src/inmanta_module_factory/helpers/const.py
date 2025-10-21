"""
Copyright 2021 Inmanta

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Contact: code@inmanta.com
Author: Inmanta
"""

import inmanta.ast.type
import inmanta.parser.plyInmantaLex
from inmanta_module_factory import __version__

INDENT_PREFIX = "    "  # Four spaces

ASL_2_0_LICENSE = "ASL 2.0"
ASL_2_0_COPYRIGHT_HEADER_TMPL = '''
"""
Copyright %(copyright)s

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Contact: %(contact)s
Author: %(author)s
"""
'''.strip(
    "\n"
)

EULA_LICENSE = "Inmanta EULA"
EULA_COPYRIGHT_HEADER_TMPL = '''
"""
:copyright: %(copyright)s
:contact: %(contact)s
:license: Inmanta EULA
:author: %(author)s
"""
'''.strip(
    "\n"
)

INMANTA_RESERVED_KEYWORDS = inmanta.parser.plyInmantaLex.keyworldlist


GENERATED_FILE_MARKER = "-".join(["IMF", "GENERATED", "FILE"])
GENERATED_FILE_FOOTER = f"""
# This file has been generated using inmanta-module-factory=={__version__}
# <{GENERATED_FILE_MARKER}/>
"""
