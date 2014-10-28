#Copyright IO-Informatics 2014

import rdflib
import hashlib
import sys
from lxml import etree
from lxml import objectify
from random import randrange

"""
- Visualize RDF files with CmapTools - 
Create CXL files from RDF files - 
"""

MY_NAMESPACES={
	'dc': 'http://purl.org/dc/elements/1.1/', 
	 None: 'http://cmap.ihmc.us/xml/cmap/'}


def make_lxml_string(query_results):

	r=etree.Element('cmap', nsmap=MY_NAMESPACES)
	res_meta=etree.Element('{%s}res-meta' % MY_NAMESPACES[None])
	title=etree.Element('{%s}title' % MY_NAMESPACES['dc'])
	title.text = "SIEVE II data model"
	description = etree.Element('{%s}description' %MY_NAMESPACES['dc'])
	description.text = "CMAP version of data model"
	res_meta.append(title)
	res_meta.append(description)
	r.append(res_meta)
	#add map node
	map_node = etree.Element('{%s}map' %MY_NAMESPACES[None])
	#create concept list
	concept_list = etree.Element('{%s}concept-list' %MY_NAMESPACES[None])
	cl = []
	#creaate linking-phrase-list
	linking_phrase_list = etree.Element('{%s}linking-phrase-list' %MY_NAMESPACES[None])
	pl = []
	#create connection list
	connection_list = etree.Element('{%s}connection-list' %MY_NAMESPACES[None])
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

		conn = etree.Element('{%s}connection' %MY_NAMESPACES[None])
		conn.set('id',str(randrange(100000)))
		conn.set('from-id', sub_md5)
		conn.set('to-id', pred_md5)
		conn2 = etree.Element('{%s}connection' %MY_NAMESPACES[None])
		conn2.set('from-id', pred_md5)
		conn2.set('to-id', obj_md5)
		connection_list.append(conn)
		connection_list.append(conn2)

	for l in cl:
		concept = etree.Element('{%s}concept' %MY_NAMESPACES[None], id=str(l[1]), label=str(l[0]))
		concept_list.append(concept)

	for p in pl:
		lp = etree.Element('{%s}linking-phrase' %MY_NAMESPACES[None], id=str(p[1]), label=str(p[0]))
		linking_phrase_list.append(lp)

	map_node.append(concept_list)
	map_node.append(linking_phrase_list)
	map_node.append(connection_list)
	r.append(map_node)
	s = etree.tostring(r, pretty_print=True)
	return s


def main():
	#path to local rdf file that you wish to convert to cxl
	input_rdf_file = "input.nt"
	#path to output cxl file to be opened with cxl
	output_cxl_file = "output.cxl"


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
	main()