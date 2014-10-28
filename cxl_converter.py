#Copyright IO-Informatics 2014

import rdflib
import hashlib
import sys
import argparse
from lxml import etree
from lxml import objectify
from random import randrange

"""
- Visualize RDF files with CmapTools - 
Create CXL files from RDF files - 
"""

parser = argparse.ArgumentParser(
	description = __doc__,
	formatter_class = argparse.RawDescriptionHelpFormatter
)
#add arguments
parser.add_argument('-i','--input_file',help='path to input RDF file', required=True)
parser.add_argument('-o', '--output_file', help='path to output CXL file', required=True)

NS_MAP={
	'dc': 'http://purl.org/dc/elements/1.1/', 
	 None: 'http://cmap.ihmc.us/xml/cmap/'}


def make_lxml_string(query_results):

	r=etree.Element('cmap', nsmap=NS_MAP)
	res_meta=etree.Element('{%s}res-meta' % NS_MAP[None])
	title=etree.Element('{%s}title' % NS_MAP['dc'])
	title.text = "SIEVE II data model"
	description = etree.Element('{%s}description' %NS_MAP['dc'])
	description.text = "CMAP version of data model"
	res_meta.append(title)
	res_meta.append(description)
	r.append(res_meta)
	#add map node
	map_node = etree.Element('{%s}map' %NS_MAP[None])
	#create concept list
	concept_list = etree.Element('{%s}concept-list' %NS_MAP[None])
	cl = []
	#creaate linking-phrase-list
	linking_phrase_list = etree.Element('{%s}linking-phrase-list' %NS_MAP[None])
	pl = []
	#create connection list
	connection_list = etree.Element('{%s}connection-list' %NS_MAP[None])
	connl = []

	for s, p, o in query_results:
		#if type(o) != rdflib.term.Literal:
		lbl = s[s.rfind('/')+1:]
		plbl = p[p.rfind('/')+1:]
		olbl = o[o.rfind('/')+1:]
		sub_md5 = hashlib.md5(str(s)).hexdigest()
		pred_md5 = hashlib.md5(str(p)).hexdigest()
		obj_md5 = hashlib.md5(str(o)).hexdigest()
		cl.append((lbl,sub_md5))
		cl.append((olbl,obj_md5))
		pl.append((plbl,pred_md5))

		conn = etree.Element('{%s}connection' %NS_MAP[None])
		conn.set('id',str(randrange(100000)))
		conn.set('from-id', sub_md5)
		conn.set('to-id', pred_md5)
		conn2 = etree.Element('{%s}connection' %NS_MAP[None])
		conn2.set('from-id', pred_md5)
		conn2.set('to-id', obj_md5)
		connection_list.append(conn)
		connection_list.append(conn2)

	for l in cl:
		concept = etree.Element('{%s}concept' %NS_MAP[None], id=str(l[1]), label=str(l[0]))
		concept_list.append(concept)

	for p in pl:
		lp = etree.Element('{%s}linking-phrase' %NS_MAP[None], id=str(p[1]), label=str(p[0]))
		linking_phrase_list.append(lp)

	map_node.append(concept_list)
	map_node.append(linking_phrase_list)
	map_node.append(connection_list)
	r.append(map_node)
	s = etree.tostring(r, pretty_print=True)
	return s


def main(argv):
	ar = parser.parse_args(argv[1:])
	#path to local rdf file that you wish to convert to cxl
	input_rdf_file = ar.input_file
	#path to output cxl file to be opened with cxl
	output_cxl_file = ar.output_file


	g = rdflib.Graph()
	g.parse(input_rdf_file)
	#currently not using Rdfs label
	query_results = g.query(
		"""
		SELECT DISTINCT ?s ?p ?o
		WHERE {
			?s ?p ?o.
		}
		"""
	)

	s = make_lxml_string(query_results)
	text_file = open(output_cxl_file, "w")
	text_file.write(s)
	text_file.close()

if __name__ == "__main__":
	main(sys.argv)