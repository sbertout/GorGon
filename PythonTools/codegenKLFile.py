#!/usr/bin/env python

import os, argparse
from jinja2 import Environment, FileSystemLoader


def render_template(template, context2):
    TEMPLATE_ENVIRONMENT = Environment(
        autoescape=False,
        loader=FileSystemLoader(os.path.dirname(os.path.abspath(template))),
        trim_blocks=False)
    return TEMPLATE_ENVIRONMENT.get_template(os.path.basename(template)).render(context2)


def create_index_html(args):
    dstFile = args.output
    context = {
        'extension' : args.extension,
        'components': args.components.split(',')
    }
    #
    with open(dstFile, 'w') as f:
        html = render_template(args.template, context)
        f.write(html)


def main(args):
    create_index_html(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Codegen KL file')
    parser.add_argument('-t', '--template', action="store", help='kl template filepath')
    parser.add_argument('-e', '--extension', action="store", help='extension namespace')
    parser.add_argument('-c', '--components', action="store", help='components to use, ex. Comp1,Comp2,Comp3')
    parser.add_argument('-o', '--output', action="store", help='kl filepath to generate')
    args = parser.parse_args()
    print 'Codegen-ed', args.output, 'from', args.template, 'using', args.components, 'within', args.extension
    main(args)
