# -*- coding: utf-8 -*-
"""Module for extracting PubMed IDs from Swiss-Prot data.

This module allows extracting PMIDs from Swiss-Prot data in TXT, XML or RDF format.

"""
import argparse
import glob
import re
import sys


TXT_REGEX = re.compile(r'PubMed=[0-9]+')
XML_REGEX = re.compile(r'<dbReference type="PubMed" id="[0-9]+"/>')
RDF_REGEX = re.compile(r'<citation rdf:resource="http://purl.uniprot.org/citations/[0-9]+')


def format2regex(fmt):
    '''Return suitable regex for given file format.

    Args:
        fmt (str): Three letter file format specification (extension)

    Returns:
        regex: a compiled regular expression

    '''
    mapper = {'txt': TXT_REGEX,
              'xml': XML_REGEX,
              'rdf': RDF_REGEX,
              }
    try:
        return mapper[fmt.lower()]
    except KeyError:
        sys.exit('Wrong format: '.format(fmt))


def cleanup_match(match, fmt):
    '''Return only the wanted bits of the regex match.

    Given a regular expression match object, only the relevant bits are
    returned which depends on the file format the match was extracted from.

    Args:
        match (re.MatchObject): regular expression match object
        fmt (str): Three letter file format specification (extension)

    Returns:
        str

    '''
    fmt = fmt.lower()
    if fmt == 'txt':
        return match[7:]
    elif fmt == 'xml':
        return match[31:-3]
    elif fmt == 'rdf':
        return match[27:]


def main():
    """Main entry point for console script.

    Defines the command line parser and runs the extraction of PubMed IDs. The parser
    requires a <glob pattern>, a <file format> and an <output file>. Valid file formats are txt,
    xml and rdf. Extracted IDs are written to the <output file> which has to be specified
    as a command line parameter.

    Note:
        The <glob pattern> has to be expressed like this: `C:/some/folder/*.sp`. Adapt as necessary.
        Apparently, specifying such a glob pattern on Windows does not require quotes of any kind
        whereas on Linux it does. Files found by <glob pattern> are read as a whole which might prove
        problematic if one provided all of Swiss-Prot in one file.

    """
    parser = argparse.ArgumentParser(description='Extract PubMed IDs from UniProt data.')
    parser.add_argument('path', help='glob path and file name pattern')
    parser.add_argument('-f', '--format', default='txt', help='format of UniProt data (txt/xml/rdf)')
    parser.add_argument('-o', '--output', help='output file the extracted Ids can be saved to')
    args = parser.parse_args()
    regex = format2regex(args.format)
    pmid_set = set()
    for file in glob.glob(args.path):
        with open(file, 'r', encoding='utf8') as f:
            content = f.read()
            for match in re.findall(regex, content):
                pmid = cleanup_match(match, args.format)
                pmid_set.add(pmid)
    if args.output:
        with open(args.output, 'w', encoding='utf8') as f:
            for pmid in pmid_set:
                f.write('{}\n'.format(pmid))
        print('{0} IDs written to {1}'.format(str(len(pmid_set)), args.output))
    else:
        for pmid in pmid_set:
            print(pmid)


if __name__ == '__main__':
    main()