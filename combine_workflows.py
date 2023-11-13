import argparse
import logging
import os
import xml.etree.ElementTree as ET

XML_TAGS = ['alerts', 'fieldUpdates', 'flowActions', 'fullName', 'knowledgePublishes', 'outboundMessages', 'rules', 'tasks']
logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def parse_args():
    """
        Function to parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='A script to create workflows.')
    parser.add_argument('-o', '--output', default='force-app/main/default/workflows')
    args = parser.parse_args()
    return args


def read_individual_xmls(workflow_directory):
    """
        Read each XML file
    """
    individual_xmls = {}
    for filename in os.listdir(workflow_directory):
        if filename.endswith('.xml') and not filename.endswith('.workflow-meta.xml'):
            parent_workflow_name = filename.split('.')[0]
            individual_xmls.setdefault(parent_workflow_name, [])

            tree = ET.parse(os.path.join(workflow_directory, filename))
            root = tree.getroot()
            individual_xmls[parent_workflow_name].append(root)

    return individual_xmls


def merge_xml_content(individual_xmls):
    """
        Merge XMLs for each object
    """
    merged_xmls = {}
    for parent_workflow_name, individual_roots in individual_xmls.items():
        parent_workflow_root = ET.Element('Workflow', xmlns="http://soap.sforce.com/2006/04/metadata")

        for tag in XML_TAGS:
            matching_roots = [root for root in individual_roots if root.tag == tag]
            for matching_root in matching_roots:
                child_element = ET.Element(tag)
                parent_workflow_root.append(child_element)
                child_element.extend(matching_root)

        merged_xmls[parent_workflow_name] = parent_workflow_root

    return merged_xmls


def format_and_write_xmls(merged_xmls, workflow_directory):
    """
        Create the final XMLs
    """
    xml_header = '<?xml version="1.0" encoding="UTF-8"?>\n'
    for parent_workflow_name, parent_workflow_root in merged_xmls.items():
        parent_xml_str = ET.tostring(parent_workflow_root, encoding='utf-8').decode('utf-8')
        formatted_xml = parent_xml_str.replace('><', '>\n    <').replace('<fullName>', '\t<fullName>')

        parent_workflow_filename = os.path.join(workflow_directory, f'{parent_workflow_name}.workflow-meta.xml')
        with open(parent_workflow_filename, 'wb') as file:
            file.write(xml_header.encode('utf-8'))
            file.write(formatted_xml.encode('utf-8'))


def combine_workflows(workflow_directory):
    """
        Combine the workflows for deployments
    """
    individual_xmls = read_individual_xmls(workflow_directory)
    merged_xmls = merge_xml_content(individual_xmls)
    format_and_write_xmls(merged_xmls, workflow_directory)

    logging.info('The workflows have been compiled for deployments.')


def main(output_directory):
    """
    Main function
    """
    combine_workflows(output_directory)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.output)