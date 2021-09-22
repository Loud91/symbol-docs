import ruamel.yaml as yaml
from .base import Command


class SerializationCommand(Command):
    """Command to parse the Symbol schema YAML file into RST documentation pages
    """

    def type_description(self, element):
        if element['type'] == 'byte':
            return 'byte[%s]' % element['size']
        elif element['type'] == 'enum':
            return 'enum (%d bytes)' % element['size']
        elif element['type'] == 'struct':
            return 'struct (%d fields)' % len(element['layout'])
        else:
            return '%s_' % element['type']

    def parse_comment(self, comment):
        return '\n\n       **Note:** '.join(comment.split('\\note'))

    def print_header(self, name):
        print()
        print('.. _Serialization' + name + ':')
        print()
        print(name)
        print('*' * len(name))
        print()

    def print_type(self, element):
        self.print_header(element['name'])
        print('**Byte array**: %d byte%s (%s)' % (element['size'], 's' if element['size'] > 1 else '', element['signedness']))
        print()
        print(self.parse_comment(element['comments']))

    def print_enum(self, element):
        self.print_header(element['name'])
        print('**Enumeration**: %d byte%s (%s)' % (element['size'], 's' if element['size'] > 1 else '', element['signedness']))
        print()
        print(self.parse_comment(element['comments']))
        print()
        print('.. list-table:: Values')
        print('   :widths: 12 30 58')
        print()
        print('   * - **Value**')
        print('     - **Name**')
        print('     - **Description**')
        for v in element['values']:
            print('   * - %s' % hex(v['value']))
            print('     - ``%s``' % v['name'])
            print('     - %s' % self.parse_comment(v['comments']))

    def print_struct(self, element):
        self.print_header(element['name'])
        print('**Struct**:')
        print()
        print(self.parse_comment(element['comments']))
        print()
        print('.. list-table:: Fields')
        print('   :widths: 30 30 40')
        print()
        print('   * - **Name**')
        print('     - **Type**')
        print('     - **Description**')
        for v in element['layout']:
            disposition = v.get('disposition') or ''
            name = '*(inline)*' if disposition == 'inline' else '``%s``' % v['name']
            comment = ('**Const value** = ``%s``\n\n       ' % v['value']) if disposition == 'const' else \
                ('**Reserved value** = ``%s``\n\n       ' % v['value']) if disposition == 'reserved' else \
                ''
            comment += self.parse_comment(v['comments'])
            print('   * - %s' % name)
            print('     - %s' % self.type_description(v))
            print('     - %s' % comment)

    def execute(self):
        """Contains all the logic to execute a command."""
        with open(self.config['schema']) as f:
            try:
                schema = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                print(exc)
                return
        print('Transaction serialization')
        print('#########################')
        print()
        for e in schema:
            if e['type'] == 'byte':
                self.print_type(e)
            elif e['type'] == 'enum':
                self.print_enum(e)
            elif e['type'] == 'struct':
                self.print_struct(e)
            else:
                raise Exception ("Unknown type %s" % e['type'])
